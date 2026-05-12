import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BorrowService } from '../../../core/services/borrow.service';
import { BorrowRecord } from '../../../core/models/borrow.model';
import { ToastrService } from 'ngx-toastr';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-borrow-history',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './borrow-history.component.html',
  styleUrl: './borrow-history.component.css'
})
export class BorrowHistoryComponent implements OnInit {
  private borrowService = inject(BorrowService);
  private toastr = inject(ToastrService);
  history = signal<BorrowRecord[]>([]);
  loading = signal(true);

  ngOnInit() {
    this.loadHistory();
  }

  loadHistory() {
    this.loading.set(true);
    this.borrowService.getMyHistory().subscribe({
      next: (history) => {
        this.history.set(history);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Failed to load history', err);
        this.toastr.error('Failed to load borrow history');
        this.loading.set(false);
      }
    });
  }

  returnBook(record: BorrowRecord) {
    this.borrowService.returnBook(record.book_id).subscribe({
      next: () => {
        this.toastr.success('Book returned successfully');
        this.loadHistory();
      },
      error: (err) => {
        this.toastr.error(err.error?.detail || 'Return failed');
      }
    });
  }
}
