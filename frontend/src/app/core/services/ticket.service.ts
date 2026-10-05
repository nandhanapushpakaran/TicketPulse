import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Ticket,
  TicketCreatePayload,
  TicketUpdatePayload,
  Comment,
  TicketHistory,
  PaginatedResponse,
} from '../../shared/models/ticket.model';

export interface TicketFilterParams {
  search?: string;
  status?: string;
  priority?: string;
  category?: string;
  assigned_to?: string;
  my_tickets?: boolean;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

@Injectable({
  providedIn: 'root'
})
export class TicketService {
  private apiUrl = `${environment.apiUrl}/tickets`;

  constructor(private http: HttpClient) {}

  getTickets(filters?: TicketFilterParams): Observable<PaginatedResponse<Ticket>> {
    let params = new HttpParams();
    if (filters) {
      if (filters.search) params = params.set('search', filters.search);
      if (filters.status) params = params.set('status', filters.status);
      if (filters.priority) params = params.set('priority', filters.priority);
      if (filters.category) params = params.set('category', filters.category);
      if (filters.assigned_to) params = params.set('assigned_to', filters.assigned_to);
      if (filters.my_tickets !== undefined) params = params.set('my_tickets', filters.my_tickets.toString());
      if (filters.date_from) params = params.set('date_from', filters.date_from);
      if (filters.date_to) params = params.set('date_to', filters.date_to);
      if (filters.page) params = params.set('page', filters.page.toString());
      if (filters.page_size) params = params.set('page_size', filters.page_size.toString());
    }
    return this.http.get<PaginatedResponse<Ticket>>(`${this.apiUrl}/`, { params });
  }

  getTicket(id: number): Observable<Ticket> {
    return this.http.get<Ticket>(`${this.apiUrl}/${id}/`);
  }

  createTicket(payload: TicketCreatePayload): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.apiUrl}/`, payload);
  }

  updateTicket(id: number, payload: TicketUpdatePayload): Observable<Ticket> {
    return this.http.patch<Ticket>(`${this.apiUrl}/${id}/`, payload);
  }

  deleteTicket(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  claimTicket(id: number): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.apiUrl}/${id}/claim/`, {});
  }

  assignTicket(id: number, agentId: number): Observable<Ticket> {
    return this.http.post<Ticket>(`${this.apiUrl}/${id}/assign/`, { agent_id: agentId });
  }

  getComments(ticketId: number): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.apiUrl}/${ticketId}/comments/`);
  }

  addComment(ticketId: number, text: string): Observable<Comment> {
    return this.http.post<Comment>(`${this.apiUrl}/${ticketId}/comments/`, { text });
  }

  getHistory(ticketId: number): Observable<TicketHistory[]> {
    return this.http.get<TicketHistory[]>(`${this.apiUrl}/${ticketId}/history/`);
  }
}
