import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardService } from '../../core/services/dashboard.service';
import { AuthService } from '../../core/services/auth.service';
import { DashboardData, VolumeTrendPoint } from '../../shared/models/dashboard.model';
import { StatCardComponent } from '../../shared/components/stat-card/stat-card.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { PriorityBadgeComponent } from '../../shared/components/priority-badge/priority-badge.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    StatCardComponent,
    StatusBadgeComponent,
    PriorityBadgeComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  private dashboardService = inject(DashboardService);
  authService = inject(AuthService);

  dashboardData = signal<DashboardData | null>(null);
  loading = signal<boolean>(true);
  error = signal<string | null>(null);

  // Time-based greeting
  greeting = computed(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  });

  // Calculate volume chart max for proper SVG bar scaling
  maxVolume = computed(() => {
    const data = this.dashboardData();
    if (!data || !data.volume_trend || data.volume_trend.length === 0) return 1;
    const max = Math.max(...data.volume_trend.map((p: VolumeTrendPoint) => p.count));
    return max > 0 ? max : 5;
  });

  ngOnInit(): void {
    this.fetchDashboardData();
  }

  fetchDashboardData(): void {
    this.loading.set(true);
    this.error.set(null);

    this.dashboardService.getDashboardData().subscribe({
      next: (data: DashboardData) => {
        this.dashboardData.set(data);
        this.loading.set(false);
      },
      error: (_err: any) => {
        this.error.set('Failed to load dashboard operational metrics.');
        this.loading.set(false);
      }
    });
  }

  getPercentage(count: number, total: number): number {
    if (!total || total === 0) return 0;
    return Math.round((count / total) * 100);
  }

  getHealthColor(score: number): string {
    if (score >= 80) return 'text-success';
    if (score >= 50) return 'text-warning';
    return 'text-danger';
  }
}
