import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An error occurred';

      if (error.error instanceof ErrorEvent) {
        // Client-side error
        errorMessage = `Client Error: ${error.error.message}`;
        console.error('Client-side error:', error.error.message);
      } else {
        // Server-side error
        console.error(
          `Server Error - Status: ${error.status}\n` +
          `Message: ${error.message}\n` +
          `Error: ${error.error?.message || error.statusText}`
        );

        switch (error.status) {
          case 400:
            errorMessage = `Bad Request: ${error.error?.message || 'Invalid request parameters'}`;
            break;
          case 401:
            errorMessage = 'Unauthorized: Please log in to continue';
            break;
          case 403:
            errorMessage = 'Forbidden: You do not have permission to access this resource';
            break;
          case 404:
            errorMessage = `Not Found: ${error.error?.message || 'The requested resource was not found'}`;
            break;
          case 409:
            errorMessage = `Conflict: ${error.error?.message || 'A conflict occurred'}`;
            break;
          case 422:
            errorMessage = `Validation Error: ${error.error?.message || 'Invalid data provided'}`;
            break;
          case 500:
            errorMessage = 'Internal Server Error: Please try again later';
            break;
          case 503:
            errorMessage = 'Service Unavailable: The server is temporarily unavailable';
            break;
          default:
            errorMessage = `Server Error: ${error.error?.message || error.statusText}`;
        }
      }

      // Return a user-friendly error
      return throwError(() => ({
        message: errorMessage,
        status: error.status,
        error: error.error,
        timestamp: new Date().toISOString()
      }));
    })
  );
};
