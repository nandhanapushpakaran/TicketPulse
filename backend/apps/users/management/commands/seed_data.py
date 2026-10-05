from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.users.models import User
from apps.tickets.models import Ticket, Comment, TicketHistory
from apps.notifications.models import Notification

class Command(BaseCommand):
    """Seeds realistic demonstration data for TicketPulse enterprise showcase."""

    help = 'Seeds database with realistic demo users, tickets, comments, audit logs, and notifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding TicketPulse enterprise demo data..."))

        # Default demo password (for development showcase only)
        DEMO_PASSWORD = "DemoPass123!"

        # 1. Create Demo Users
        admin, _ = User.objects.get_or_create(
            email='admin@ticketpulse.local',
            defaults={
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin.set_password(DEMO_PASSWORD)
        admin.save()

        agent_sarah, _ = User.objects.get_or_create(
            email='agent.sarah@ticketpulse.local',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'role': User.Role.AGENT,
                'is_staff': False,
            }
        )
        agent_sarah.set_password(DEMO_PASSWORD)
        agent_sarah.save()

        agent_mike, _ = User.objects.get_or_create(
            email='agent.mike@ticketpulse.local',
            defaults={
                'first_name': 'Mike',
                'last_name': 'Ross',
                'role': User.Role.AGENT,
                'is_staff': False,
            }
        )
        agent_mike.set_password(DEMO_PASSWORD)
        agent_mike.save()

        user_alex, _ = User.objects.get_or_create(
            email='user.alex@ticketpulse.local',
            defaults={
                'first_name': 'Alex',
                'last_name': 'Morgan',
                'role': User.Role.USER,
                'is_staff': False,
            }
        )
        user_alex.set_password(DEMO_PASSWORD)
        user_alex.save()

        user_emily, _ = User.objects.get_or_create(
            email='user.emily@ticketpulse.local',
            defaults={
                'first_name': 'Emily',
                'last_name': 'Chen',
                'role': User.Role.USER,
                'is_staff': False,
            }
        )
        user_emily.set_password(DEMO_PASSWORD)
        user_emily.save()

        self.stdout.write(self.style.SUCCESS("Users seeded successfully."))

        # 2. Seed Realistic Tickets
        now = timezone.now()

        tickets_data = [
            {
                'title': 'VPN Gateway disconnects during video conferencing',
                'description': 'Every time I join a Google Meet or Zoom call, the internal corporate VPN gateway disconnects after approximately 5 minutes, disrupting connectivity.',
                'category': Ticket.Category.NETWORK,
                'priority': Ticket.Priority.HIGH,
                'status': Ticket.Status.IN_PROGRESS,
                'created_by': user_alex,
                'assigned_to': agent_sarah,
                'created_offset': 3,
                'resolved': False,
                'comments': [
                    (agent_sarah, "Hello Alex, I'm checking the gateway logs for tunnel keepalive drops on your subnet.", 2),
                    (user_alex, "Thanks Sarah, it happened again just 10 minutes ago during a client demo.", 1),
                ]
            },
            {
                'title': 'Request Adobe Creative Cloud license for design sprint',
                'description': 'Our product marketing design sprint begins next Monday and I require an assigned Adobe Creative Cloud All Apps license key.',
                'category': Ticket.Category.SOFTWARE,
                'priority': Ticket.Priority.MEDIUM,
                'status': Ticket.Status.OPEN,
                'created_by': user_emily,
                'assigned_to': agent_mike,
                'created_offset': 2,
                'resolved': False,
                'comments': [
                    (agent_mike, "Procurement ticket has been initiated. Waiting on department manager sign-off.", 1),
                ]
            },
            {
                'title': 'Production PostgreSQL replica latency spiking',
                'description': 'The read-replica in us-east region is showing replication lag exceeding 120 seconds under peak query load.',
                'category': Ticket.Category.ACCESS,
                'priority': Ticket.Priority.HIGH,
                'status': Ticket.Status.NEW,
                'created_by': user_alex,
                'assigned_to': None,
                'created_offset': 1,
                'resolved': False,
                'comments': []
            },
            {
                'title': 'MacBook Pro M3 battery draining prematurely',
                'description': 'Company laptop battery health dropped below 75% capacity and device throttles heavily when unplugged.',
                'category': Ticket.Category.HARDWARE,
                'priority': Ticket.Priority.LOW,
                'status': Ticket.Status.RESOLVED,
                'created_by': user_alex,
                'assigned_to': agent_mike,
                'created_offset': 6,
                'resolved': True,
                'comments': [
                    (agent_mike, "Diagnostic completed. Scheduled replacement unit at IT service desk.", 5),
                    (user_alex, "Picked up the new MacBook today. Everything transferred properly. Thank you!", 4),
                ]
            },
            {
                'title': 'Single Sign-On (SSO) Okta login loop error',
                'description': 'When attempting to authenticate into Jira and Confluence via Okta, browser enters an infinite redirect loop with 401 error.',
                'category': Ticket.Category.ACCOUNT,
                'priority': Ticket.Priority.HIGH,
                'status': Ticket.Status.WAITING_FOR_USER,
                'created_by': user_emily,
                'assigned_to': agent_sarah,
                'created_offset': 4,
                'resolved': False,
                'comments': [
                    (agent_sarah, "Alex, could you please clear your browser cookies for the idp domain and attempt login in an incognito window?", 2),
                ]
            },
            {
                'title': 'Request ergonomic standing desk setup in Room 4B',
                'description': 'Facilities request for height-adjustable monitor arm and anti-fatigue floor mat.',
                'category': Ticket.Category.OTHER,
                'priority': Ticket.Priority.LOW,
                'status': Ticket.Status.CLOSED,
                'created_by': user_emily,
                'assigned_to': agent_mike,
                'created_offset': 10,
                'resolved': True,
                'comments': [
                    (agent_mike, "Ergonomic equipment dispatched and assembled on site.", 9),
                ]
            },
        ]

        # Clear existing tickets for fresh seed if desired
        Ticket.objects.all().delete()
        Notification.objects.all().delete()

        for t_data in tickets_data:
            created_time = now - timedelta(days=t_data['created_offset'], hours=3)
            ticket = Ticket.objects.create(
                title=t_data['title'],
                description=t_data['description'],
                category=t_data['category'],
                priority=t_data['priority'],
                status=t_data['status'],
                created_by=t_data['created_by'],
                assigned_to=t_data['assigned_to'],
                resolved_at=now - timedelta(days=t_data['created_offset'] - 2) if t_data['resolved'] else None
            )
            # Override created_at
            Ticket.objects.filter(id=ticket.id).update(created_at=created_time)
            ticket.refresh_from_db()

            # Record creation in history
            TicketHistory.objects.create(
                ticket=ticket,
                user=t_data['created_by'],
                action=TicketHistory.Action.CREATED,
                details=f"Ticket created by {t_data['created_by'].full_name}.",
                created_at=created_time
            )

            # Record assignment in history
            if t_data['assigned_to']:
                assign_time = created_time + timedelta(hours=2)
                TicketHistory.objects.create(
                    ticket=ticket,
                    user=admin,
                    action=TicketHistory.Action.ASSIGNED,
                    details=f"Ticket assigned to {t_data['assigned_to'].full_name}.",
                    created_at=assign_time
                )

            # Record status progression
            if t_data['status'] in [Ticket.Status.IN_PROGRESS, Ticket.Status.WAITING_FOR_USER, Ticket.Status.RESOLVED, Ticket.Status.CLOSED]:
                progression_time = created_time + timedelta(hours=5)
                TicketHistory.objects.create(
                    ticket=ticket,
                    user=t_data['assigned_to'] or admin,
                    action=TicketHistory.Action.STATUS_CHANGED,
                    details=f"Status updated to '{ticket.status}'.",
                    created_at=progression_time
                )

            # Comments
            for author, comment_text, comment_offset in t_data['comments']:
                c_time = now - timedelta(days=comment_offset)
                comment = Comment.objects.create(
                    ticket=ticket,
                    author=author,
                    text=comment_text,
                )
                Comment.objects.filter(id=comment.id).update(created_at=c_time)
                TicketHistory.objects.create(
                    ticket=ticket,
                    user=author,
                    action=TicketHistory.Action.COMMENT_ADDED,
                    details=f"Comment added by {author.full_name}.",
                    created_at=c_time
                )

        # 3. Create Sample Notifications
        Notification.objects.create(
            recipient=user_alex,
            ticket=Ticket.objects.filter(created_by=user_alex, status=Ticket.Status.IN_PROGRESS).first(),
            notification_type=Notification.NotificationType.STATUS_CHANGED,
            title="Ticket Status: In Progress",
            message="Sarah Jenkins is actively investigating your VPN connectivity issue.",
            is_read=False
        )
        Notification.objects.create(
            recipient=agent_sarah,
            ticket=Ticket.objects.filter(priority=Ticket.Priority.HIGH).first(),
            notification_type=Notification.NotificationType.HIGH_PRIORITY_CREATED,
            title="High Priority Incident",
            message="Production PostgreSQL replica latency spiking ticket requires immediate review.",
            is_read=False
        )
        Notification.objects.create(
            recipient=user_emily,
            ticket=Ticket.objects.filter(status=Ticket.Status.WAITING_FOR_USER).first(),
            notification_type=Notification.NotificationType.NEW_COMMENT,
            title="Update required on SSO ticket",
            message="Support agent left instructions regarding your Okta loop error.",
            is_read=True
        )

        self.stdout.write(self.style.SUCCESS("All demo tickets, comments, histories, and notifications seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("Demo credentials available: admin@ticketpulse.local / agent.sarah@ticketpulse.local / user.alex@ticketpulse.local (password: DemoPass123!)"))
