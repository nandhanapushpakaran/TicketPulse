export type NotificationType =
  | 'TICKET_ASSIGNED'
  | 'STATUS_CHANGED'
  | 'TICKET_RESOLVED'
  | 'NEW_COMMENT'
  | 'HIGH_PRIORITY_CREATED';

export interface Notification {
  id: number;
  ticket: number | null;
  ticket_id: number | null;
  ticket_number: string | null;
  notification_type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}
