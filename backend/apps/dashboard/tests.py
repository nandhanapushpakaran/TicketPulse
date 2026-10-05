from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.tickets.models import Ticket

class DashboardAndReportsTests(APITestCase):
    """Test suite covering Command Center operational analytics and reporting endpoints."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@test.local',
            password='AdminPassword123!',
            first_name='Admin',
            role=User.Role.ADMIN,
            is_staff=True
        )

        self.user = User.objects.create_user(
            email='user@test.local',
            password='UserPassword123!',
            first_name='User',
            role=User.Role.USER
        )

        # Create sample tickets across statuses and priorities
        Ticket.objects.create(
            title='High priority open ticket',
            description='Test description 1',
            category=Ticket.Category.SOFTWARE,
            priority=Ticket.Priority.HIGH,
            status=Ticket.Status.OPEN,
            created_by=self.user
        )

        Ticket.objects.create(
            title='Resolved low priority ticket',
            description='Test description 2',
            category=Ticket.Category.HARDWARE,
            priority=Ticket.Priority.LOW,
            status=Ticket.Status.RESOLVED,
            created_by=self.user
        )

        self.dashboard_url = '/api/dashboard/'
        self.reports_url = '/api/reports/'

    def test_dashboard_command_center_analytics(self):
        """Verify dashboard returns real calculations for stats, distributions, and ticket health."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['stats']['total_tickets'], 2)
        self.assertEqual(data['stats']['open_tickets'], 1)
        self.assertEqual(data['stats']['resolved_tickets'], 1)
        self.assertEqual(data['stats']['high_priority_tickets'], 1)

        # Verify distributions
        self.assertIn('status', data['distributions'])
        self.assertIn('priority', data['distributions'])
        self.assertIn('category', data['distributions'])

        # Verify Ticket Health calculations
        self.assertIn('ticket_health', data)
        self.assertIn('health_score', data['ticket_health'])
        self.assertIn('critical', data['ticket_health'])
        self.assertEqual(data['ticket_health']['critical'], 1)

    def test_reports_analytics_filtering(self):
        """Verify reports endpoint calculates resolution rate and respects category filters."""
        self.client.force_authenticate(user=self.admin)

        # Unfiltered reports
        res = self.client.get(self.reports_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['summary']['total_tickets'], 2)
        self.assertEqual(res.data['summary']['resolution_rate'], 50.0)

        # Filtered by category
        res_filtered = self.client.get(f"{self.reports_url}?category=SOFTWARE")
        self.assertEqual(res_filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(res_filtered.data['summary']['total_tickets'], 1)
