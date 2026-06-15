import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DocumentMeta {
  id: string;
  filename: string;
  file_type: 'excel' | 'pdf';
  upload_path: string;
  uploaded_at: string;
  sheet_names?: string[];
  row_count?: number;
  size_bytes?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'model';
  content: string;
  timestamp?: string;
}

export interface ChatSession {
  id: string;
  session_id: string;
  document_ids: string[];
  messages: ChatMessage[];
  created_at: string;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  role: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = 'http://localhost:8000/api/v1';

  constructor(private http: HttpClient) {}

  // Documents
  uploadDocument(file: File): Observable<{ id: string; filename: string; file_type: string }> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post<{ id: string; filename: string; file_type: string }>(
      `${this.base}/documents/upload`,
      form
    );
  }

  listDocuments(): Observable<DocumentMeta[]> {
    return this.http.get<DocumentMeta[]>(`${this.base}/documents/`);
  }

  deleteDocument(id: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.base}/documents/${id}`);
  }

  getSheets(docId: string): Observable<{ sheets: string[]; data: Record<string, any[]> }> {
    return this.http.get<{ sheets: string[]; data: Record<string, any[]> }>(
      `${this.base}/documents/${docId}/sheets`
    );
  }

  // Chat
  createSession(documentIds: string[]): Observable<{ session_id: string; id: string }> {
    return this.http.post<{ session_id: string; id: string }>(`${this.base}/chat/session`, {
      document_ids: documentIds,
    });
  }

  sendMessage(message: string, sessionId: string, documentIds: string[]): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.base}/chat/message`, {
      message,
      session_id: sessionId,
      document_ids: documentIds,
    });
  }

  getSession(sessionId: string): Observable<ChatSession> {
    return this.http.get<ChatSession>(`${this.base}/chat/session/${sessionId}`);
  }

  listSessions(): Observable<ChatSession[]> {
    return this.http.get<ChatSession[]>(`${this.base}/chat/sessions`);
  }
}
