import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TicketService, TicketFilterParams } from '../../../core/services/ticket.service';
import { AuthService } from '../../../core/services/auth.service';
import { Ticket } from '../../../shared/models/ticket.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { PriorityBadgeComponent } from '../../../shared/components/priority-badge/priority-badge.component';

@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, StatusBadgeComponent, PriorityBadgeComponent],
  templateUrl: './ticket-list.component.html',
  styleUrls: ['./ticket-list.component.scss']
})
export class TicketListComponent implements OnInit {
  private ticketService = inject(TicketService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  authService = inject(AuthService);

  tickets = signal<Ticket[]>([]);
  totalCount = signal<number>(0);
  loading = signal<boolean>(true);
  currentPage = signal<number>(1);
  pageSize = 10;

  // Filter models
  searchTerm = '';
  selectedStatus = '';
  selectedPriority = '';
  selectedCategory = '';
  myTicketsOnly = false;

  readonly categories = ['HARDWARE', 'SOFTWARE', 'NETWORK', 'ACCOUNT', 'ACCESS', 'OTHER'];
  readonly priorities = ['LOW', 'MEDIUM', 'HIGH'];
  readonly statuses = ['NEW', 'OPEN', 'IN_PROGRESS', 'WAITING_FOR_USER', 'RESOLVED', 'CLOSED'];

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.searchTerm = params['search'] || '';
      this.selectedStatus = params['status'] || '';
      this.selectedPriority = params['priority'] || '';
      this.selectedCategory = params['category'] || '';
      this.myTicketsOnly = params['my_tickets'] === 'true';
      this.currentPage.set(Number(params['page']) || 1);
      this.loadTickets();
    });
  }

  loadTickets(): void {
    this.loading.set(true);

    const filters: TicketFilterParams = {
      search: this.searchTerm || undefined,
      status: this.selectedStatus || undefined,
      priority: this.selectedPriority || undefined,
      category: this.selectedCategory || undefined,
      my_tickets: this.myTicketsOnly || undefined,
      page: this.currentPage(),
      page_size: this.pageSize
    };

    this.ticketService.getTickets(filters).subscribe({
      next: (res) => {
        this.tickets.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      }
    });
  }

  applyFilters(): void {
    this.currentPage.set(1);
    this.updateQueryParams();
  }

  resetFilters(): void {
    this.searchTerm = '';
    this.selectedStatus = '';
    this.selectedPriority = '';
    this.selectedCategory = '';
    this.myTicketsOnly = false;
    this.currentPage.set(1);
    this.updateQueryParams();
  }

  toggleMyTickets(): void {
    this.myTicketsOnly = !this.myTicketsOnly;
    this.applyFilters();
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage.set(page);
      this.updateQueryParams();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.totalCount() / this.pageSize) || 1;
  }

  private updateQueryParams(): void {
    const qp: Record<string, string | boolean | number> = {};
    if (this.searchTerm) qp['search'] = this.searchTerm;
    if (this.selectedStatus) qp['status'] = this.selectedStatus;
    if (this.selectedPriority) qp['priority'] = this.selectedPriority;
    if (this.selectedCategory) qp['category'] = this.selectedCategory;
    if (this.myTicketsOnly) qp['my_tickets'] = true;
    if (this.currentPage() > 1) qp['page'] = this.currentPage();

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: qp,
      queryParamsHandling: 'merge'
    });
  }
}
