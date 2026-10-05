import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TicketService } from '../../../core/services/ticket.service';
import { AuthService } from '../../../core/services/auth.service';
import { UserService } from '../../../core/services/user.service';
import { Ticket, Comment, TicketHistory, TicketStatus, TicketPriority } from '../../../shared/models/ticket.model';
import { User } from '../../../shared/models/user.model';
import { StatusBadgeComponent } from '../../../shared/components/status-badge/status-badge.component';
import { PriorityBadgeComponent } from '../../../shared/components/priority-badge/priority-badge.component';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, StatusBadgeComponent, PriorityBadgeComponent],
  templateUrl: './ticket-detail.component.html',
  styleUrls: ['./ticket-detail.component.scss']
})
export class TicketDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private ticketService = inject(TicketService);
  private userService = inject(UserService);
  authService = inject(AuthService);

  ticketId!: number;
  ticket = signal<Ticket | null>(null);
  comments = signal<Comment[]>([]);
  history = signal<TicketHistory[]>([]);
  agents = signal<User[]>([]);

  loading = signal<boolean>(true);
  commentSubmitting = signal<boolean>(false);
  actionLoading = signal<boolean>(false);
  newCommentText = '';
  actionMessage = signal<string | null>(null);
  actionError = signal<string | null>(null);

  // Status transitions
  readonly validTransitions: Record<string, string[]> = {
    'NEW': ['OPEN', 'IN_PROGRESS', 'CLOSED'],
    'OPEN': ['IN_PROGRESS', 'WAITING_FOR_USER', 'RESOLVED', 'CLOSED'],
    'IN_PROGRESS': ['OPEN', 'WAITING_FOR_USER', 'RESOLVED', 'CLOSED'],
    'WAITING_FOR_USER': ['IN_PROGRESS', 'RESOLVED', 'CLOSED'],
    'RESOLVED': ['CLOSED', 'OPEN'],
    'CLOSED': ['OPEN']
  };

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.ticketId = Number(idParam);
      this.loadAllData();
      if (this.authService.isSupportStaff()) {
        this.loadAgents();
      }
    }
  }

  loadAllData(): void {
    this.loading.set(true);
    this.ticketService.getTicket(this.ticketId).subscribe({
      next: (ticket) => {
        this.ticket.set(ticket);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });

    this.loadComments();
    this.loadHistory();
  }

  loadComments(): void {
    this.ticketService.getComments(this.ticketId).subscribe({
      next: (res) => this.comments.set(res)
    });
  }

  loadHistory(): void {
    this.ticketService.getHistory(this.ticketId).subscribe({
      next: (res) => this.history.set(res)
    });
  }

  loadAgents(): void {
    this.userService.getAgents().subscribe({
      next: (res) => this.agents.set(res)
    });
  }

  getAllowedStatuses(): string[] {
    const current = this.ticket()?.status;
    if (!current) return [];
    return this.validTransitions[current] || [];
  }

  onStatusChange(newStatus: string): void {
    if (!newStatus) return;
    this.actionLoading.set(true);
    this.actionError.set(null);

    this.ticketService.updateTicket(this.ticketId, { status: newStatus as TicketStatus }).subscribe({
      next: (updated) => {
        this.ticket.set(updated);
        this.actionLoading.set(false);
        this.actionMessage.set(`Status changed to ${newStatus}.`);
        this.loadHistory();
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.actionError.set(err.error?.detail || err.error?.status?.[0] || 'Status transition rejected.');
      }
    });
  }

  onPriorityChange(newPriority: string): void {
    if (!newPriority) return;
    this.actionLoading.set(true);
    this.actionError.set(null);

    this.ticketService.updateTicket(this.ticketId, { priority: newPriority as TicketPriority }).subscribe({
      next: (updated) => {
        this.ticket.set(updated);
        this.actionLoading.set(false);
        this.actionMessage.set(`Priority updated to ${newPriority}.`);
        this.loadHistory();
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.actionError.set(err.error?.detail || 'Failed to update priority.');
      }
    });
  }

  onClaimTicket(): void {
    this.actionLoading.set(true);
    this.actionError.set(null);

    this.ticketService.claimTicket(this.ticketId).subscribe({
      next: (updated) => {
        this.ticket.set(updated);
        this.actionLoading.set(false);
        this.actionMessage.set('Ticket successfully claimed.');
        this.loadHistory();
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.actionError.set(err.error?.detail || 'Failed to claim ticket.');
      }
    });
  }

  onAssignAgent(agentId: string): void {
    if (!agentId) return;
    this.actionLoading.set(true);
    this.actionError.set(null);

    this.ticketService.assignTicket(this.ticketId, Number(agentId)).subscribe({
      next: (updated) => {
        this.ticket.set(updated);
        this.actionLoading.set(false);
        this.actionMessage.set('Ticket reassigned.');
        this.loadHistory();
      },
      error: (err) => {
        this.actionLoading.set(false);
        this.actionError.set(err.error?.detail || 'Failed to assign agent.');
      }
    });
  }

  onAddComment(): void {
    const text = this.newCommentText.trim();
    if (!text) return;

    this.commentSubmitting.set(true);
    this.actionError.set(null);

    this.ticketService.addComment(this.ticketId, text).subscribe({
      next: () => {
        this.newCommentText = '';
        this.commentSubmitting.set(false);
        this.loadComments();
        this.loadHistory();
      },
      error: (err) => {
        this.commentSubmitting.set(false);
        this.actionError.set(err.error?.text?.[0] || 'Failed to post comment.');
      }
    });
  }
}
