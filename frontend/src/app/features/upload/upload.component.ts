import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, DocumentMeta } from '../../core/api.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.scss',
})
export class UploadComponent {
  @Output() uploaded = new EventEmitter<DocumentMeta[]>();

  documents: DocumentMeta[] = [];
  uploading = false;
  error: string | null = null;
  dragOver = false;

  constructor(private api: ApiService) {
    this.loadDocuments();
  }

  loadDocuments() {
    this.api.listDocuments().subscribe({
      next: (docs) => (this.documents = docs),
      error: () => (this.error = 'Failed to load documents'),
    });
  }

  onDragOver(e: DragEvent) {
    e.preventDefault();
    this.dragOver = true;
  }

  onDragLeave() {
    this.dragOver = false;
  }

  onDrop(e: DragEvent) {
    e.preventDefault();
    this.dragOver = false;
    const files = e.dataTransfer?.files;
    if (files?.length) this.uploadFiles(files);
  }

  onFileSelect(e: Event) {
    const input = e.target as HTMLInputElement;
    if (input.files?.length) this.uploadFiles(input.files);
  }

  uploadFiles(files: FileList) {
    this.error = null;
    this.uploading = true;
    let pending = files.length;

    Array.from(files).forEach((file) => {
      this.api.uploadDocument(file).subscribe({
        next: () => {
          if (--pending === 0) {
            this.uploading = false;
            this.loadDocuments();
            this.uploaded.emit(this.documents);
          }
        },
        error: (err) => {
          this.error = err.error?.detail || 'Upload failed';
          if (--pending === 0) this.uploading = false;
        },
      });
    });
  }

  deleteDoc(id: string) {
    this.api.deleteDocument(id).subscribe({
      next: () => {
        this.documents = this.documents.filter((d) => d.id !== id);
        this.uploaded.emit(this.documents);
      },
      error: () => (this.error = 'Delete failed'),
    });
  }

  formatSize(bytes?: number): string {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }
}
