from django.db import models
from django.conf import settings
from django.utils import timezone

class Ticket(models.Model):
    """Core support ticket entity representing customer/internal requests."""

    class Category(models.TextChoices):
        HARDWARE = 'HARDWARE', 'Hardware'
        SOFTWARE = 'SOFTWARE', 'Software'
        NETWORK = 'NETWORK', 'Network'
        ACCOUNT = 'ACCOUNT', 'Account'
        ACCESS = 'ACCESS', 'Access'
        OTHER = 'OTHER', 'Other'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        WAITING_FOR_USER = 'WAITING_FOR_USER', 'Waiting for User'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    VALID_TRANSITIONS = {
        Status.NEW: [Status.OPEN, Status.IN_PROGRESS, Status.CLOSED],
        Status.OPEN: [Status.IN_PROGRESS, Status.WAITING_FOR_USER, Status.RESOLVED, Status.CLOSED],
        Status.IN_PROGRESS: [Status.OPEN, Status.WAITING_FOR_USER, Status.RESOLVED, Status.CLOSED],
        Status.WAITING_FOR_USER: [Status.IN_PROGRESS, Status.RESOLVED, Status.CLOSED],
        Status.RESOLVED: [Status.CLOSED, Status.OPEN],
        Status.CLOSED: [Status.OPEN],
    }

    ticket_number = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.ticket_number and is_new:
            super().save(*args, **kwargs)
            self.ticket_number = f"TIC-{1000 + self.pk}"
            kwargs['force_insert'] = False
            return super().save(*args, **kwargs)

        # Automatically update resolved_at timestamp
        if self.status in [self.Status.RESOLVED, self.Status.CLOSED] and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status not in [self.Status.RESOLVED, self.Status.CLOSED]:
            self.resolved_at = None

        return super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        if self.status == new_status:
            return True
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def __str__(self):
        return f"[{self.ticket_number or 'UNSAVED'}] {self.title}"


class Comment(models.Model):
    """Chronological discussion comment attached to a ticket."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.ticket.ticket_number}"


class TicketHistory(models.Model):
    """Audit trail record tracking changes across ticket lifecycle."""

    class Action(models.TextChoices):
        CREATED = 'CREATED', 'Ticket Created'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Status Changed'
        PRIORITY_CHANGED = 'PRIORITY_CHANGED', 'Priority Changed'
        ASSIGNED = 'ASSIGNED', 'Ticket Assigned'
        COMMENT_ADDED = 'COMMENT_ADDED', 'Comment Added'
        RESOLVED = 'RESOLVED', 'Ticket Resolved'
        CLOSED = 'CLOSED', 'Ticket Closed'
        UPDATED = 'UPDATED', 'Ticket Details Updated'

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='history'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_actions'
    )
    action = models.CharField(
        max_length=30,
        choices=Action.choices,
        default=Action.UPDATED
    )
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Ticket histories'

    def __str__(self):
        return f"{self.action} on {self.ticket.ticket_number} at {self.created_at}"
