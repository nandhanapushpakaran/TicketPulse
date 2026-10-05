import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NotificationService } from '../../core/services/notification.service';
import { Notification } from '../../shared/models/notification.model';
import { PaginatedResponse } from '../../shared/models/ticket.model';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss']
})
export class NotificationsComponent implements OnInit {
  notificationService = inject(NotificationService);

  notifications = signal<Notification[]>([]);
  loading = signal<boolean>(true);

  ngOnInit(): void {
    this.loadNotifications();
  }

  loadNotifications(): void {
    this.loading.set(true);
    this.notificationService.getNotifications().subscribe({
      next: (res: PaginatedResponse<Notification>) => {
        this.notifications.set(res.results);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  markAsRead(item: Notification): void {
    if (!item.is_read) {
      this.notificationService.markAsRead(item.id).subscribe(() => {
        item.is_read = true;
      });
    }
  }

  markAllAsRead(): void {
    this.notificationService.markAllAsRead().subscribe(() => {
      this.notifications.update((list) =>
        list.map((n) => ({ ...n, is_read: true }))
      );
    });
  }
}
