export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'member';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
