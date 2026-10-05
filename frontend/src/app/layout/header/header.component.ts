import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';
import { Notification } from '../../shared/models/notification.model';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  authService = inject(AuthService);
  notificationService = inject(NotificationService);
  router = inject(Router);

  searchQuery = '';
  showNotificationsDropdown = signal<boolean>(false);
  recentNotifications = signal<Notification[]>([]);
  loadingNotifications = signal<boolean>(false);

  ngOnInit(): void {
    if (this.authService.isAuthenticated()) {
      this.notificationService.fetchUnreadCount();
    }
  }

  onSearch(): void {
    const q = this.searchQuery.trim();
    if (q) {
      this.router.navigate(['/tickets'], { queryParams: { search: q } });
    }
  }

  toggleNotifications(): void {
    const nextState = !this.showNotificationsDropdown();
    this.showNotificationsDropdown.set(nextState);

    if (nextState) {
      this.loadingNotifications.set(true);
      this.notificationService.getNotifications().subscribe({
        next: (res) => {
          this.recentNotifications.set(res.results.slice(0, 5));
          this.loadingNotifications.set(false);
        },
        error: () => {
          this.loadingNotifications.set(false);
        }
      });
    }
  }

  markAsRead(notification: Notification, event: Event): void {
    event.stopPropagation();
    if (!notification.is_read) {
      this.notificationService.markAsRead(notification.id).subscribe(() => {
        notification.is_read = true;
      });
    }
    if (notification.ticket_id) {
      this.showNotificationsDropdown.set(false);
      this.router.navigate(['/tickets', notification.ticket_id]);
    }
  }

  markAllAsRead(): void {
    this.notificationService.markAllAsRead().subscribe(() => {
      this.recentNotifications.update((list) =>
        list.map((n) => ({ ...n, is_read: true }))
      );
    });
  }

  getRoleBadgeClass(role: string | null | undefined): string {
    switch (role) {
      case 'ADMIN': return 'role-admin';
      case 'AGENT': return 'role-agent';
      default: return 'role-user';
    }
  }
}
