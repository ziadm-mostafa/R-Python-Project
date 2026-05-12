import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BookService } from '../../../core/services/book.service';
import { Book } from '../../../core/models/book.model';
import { BookCardComponent } from '../book-card/book-card.component';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { debounceTime, distinctUntilChanged } from 'rxjs';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-book-list',
  standalone: true,
  imports: [CommonModule, BookCardComponent, ReactiveFormsModule],
  templateUrl: './book-list.component.html',
  styleUrl: './book-list.component.css'
})
export class BookListComponent implements OnInit {
  private bookService = inject(BookService);
  private toastr = inject(ToastrService);
  
  books = signal<Book[]>([]);
  loading = signal(true);
  searchQuery = signal('');
  showAvailableOnly = signal(false);

  searchControl = new FormControl('');
  availableOnlyControl = new FormControl(false);

  filteredBooks = computed(() => {
    const q = this.searchQuery().toLowerCase();
    const availableOnly = this.showAvailableOnly();

    return this.books().filter(b => {
      const matchesSearch = b.title.toLowerCase().includes(q) || 
                            b.author.toLowerCase().includes(q) || 
                            b.isbn.toLowerCase().includes(q);
      const matchesAvailability = !availableOnly || b.available_copies > 0;
      return matchesSearch && matchesAvailability;
    });
  });

  ngOnInit() {
    this.loadBooks();
    
    this.searchControl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(value => {
      this.searchQuery.set(value || '');
    });

    this.availableOnlyControl.valueChanges.subscribe(value => {
      this.showAvailableOnly.set(!!value);
    });
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
}
