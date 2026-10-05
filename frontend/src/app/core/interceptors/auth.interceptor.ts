import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { environment } from '../../../environments/environment';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getAccessToken();

  let modifiedReq = req;

  // Attach token if request is directed to our backend API
  if (token && req.url.startsWith(environment.apiUrl)) {
    modifiedReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(modifiedReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // If unauthorized and not already attempting login/register, clear session
      if (error.status === 401 && !req.url.includes('/auth/login/') && !req.url.includes('/auth/register/')) {
        authService.logout();
      }
      return throwError(() => error);
    })
  );
};
