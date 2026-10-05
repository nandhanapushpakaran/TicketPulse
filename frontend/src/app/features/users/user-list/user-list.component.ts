import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService, UserFilterParams } from '../../../core/services/user.service';
import { User, UserRole } from '../../../shared/models/user.model';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss']
})
export class UserListComponent implements OnInit {
  private userService = inject(UserService);

  users = signal<User[]>([]);
  totalCount = signal<number>(0);
  loading = signal<boolean>(true);
  currentPage = signal<number>(1);
  pageSize = 10;

  // Search & Filter
  searchTerm = '';
  selectedRole = '';

  // Role Edit Modal / Inline
  selectedUser = signal<User | null>(null);
  modalRole: UserRole = 'USER';
  modalActive: boolean = true;
  modalSaving = signal<boolean>(false);
  modalMessage = signal<string | null>(null);
  modalError = signal<string | null>(null);

  readonly roles: UserRole[] = ['USER', 'AGENT', 'ADMIN'];

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading.set(true);

    const filters: UserFilterParams = {
      search: this.searchTerm || undefined,
      role: this.selectedRole || undefined,
      page: this.currentPage()
    };

    this.userService.getUsers(filters).subscribe({
      next: (res) => {
        this.users.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  applyFilters(): void {
    this.currentPage.set(1);
    this.loadUsers();
  }

  resetFilters(): void {
    this.searchTerm = '';
    this.selectedRole = '';
    this.currentPage.set(1);
    this.loadUsers();
  }

  openEditModal(user: User): void {
    this.selectedUser.set(user);
    this.modalRole = user.role;
    this.modalActive = user.is_active;
    this.modalMessage.set(null);
    this.modalError.set(null);
  }

  closeModal(): void {
    this.selectedUser.set(null);
  }

  saveUserChanges(): void {
    const user = this.selectedUser();
    if (!user) return;

    this.modalSaving.set(true);
    this.modalError.set(null);

    this.userService.updateUser(user.id, {
      role: this.modalRole,
      is_active: this.modalActive
    }).subscribe({
      next: (updated) => {
        this.modalSaving.set(false);
        this.users.update(list =>
          list.map(u => u.id === updated.id ? updated : u)
        );
        this.closeModal();
      },
      error: (err) => {
        this.modalSaving.set(false);
        this.modalError.set(err.error?.detail || err.error?.role?.[0] || 'Failed to update user.');
      }
    });
  }
}
