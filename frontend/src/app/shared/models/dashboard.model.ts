import { Ticket } from './ticket.model';

export interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  in_progress_tickets: number;
  resolved_tickets: number;
  high_priority_tickets: number;
}

export interface VolumeTrendPoint {
  date: string;
  count: number;
}

export interface TicketHealth {
  healthy: number;
  needs_attention: number;
  critical: number;
  health_score: number;
  total_active: number;
}

export interface MyWorkSection {
  title: string;
  tickets: Ticket[];
  count: number;
}

export interface DashboardData {
  stats: DashboardStats;
  distributions: {
    status: Record<string, number>;
    priority: Record<string, number>;
    category: Record<string, number>;
  };
  volume_trend: VolumeTrendPoint[];
  ticket_health: TicketHealth;
  recent_tickets: Ticket[];
  my_work: MyWorkSection;
  user: {
    first_name: string;
    full_name: string;
    role: string;
  };
}

export interface ReportsSummary {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  resolution_rate: number;
  avg_resolution_hours: number;
}

export interface ReportsData {
  filters: {
    date_from: string | null;
    date_to: string | null;
    status: string | null;
    priority: string | null;
    category: string | null;
  };
  summary: ReportsSummary;
  breakdowns: {
    priority: Record<string, number>;
    category: Record<string, number>;
    status: Record<string, number>;
  };
  trend: VolumeTrendPoint[];
}
