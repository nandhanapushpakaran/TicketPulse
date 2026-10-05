import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TicketStatus } from '../../models/ticket.model';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="tp-badge" [ngClass]="statusClass">
      <span class="status-indicator"></span>
      {{ statusLabel }}
    </span>
  `,
  styles: [`
    .status-indicator {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: currentColor;
      display: inline-block;
      margin-right: 4px;
    }
  `]
})
export class StatusBadgeComponent {
  @Input({ required: true }) status!: TicketStatus | string;

  get statusClass(): string {
    switch (this.status) {
      case 'NEW': return 'status-new';
      case 'OPEN': return 'status-open';
      case 'IN_PROGRESS': return 'status-in-progress';
      case 'WAITING_FOR_USER': return 'status-waiting-for-user';
      case 'RESOLVED': return 'status-resolved';
      case 'CLOSED': return 'status-closed';
      default: return 'status-open';
    }
  }

  get statusLabel(): string {
    switch (this.status) {
      case 'NEW': return 'New';
      case 'OPEN': return 'Open';
      case 'IN_PROGRESS': return 'In Progress';
      case 'WAITING_FOR_USER': return 'Waiting for User';
      case 'RESOLVED': return 'Resolved';
      case 'CLOSED': return 'Closed';
      default: return this.status;
    }
  }
}
