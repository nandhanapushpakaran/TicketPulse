import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TicketPriority } from '../../models/ticket.model';

@Component({
  selector: 'app-priority-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="tp-badge" [ngClass]="priorityClass">
      <span *ngIf="priority === 'HIGH'" class="pulse-dot"></span>
      {{ priorityLabel }}
    </span>
  `,
  styles: [`
    .pulse-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: #ef4444;
      display: inline-block;
      margin-right: 4px;
      animation: pulse-ring 1.8s infinite;
    }
  `]
})
export class PriorityBadgeComponent {
  @Input({ required: true }) priority!: TicketPriority | string;

  get priorityClass(): string {
    switch (this.priority) {
      case 'LOW': return 'priority-low';
      case 'MEDIUM': return 'priority-medium';
      case 'HIGH': return 'priority-high';
      default: return 'priority-medium';
    }
  }

  get priorityLabel(): string {
    switch (this.priority) {
      case 'LOW': return 'Low';
      case 'MEDIUM': return 'Medium';
      case 'HIGH': return 'High';
      default: return this.priority;
    }
  }
}
