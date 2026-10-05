from django.db import models
from django.conf import settings
from apps.tickets.models import Ticket

class Notification(models.Model):
    """Notification sent to user/agent/admin upon ticket events."""

    class NotificationType(models.TextChoices):
        TICKET_ASSIGNED = 'TICKET_ASSIGNED', 'Ticket Assigned'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Status Changed'
        TICKET_RESOLVED = 'TICKET_RESOLVED', 'Ticket Resolved'
        NEW_COMMENT = 'NEW_COMMENT', 'New Comment'
        HIGH_PRIORITY_CREATED = 'HIGH_PRIORITY_CREATED', 'High Priority Ticket Created'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.STATUS_CHANGED
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.email}: {self.title}"
