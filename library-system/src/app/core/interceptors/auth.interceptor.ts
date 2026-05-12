import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { jwtDecode } from 'jwt-decode';
import { ToastrService } from 'ngx-toastr';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const toastr = inject(ToastrService);
  const token = localStorage.getItem('token');

  if (token) {
    try {
      const decoded: any = jwtDecode(token);
      const isExpired = decoded.exp * 1000 < Date.now();

      if (isExpired) {
        localStorage.removeItem('token');
        router.navigate(['/login']);
        return next(req);
      }

      req = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch {
      localStorage.removeItem('token');
      router.navigate(['/login']);
      return next(req);
    }
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        localStorage.removeItem('token');
        if (router.url !== '/login') {
          router.navigate(['/login']);
        }
        toastr.error(error.error?.detail || 'Session expired, please login again');
      } else if (error.status >= 400 && error.status < 500) {
        toastr.error(error.error?.detail || 'Request failed');
      } else if (error.status >= 500) {
        toastr.error('Server error, please try again later');
      }
      return throwError(() => error);
    }),
  );
};
