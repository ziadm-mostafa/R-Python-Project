export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  cover_url?: string;
  total_copies: number;
  available_copies: number;
}

export interface BookCreate extends Omit<Book, 'id' | 'available_copies'> {}
export interface BookUpdate extends Partial<BookCreate> {}
