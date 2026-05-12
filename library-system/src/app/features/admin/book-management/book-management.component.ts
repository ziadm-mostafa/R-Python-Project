import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { BookService } from '../../../core/services/book.service';
import { Book } from '../../../core/models/book.model';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-book-management',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './book-management.component.html',
  styleUrl: './book-management.component.css'
})
export class BookManagementComponent implements OnInit {
  private bookService = inject(BookService);
  private fb = inject(FormBuilder);
  private toastr = inject(ToastrService);

  books = signal<Book[]>([]);
  loading = signal(true);
  editingId = signal<number | null>(null);
  deleteTarget = signal<Book | null>(null);
  uploading = signal(false);

  bookForm = this.fb.group({
    title: ['', Validators.required],
    author: ['', Validators.required],
    isbn: ['', Validators.required],
    cover_url: [''],
    total_copies: [1, [Validators.required, Validators.min(0)]]
  });

  ngOnInit() {
    this.loadBooks();
  }

  loadBooks() {
    this.loading.set(true);
    this.bookService.getBooks().subscribe({
      next: (books) => {
        this.books.set(books);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load books', err);
        this.toastr.error('Failed to load books');
        this.loading.set(false);
      }
    });
  }

  onSubmit() {
    if (this.bookForm.valid) {
      const data = this.bookForm.value as any;
      const id = this.editingId();

      if (id) {
        this.bookService.updateBook(id, data).subscribe({
          next: () => {
            this.toastr.success('Book updated successfully');
            this.cancelEdit();
            this.loadBooks();
          },
          error: (err) => this.toastr.error(err.error?.detail || 'Update failed')
        });
      } else {
        this.bookService.createBook(data).subscribe({
          next: () => {
            this.toastr.success('Book added successfully');
            this.bookForm.reset({ total_copies: 1 });
            this.loadBooks();
          },
          error: (err) => this.toastr.error(err.error?.detail || 'Add failed')
        });
      }
    }
  }

  editBook(book: Book) {
    this.editingId.set(book.id);
    this.bookForm.patchValue({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      cover_url: book.cover_url || '',
      total_copies: book.total_copies
    });
  }

  cancelEdit() {
    this.editingId.set(null);
    this.bookForm.reset({ total_copies: 1 });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploading.set(true);
    this.bookService.uploadCover(file).subscribe({
      next: (res) => {
        this.bookForm.patchValue({ cover_url: res.url });
        this.uploading.set(false);
      },
      error: (err) => {
        this.toastr.error(err.error?.detail || 'Upload failed');
        this.uploading.set(false);
      }
    });
  }

  confirmDelete(book: Book) {
    this.deleteTarget.set(book);
  }

  cancelDelete() {
    this.deleteTarget.set(null);
  }

  deleteBook(id: number) {
    this.deleteTarget.set(null);
    this.bookService.deleteBook(id).subscribe({
      next: () => {
        this.toastr.success('Book deleted successfully');
        this.loadBooks();
      },
      error: (err) => this.toastr.error(err.error?.detail || 'Delete failed')
    });
  }
}
