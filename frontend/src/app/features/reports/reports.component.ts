import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DashboardService, ReportsFilterParams } from '../../core/services/dashboard.service';
import { ReportsData } from '../../shared/models/dashboard.model';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, FormsModule, StatCardComponent],
  templateUrl: './reports.component.html',
  styleUrls: ['./reports.component.scss']
})
export class ReportsComponent implements OnInit {
  private dashboardService = inject(DashboardService);

  reportsData = signal<ReportsData | null>(null);
  loading = signal<boolean>(true);

  // Filter models
  dateFrom = '';
  dateTo = '';
  selectedStatus = '';
  selectedPriority = '';
  selectedCategory = '';

  readonly categories = ['HARDWARE', 'SOFTWARE', 'NETWORK', 'ACCOUNT', 'ACCESS', 'OTHER'];
  readonly priorities = ['LOW', 'MEDIUM', 'HIGH'];
  readonly statuses = ['NEW', 'OPEN', 'IN_PROGRESS', 'WAITING_FOR_USER', 'RESOLVED', 'CLOSED'];

  ngOnInit(): void {
    this.loadReports();
  }

  loadReports(): void {
    this.loading.set(true);

    const filters: ReportsFilterParams = {
      date_from: this.dateFrom || undefined,
      date_to: this.dateTo || undefined,
      status: this.selectedStatus || undefined,
      priority: this.selectedPriority || undefined,
      category: this.selectedCategory || undefined
    };

    this.dashboardService.getReportsData(filters).subscribe({
      next: (data: ReportsData) => {
        this.reportsData.set(data);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  resetFilters(): void {
    this.dateFrom = '';
    this.dateTo = '';
    this.selectedStatus = '';
    this.selectedPriority = '';
    this.selectedCategory = '';
    this.loadReports();
  }

  getPercentage(count: number, total: number): number {
    if (!total || total === 0) return 0;
    return Math.round((count / total) * 100);
  }
}
