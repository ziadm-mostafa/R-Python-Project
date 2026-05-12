import { Routes } from '@angular/router';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { BookListComponent } from './features/books/book-list/book-list.component';
import { BorrowHistoryComponent } from './features/borrow/borrow-history/borrow-history.component';
import { BookManagementComponent } from './features/admin/book-management/book-management.component';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';
import { loggedInGuard } from './core/guards/logged-in.guard';

export const routes: Routes = [
  {
    path: '',
    component: MainLayoutComponent,
    children: [
      { path: '', redirectTo: 'books', pathMatch: 'full' },
      { path: 'books', component: BookListComponent },
      { 
        path: 'history', 
        component: BorrowHistoryComponent,
        canActivate: [authGuard]
      },
      { 
        path: 'admin',
        canActivate: [adminGuard],
        children: [
          { path: '', redirectTo: 'books', pathMatch: 'full' },
          { path: 'books', component: BookManagementComponent },
          { path: 'dashboard', loadComponent: () => import('./features/admin/dashboard/dashboard.component').then(c => c.DashboardComponent) }
        ]
      }
    ]
  },
  {
    path: '',
    component: AuthLayoutComponent,
    canActivate: [loggedInGuard],
    children: [
      { path: 'login', component: LoginComponent },
      { path: 'register', component: RegisterComponent }
    ]
  },
  { path: '**', redirectTo: '' }
];
