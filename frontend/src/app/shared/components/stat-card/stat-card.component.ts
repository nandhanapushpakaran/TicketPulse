import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="tp-card stat-card" [ngClass]="variant">
      <div class="stat-header">
        <span class="stat-title">{{ title }}</span>
        <div class="stat-icon-wrapper" [ngClass]="variant">
          <ng-content select="[slot=icon]"></ng-content>
        </div>
      </div>
      <div class="stat-main">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-trend" *ngIf="trend">
          <span class="trend-badge" [class.positive]="trendPositive" [class.negative]="!trendPositive">
            {{ trend }}
          </span>
          <span class="trend-label" *ngIf="trendLabel">{{ trendLabel }}</span>
        </div>
      </div>
      <div class="stat-footer" *ngIf="subtitle">
        <span class="stat-subtitle">{{ subtitle }}</span>
      </div>
    </div>
  `,
  styles: [`
    .stat-card {
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 140px;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
      }

      &.primary::before { background-color: var(--primary); }
      &.info::before { background-color: var(--pulse-accent); }
      &.warning::before { background-color: var(--warning); }
      &.success::before { background-color: var(--success); }
      &.danger::before { background-color: var(--danger); }
    }

    .stat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.75rem;

      .stat-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .stat-icon-wrapper {
        width: 36px;
        height: 36px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;

        &.primary { background-color: #eef2ff; color: #4f46e5; }
        &.info { background-color: #ecfeff; color: #0891b2; }
        &.warning { background-color: #fffbeb; color: #d97706; }
        &.success { background-color: #ecfdf5; color: #059669; }
        &.danger { background-color: #fef2f2; color: #dc2626; }
      }
    }

    .stat-main {
      display: flex;
      align-items: baseline;
      gap: 0.75rem;
      margin-bottom: 0.5rem;

      .stat-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text-main);
        letter-spacing: -0.03em;
        line-height: 1;
      }

      .stat-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 0.75rem;

        .trend-badge {
          font-weight: 700;
          padding: 1px 6px;
          border-radius: var(--radius-sm);
          &.positive { background-color: #ecfdf5; color: #059669; }
          &.negative { background-color: #fef2f2; color: #dc2626; }
        }

        .trend-label {
          color: var(--text-muted);
        }
      }
    }

    .stat-footer {
      .stat-subtitle {
        font-size: 0.775rem;
        color: var(--text-muted);
      }
    }
  `]
})
export class StatCardComponent {
  @Input({ required: true }) title!: string;
  @Input({ required: true }) value!: number | string;
  @Input() subtitle?: string;
  @Input() trend?: string;
  @Input() trendPositive: boolean = true;
  @Input() trendLabel?: string;
  @Input() variant: 'primary' | 'info' | 'warning' | 'success' | 'danger' = 'primary';
}
