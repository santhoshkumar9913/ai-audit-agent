import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadComponent } from './features/upload/upload.component';
import { ChatComponent } from './features/chat/chat.component';
import { DocumentMeta } from './core/api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, UploadComponent, ChatComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  documents: DocumentMeta[] = [];
  activeTab: 'documents' | 'chat' = 'documents';

  onDocumentsUpdated(docs: DocumentMeta[]) {
    this.documents = [...docs];
    if (docs.length > 0) this.activeTab = 'chat';
  }

  switchTab(tab: 'documents' | 'chat') {
    this.activeTab = tab;
  }
}
