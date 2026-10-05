from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from apps.tickets.models import Ticket
from apps.users.models import User

class ReportsAnalyticsView(APIView):
    """
    Endpoint providing comprehensive reports and analytics.
    Allows filtering by date range, status, priority, and category.
    Calculates resolution rates, average resolution time, and multi-dimensional breakdowns.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        params = request.query_params

        # Scope by role
        if user.role == User.Role.USER:
            qs = Ticket.objects.filter(created_by=user)
        else:
            qs = Ticket.objects.all()

        # Date filtering
        date_from = params.get('date_from')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        # Status filtering
        status_param = params.get('status')
        if status_param:
            statuses = [s.strip().upper() for s in status_param.split(',') if s.strip()]
            qs = qs.filter(status__in=statuses)

        # Priority filtering
        priority_param = params.get('priority')
        if priority_param:
            priorities = [p.strip().upper() for p in priority_param.split(',') if p.strip()]
            qs = qs.filter(priority__in=priorities)

        # Category filtering
        category_param = params.get('category')
        if category_param:
            categories = [c.strip().upper() for c in category_param.split(',') if c.strip()]
            qs = qs.filter(category__in=categories)

        total_tickets = qs.count()

        resolved_count = qs.filter(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]).count()
        open_count = total_tickets - resolved_count
        resolution_rate = round((resolved_count / total_tickets * 100), 1) if total_tickets > 0 else 0.0

        # Average resolution duration in hours for resolved tickets
        resolved_tickets = qs.filter(
            resolved_at__isnull=False,
            status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
        )
        avg_resolution_hours = 0.0
        if resolved_tickets.exists():
            duration_expr = ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=fields.DurationField()
            )
            durations = resolved_tickets.annotate(duration=duration_expr).values_list('duration', flat=True)
            total_seconds = sum([d.total_seconds() for d in durations if d is not None])
            if len(durations) > 0:
                avg_resolution_hours = round((total_seconds / len(durations)) / 3600, 1)

        # Priority breakdown
        priority_data = {choice[0]: 0 for choice in Ticket.Priority.choices}
        for item in qs.values('priority').annotate(count=Count('id')):
            priority_data[item['priority']] = item['count']

        # Category breakdown
        category_data = {choice[0]: 0 for choice in Ticket.Category.choices}
        for item in qs.values('category').annotate(count=Count('id')):
            category_data[item['category']] = item['count']

        # Status breakdown
        status_data = {choice[0]: 0 for choice in Ticket.Status.choices}
        for item in qs.values('status').annotate(count=Count('id')):
            status_data[item['status']] = item['count']

        # Daily trend
        trend_query = qs.values('created_at__date').annotate(count=Count('id')).order_by('created_at__date')
        ticket_trend = [{'date': item['created_at__date'].isoformat(), 'count': item['count']} for item in trend_query]

        return Response({
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'status': status_param,
                'priority': priority_param,
                'category': category_param,
            },
            'summary': {
                'total_tickets': total_tickets,
                'open_tickets': open_count,
                'resolved_tickets': resolved_count,
                'resolution_rate': resolution_rate,
                'avg_resolution_hours': avg_resolution_hours,
            },
            'breakdowns': {
                'priority': priority_data,
                'category': category_data,
                'status': status_data,
            },
            'trend': ticket_trend,
        })
