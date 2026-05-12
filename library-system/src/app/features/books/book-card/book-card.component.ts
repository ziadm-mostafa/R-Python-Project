import { Component, Input, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Book } from '../../../core/models/book.model';
import { BorrowService } from '../../../core/services/borrow.service';
import { AuthService } from '../../../core/services/auth.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-book-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './book-card.component.html',
  styleUrl: './book-card.component.css'
})
export class BookCardComponent {
  @Input({ required: true }) book!: Book;
  
  private borrowService = inject(BorrowService);
  authService = inject(AuthService);
  private toastr = inject(ToastrService);
  private cdr = inject(ChangeDetectorRef);

  onImageError() {
    this.book.cover_url = undefined;
    this.cdr.detectChanges();
  }

  borrowBook() {
    this.book.available_copies--;
    this.borrowService.borrowBook(this.book.id).subscribe({
      next: () => {
        this.toastr.success(`You've successfully borrowed "${this.book.title}"`, 'Success!');
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.book.available_copies++;
        const message = err.error?.detail || 'An unexpected error occurred while borrowing.';
        this.toastr.error(message, 'Borrow Failed');
        this.cdr.detectChanges();
      }
    });
  }
}
