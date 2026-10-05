import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { TicketService } from '../../../core/services/ticket.service';

@Component({
  selector: 'app-ticket-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './ticket-create.component.html',
  styleUrls: ['./ticket-create.component.scss']
})
export class TicketCreateComponent {
  private fb = inject(FormBuilder);
  private ticketService = inject(TicketService);
  private router = inject(Router);

  ticketForm: FormGroup = this.fb.group({
    title: ['', [Validators.required, Validators.minLength(5)]],
    description: ['', [Validators.required, Validators.minLength(10)]],
    category: ['SOFTWARE', [Validators.required]],
    priority: ['MEDIUM', [Validators.required]]
  });

  loading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  readonly categories = [
    { value: 'HARDWARE', label: 'Hardware (Laptops, Peripherals, Screens)' },
    { value: 'SOFTWARE', label: 'Software (OS, SaaS Tools, IDEs)' },
    { value: 'NETWORK', label: 'Network (VPN, Wi-Fi, DNS, Gateways)' },
    { value: 'ACCOUNT', label: 'Account (SSO, Passwords, MFA)' },
    { value: 'ACCESS', label: 'Access (Database, Repository, Cloud IAM)' },
    { value: 'OTHER', label: 'Other Facilities & Inquiries' }
  ];

  readonly priorities = [
    { value: 'LOW', label: 'Low - Standard inquiry or minor visual issue' },
    { value: 'MEDIUM', label: 'Medium - Impacting regular work routine' },
    { value: 'HIGH', label: 'High - Critical blocking outage or security event' }
  ];

  onSubmit(): void {
    if (this.ticketForm.invalid) {
      this.ticketForm.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    this.ticketService.createTicket(this.ticketForm.value).subscribe({
      next: (ticket) => {
        this.loading.set(false);
        this.router.navigate(['/tickets', ticket.id]);
      },
      error: (err) => {
        this.loading.set(false);
        if (err.error?.title) {
          this.errorMessage.set(err.error.title[0]);
        } else if (err.error?.description) {
          this.errorMessage.set(err.error.description[0]);
        } else if (err.error?.detail) {
          this.errorMessage.set(err.error.detail);
        } else {
          this.errorMessage.set('Failed to submit ticket. Please check input data.');
        }
      }
    });
  }
}
