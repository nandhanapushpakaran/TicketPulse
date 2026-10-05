import { User } from './user.model';

export type TicketCategory = 'HARDWARE' | 'SOFTWARE' | 'NETWORK' | 'ACCOUNT' | 'ACCESS' | 'OTHER';
export type TicketPriority = 'LOW' | 'MEDIUM' | 'HIGH';
export type TicketStatus = 'NEW' | 'OPEN' | 'IN_PROGRESS' | 'WAITING_FOR_USER' | 'RESOLVED' | 'CLOSED';

export interface Ticket {
  id: number;
  ticket_number: string;
  title: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
  status: TicketStatus;
  created_by: User;
  assigned_to: User | null;
  comments_count?: number;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface TicketCreatePayload {
  title: string;
  description: string;
  category: TicketCategory;
  priority: TicketPriority;
}

export interface TicketUpdatePayload {
  title?: string;
  description?: string;
  category?: TicketCategory;
  priority?: TicketPriority;
  status?: TicketStatus;
  assigned_to_id?: number | null;
}

export interface Comment {
  id: number;
  ticket: number;
  author: User;
  text: string;
  created_at: string;
  updated_at: string;
}

export interface TicketHistory {
  id: number;
  ticket: number;
  user: User | null;
  action: string;
  action_display: string;
  details: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
