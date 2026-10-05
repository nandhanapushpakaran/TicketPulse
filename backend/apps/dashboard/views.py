from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.tickets.models import Ticket
from apps.tickets.serializers import TicketListSerializer
from apps.users.models import User

class DashboardOverviewView(APIView):
    """
    Endpoint for 'TICKETPULSE COMMAND CENTER'.
    Provides enterprise operational analytics, stat cards, distribution charts,
    ticket health scoring, and role-tailored 'My Work' items.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # Base queryset scoped by role
        if user.role == User.Role.USER:
            base_qs = Ticket.objects.filter(created_by=user)
        else:
            base_qs = Ticket.objects.all()

        # 1. Stat Cards
        total_count = base_qs.count()
        open_count = base_qs.filter(status__in=[Ticket.Status.NEW, Ticket.Status.OPEN]).count()
        in_progress_count = base_qs.filter(status=Ticket.Status.IN_PROGRESS).count()
        resolved_count = base_qs.filter(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]).count()
        high_priority_count = base_qs.filter(
            priority=Ticket.Priority.HIGH
        ).exclude(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]).count()

        # 2. Status Distribution
        status_counts = {choice[0]: 0 for choice in Ticket.Status.choices}
        for item in base_qs.values('status').annotate(count=Count('id')):
            status_counts[item['status']] = item['count']

        # 3. Priority Breakdown
        priority_counts = {choice[0]: 0 for choice in Ticket.Priority.choices}
        for item in base_qs.values('priority').annotate(count=Count('id')):
            priority_counts[item['priority']] = item['count']

        # 4. Category Distribution
        category_counts = {choice[0]: 0 for choice in Ticket.Category.choices}
        for item in base_qs.values('category').annotate(count=Count('id')):
            category_counts[item['category']] = item['count']

        # 5. Ticket Volume (Trend over last 14 days)
        fourteen_days_ago = (now - timedelta(days=13)).date()
        daily_counts = {}
        for i in range(14):
            day_str = (fourteen_days_ago + timedelta(days=i)).isoformat()
            daily_counts[day_str] = 0

        volume_query = (
            base_qs.filter(created_at__date__gte=fourteen_days_ago)
            .values('created_at__date')
            .annotate(count=Count('id'))
            .order_by('created_at__date')
        )
        for item in volume_query:
            day_key = item['created_at__date'].isoformat()
            if day_key in daily_counts:
                daily_counts[day_key] = item['count']

        volume_trend = [{'date': d, 'count': c} for d, c in daily_counts.items()]

        # 6. Ticket Health Calculation
        # Critical: Unresolved high priority tickets OR tickets open > 7 days
        seven_days_ago = now - timedelta(days=7)
        unresolved_qs = base_qs.exclude(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED])
        unresolved_count = unresolved_qs.count()

        critical_count = unresolved_qs.filter(
            Q(priority=Ticket.Priority.HIGH) | Q(created_at__lt=seven_days_ago)
        ).distinct().count()

        # Needs Attention: Medium priority or Waiting for user (and not already critical)
        needs_attention_count = unresolved_qs.filter(
            Q(status=Ticket.Status.WAITING_FOR_USER) | Q(priority=Ticket.Priority.MEDIUM)
        ).exclude(
            Q(priority=Ticket.Priority.HIGH) | Q(created_at__lt=seven_days_ago)
        ).distinct().count()

        # Healthy: Low priority or recently opened tickets
        healthy_count = max(0, unresolved_count - critical_count - needs_attention_count)

        health_score = 100
        if unresolved_count > 0:
            health_score = max(0, round(((healthy_count + 0.5 * needs_attention_count) / unresolved_count) * 100))

        # 7. Recent Tickets (latest 5)
        recent_tickets = base_qs.select_related('created_by', 'assigned_to').order_by('-created_at')[:5]
        recent_tickets_data = TicketListSerializer(recent_tickets, many=True).data

        # 8. My Work Section
        if user.role == User.Role.USER:
            my_work_tickets = Ticket.objects.filter(created_by=user).select_related('assigned_to').order_by('-updated_at')[:5]
            my_work_title = "My Recent Tickets"
        else:
            my_work_tickets = Ticket.objects.filter(assigned_to=user).exclude(
                status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
            ).select_related('created_by').order_by('-priority', '-updated_at')[:5]
            my_work_title = "My Assigned Tickets"

        my_work_data = TicketListSerializer(my_work_tickets, many=True).data

        return Response({
            'stats': {
                'total_tickets': total_count,
                'open_tickets': open_count,
                'in_progress_tickets': in_progress_count,
                'resolved_tickets': resolved_count,
                'high_priority_tickets': high_priority_count,
            },
            'distributions': {
                'status': status_counts,
                'priority': priority_counts,
                'category': category_counts,
            },
            'volume_trend': volume_trend,
            'ticket_health': {
                'healthy': healthy_count,
                'needs_attention': needs_attention_count,
                'critical': critical_count,
                'health_score': health_score,
                'total_active': unresolved_count,
            },
            'recent_tickets': recent_tickets_data,
            'my_work': {
                'title': my_work_title,
                'tickets': my_work_data,
                'count': my_work_tickets.count(),
            },
            'user': {
                'first_name': user.first_name,
                'full_name': user.full_name,
                'role': user.role,
            }
        })
