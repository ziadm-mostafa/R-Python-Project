export interface BorrowRecord {
  id: number;
  user_id: number;
  book_id: number;
  borrow_date: string;
  return_date: string | null;
  is_returned: boolean;
  book_title?: string; // Optional for UI display
}
