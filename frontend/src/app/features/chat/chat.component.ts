import { Component, Input, OnChanges, SimpleChanges, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, ChatMessage, DocumentMeta } from '../../core/api.service';

interface DisplayMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent implements OnChanges, AfterViewChecked {
  @Input() documents: DocumentMeta[] = [];
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;

  messages: DisplayMessage[] = [];
  inputText = '';
  loading = false;
  error: string | null = null;
  sessionId: string | null = null;
  private shouldScroll = false;

  constructor(private api: ApiService) {}

  ngOnChanges(changes: SimpleChanges) {
    // When documents change, reset the session
    if (changes['documents']) {
      this.sessionId = null;
      this.messages = [];
    }
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  get documentIds(): string[] {
    return this.documents.map((d) => d.id);
  }

  send() {
    const text = this.inputText.trim();
    if (!text || this.loading) return;

    this.inputText = '';
    this.error = null;
    this.loading = true;

    this.messages.push({ role: 'user', content: text, timestamp: new Date() });
    this.shouldScroll = true;

    this.api.sendMessage(text, this.sessionId || '', this.documentIds).subscribe({
      next: (res) => {
        this.sessionId = res.session_id;
        this.messages.push({ role: 'assistant', content: res.answer, timestamp: new Date() });
        this.loading = false;
        this.shouldScroll = true;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Agent error. Please try again.';
        this.loading = false;
      },
    });
  }

  onKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.send();
    }
  }

  clearChat() {
    this.messages = [];
    this.sessionId = null;
    this.error = null;
  }

  private scrollToBottom() {
    try {
      this.messagesEnd.nativeElement.scrollIntoView({ behavior: 'smooth' });
    } catch {}
  }

  formatContent(content: string): string {
    // Basic markdown-lite: code blocks and newlines
    return content
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  }
}
