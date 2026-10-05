from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.utils import timezone

from .models import Ticket, TicketHistory
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
)
from .permissions import CanAccessTicket, CanDeleteTicket
from apps.users.models import User
from apps.notifications.models import Notification


class TicketViewSet(viewsets.ModelViewSet):
    """
    Complete Ticket management ViewSet supporting role-based scoping,
    lifecycle status transitions, history logging, and notifications.
    """

    permission_classes = [permissions.IsAuthenticated, CanAccessTicket]

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), CanDeleteTicket()]
        return [permissions.IsAuthenticated(), CanAccessTicket()]

    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        elif self.action == 'retrieve':
            return TicketDetailSerializer
        elif self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Ticket.objects.none()

        # Regular users only see tickets they submitted
        if user.role == User.Role.USER:
            queryset = Ticket.objects.filter(created_by=user)
        else:
            # Agents and Administrators have enterprise-wide visibility
            queryset = Ticket.objects.all()

        queryset = queryset.select_related('created_by', 'assigned_to').prefetch_related('comments')

        # Query parameter filters
        params = self.request.query_params

        # Search across key fields
        search = params.get('search') or params.get('q')
        if search:
            search = search.strip()
            queryset = queryset.filter(
                models.Q(ticket_number__icontains=search) |
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(created_by__email__icontains=search)
            )

        # Status filter (supports multiple comma-separated statuses)
        status_param = params.get('status')
        if status_param:
            statuses = [s.strip().upper() for s in status_param.split(',') if s.strip()]
            queryset = queryset.filter(status__in=statuses)

        # Priority filter
        priority_param = params.get('priority')
        if priority_param:
            priorities = [p.strip().upper() for p in priority_param.split(',') if p.strip()]
            queryset = queryset.filter(priority__in=priorities)

        # Category filter
        category_param = params.get('category')
        if category_param:
            categories = [c.strip().upper() for c in category_param.split(',') if c.strip()]
            queryset = queryset.filter(category__in=categories)

        # Assigned to filter
        assigned_param = params.get('assigned_to')
        if assigned_param:
            if assigned_param.lower() == 'me':
                queryset = queryset.filter(assigned_to=user)
            elif assigned_param.lower() == 'unassigned':
                queryset = queryset.filter(assigned_to__isnull=True)
            elif assigned_param.isdigit():
                queryset = queryset.filter(assigned_to_id=int(assigned_param))

        # 'my_work' or 'my_tickets' shortcut
        if params.get('my_tickets', '').lower() in ('true', '1'):
            if user.role == User.Role.USER:
                queryset = queryset.filter(created_by=user)
            else:
                queryset = queryset.filter(assigned_to=user)

        # Date range filters
        date_from = params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        ticket = serializer.save(
            created_by=user,
            status=Ticket.Status.NEW
        )

        # Record ticket creation in audit trail
        TicketHistory.objects.create(
            ticket=ticket,
            user=user,
            action=TicketHistory.Action.CREATED,
            details=f"Ticket created by {user.full_name} ({user.email}). Initial priority: {ticket.priority}."
        )

        # Notify agents and admins if high priority
        if ticket.priority == Ticket.Priority.HIGH:
            staff = User.objects.filter(
                role__in=[User.Role.AGENT, User.Role.ADMIN],
                is_active=True
            ).exclude(id=user.id)
            notifications = [
                Notification(
                    recipient=agent,
                    ticket=ticket,
                    notification_type=Notification.NotificationType.HIGH_PRIORITY_CREATED,
                    title=f"High Priority Ticket: {ticket.ticket_number}",
                    message=f"New high priority ticket '{ticket.title}' submitted by {user.full_name}."
                )
                for agent in staff
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.instance
        old_status = instance.status
        old_priority = instance.priority
        old_assigned = instance.assigned_to

        # Role enforcement for regular users:
        # Regular users cannot change assigned_to or priority
        if user.role == User.Role.USER:
            new_status = serializer.validated_data.get('status', old_status)
            # Regular users can only reopen or close their resolved tickets, or update text when NEW
            if 'assigned_to_id' in serializer.validated_data:
                serializer.validated_data.pop('assigned_to_id')
            if 'priority' in serializer.validated_data:
                serializer.validated_data.pop('priority')

            if new_status != old_status:
                if old_status == Ticket.Status.RESOLVED and new_status not in [Ticket.Status.CLOSED, Ticket.Status.OPEN]:
                    raise permissions.exceptions.PermissionDenied(
                        "Users can only close or reopen a resolved ticket."
                    )
                elif old_status != Ticket.Status.RESOLVED and new_status != old_status:
                    raise permissions.exceptions.PermissionDenied(
                        "Users cannot modify the ticket status directly while under investigation."
                    )

        # Handle agent assignment if provided
        assigned_to_id = serializer.validated_data.pop('assigned_to_id', None)
        if assigned_to_id is not None:
            if assigned_to_id == 0 or assigned_to_id == '':
                serializer.validated_data['assigned_to'] = None
            else:
                try:
                    assigned_user = User.objects.get(id=assigned_to_id, role__in=[User.Role.AGENT, User.Role.ADMIN])
                    serializer.validated_data['assigned_to'] = assigned_user
                except User.DoesNotExist:
                    raise serializers.ValidationError({"assigned_to_id": "Specified agent does not exist."})

        ticket = serializer.save()

        # Audit and notify status change
        if old_status != ticket.status:
            action_type = TicketHistory.Action.STATUS_CHANGED
            if ticket.status == Ticket.Status.RESOLVED:
                action_type = TicketHistory.Action.RESOLVED
            elif ticket.status == Ticket.Status.CLOSED:
                action_type = TicketHistory.Action.CLOSED

            TicketHistory.objects.create(
                ticket=ticket,
                user=user,
                action=action_type,
                details=f"Status updated from '{old_status}' to '{ticket.status}' by {user.full_name}."
            )

            # Notify ticket creator if someone else updated status
            if ticket.created_by != user:
                Notification.objects.create(
                    recipient=ticket.created_by,
                    ticket=ticket,
                    notification_type=Notification.NotificationType.STATUS_CHANGED,
                    title=f"Ticket {ticket.ticket_number} Status Updated",
                    message=f"Your ticket '{ticket.title}' is now {ticket.get_status_display()}."
                )

        # Audit and notify priority change
        if old_priority != ticket.priority:
            TicketHistory.objects.create(
                ticket=ticket,
                user=user,
                action=TicketHistory.Action.PRIORITY_CHANGED,
                details=f"Priority updated from '{old_priority}' to '{ticket.priority}' by {user.full_name}."
            )

        # Audit and notify assignment change
        if old_assigned != ticket.assigned_to:
            new_assignee_name = ticket.assigned_to.full_name if ticket.assigned_to else "Unassigned"
            TicketHistory.objects.create(
                ticket=ticket,
                user=user,
                action=TicketHistory.Action.ASSIGNED,
                details=f"Ticket assigned to {new_assignee_name} by {user.full_name}."
            )

            if ticket.assigned_to and ticket.assigned_to != user:
                Notification.objects.create(
                    recipient=ticket.assigned_to,
                    ticket=ticket,
                    notification_type=Notification.NotificationType.TICKET_ASSIGNED,
                    title=f"Assigned to {ticket.ticket_number}",
                    message=f"You have been assigned to ticket '{ticket.title}' by {user.full_name}."
                )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def claim(self, request, pk=None):
        """Allows an Agent or Admin to self-assign a ticket."""
        ticket = self.get_object()
        user = request.user

        if user.role not in [User.Role.AGENT, User.Role.ADMIN] and not user.is_superuser:
            return Response(
                {"detail": "Only support agents and administrators can claim tickets."},
                status=status.HTTP_403_FORBIDDEN
            )

        old_assignee = ticket.assigned_to
        ticket.assigned_to = user
        if ticket.status == Ticket.Status.NEW:
            ticket.status = Ticket.Status.OPEN
        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            user=user,
            action=TicketHistory.Action.ASSIGNED,
            details=f"Ticket claimed by agent {user.full_name}."
        )

        serializer = TicketDetailSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def assign(self, request, pk=None):
        """Allows assigning a ticket to an agent."""
        ticket = self.get_object()
        user = request.user

        if user.role not in [User.Role.AGENT, User.Role.ADMIN] and not user.is_superuser:
            return Response(
                {"detail": "Only support agents and administrators can assign tickets."},
                status=status.HTTP_403_FORBIDDEN
            )

        agent_id = request.data.get('agent_id')
        if not agent_id:
            return Response({"detail": "agent_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            agent = User.objects.get(id=agent_id, role__in=[User.Role.AGENT, User.Role.ADMIN])
        except User.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)

        ticket.assigned_to = agent
        if ticket.status == Ticket.Status.NEW:
            ticket.status = Ticket.Status.OPEN
        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            user=user,
            action=TicketHistory.Action.ASSIGNED,
            details=f"Ticket assigned to {agent.full_name} by {user.full_name}."
        )

        if agent != user:
            Notification.objects.create(
                recipient=agent,
                ticket=ticket,
                notification_type=Notification.NotificationType.TICKET_ASSIGNED,
                title=f"Assigned to {ticket.ticket_number}",
                message=f"Ticket '{ticket.title}' assigned to you by {user.full_name}."
            )

        serializer = TicketDetailSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
