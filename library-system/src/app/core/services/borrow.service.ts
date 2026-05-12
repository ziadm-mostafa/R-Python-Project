import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { BorrowRecord } from '../models/borrow.model';

@Injectable({
  providedIn: 'root'
})
export class BorrowService {
  private readonly baseUrl = `${environment.apiUrl}/borrow`;

  constructor(private http: HttpClient) {}

  borrowBook(bookId: number): Observable<BorrowRecord> {
    return this.http.post<BorrowRecord>(`${this.baseUrl}/${bookId}`, {});
  }

  returnBook(bookId: number): Observable<BorrowRecord> {
    return this.http.post<BorrowRecord>(`${this.baseUrl}/return/${bookId}`, {});
  }

  getMyHistory(): Observable<BorrowRecord[]> {
    return this.http.get<BorrowRecord[]>(`${this.baseUrl}/my-history`);
  }

  getAllRecords(): Observable<BorrowRecord[]> {
    return this.http.get<BorrowRecord[]>(`${this.baseUrl}/all`);
  }
}
