import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Notification } from '../../shared/models/notification.model';
import { PaginatedResponse } from '../../shared/models/ticket.model';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private apiUrl = `${environment.apiUrl}/notifications`;

  readonly unreadCount = signal<number>(0);

  constructor(private http: HttpClient) {}

  getNotifications(): Observable<PaginatedResponse<Notification>> {
    return this.http.get<PaginatedResponse<Notification>>(`${this.apiUrl}/`).pipe(
      tap(() => this.fetchUnreadCount())
    );
  }

  markAsRead(id: number): Observable<Notification> {
    return this.http.patch<Notification>(`${this.apiUrl}/${id}/read/`, {}).pipe(
      tap(() => {
        const current = this.unreadCount();
        if (current > 0) this.unreadCount.set(current - 1);
      })
    );
  }

  markAllAsRead(): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.apiUrl}/mark-all-read/`, {}).pipe(
      tap(() => {
        this.unreadCount.set(0);
      })
    );
  }

  fetchUnreadCount(): void {
    this.http.get<{ unread_count: number }>(`${this.apiUrl}/unread-count/`).subscribe({
      next: (res) => this.unreadCount.set(res.unread_count),
      error: () => {} // Silent fail if unauthenticated
    });
  }
}
