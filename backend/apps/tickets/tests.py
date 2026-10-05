from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.tickets.models import Ticket, Comment, TicketHistory

class TicketSystemTests(APITestCase):
    """Test suite covering ticket creation, scoping, workflow transitions, comments, and history."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.local',
            password='TestPassword123!',
            first_name='Alex',
            role=User.Role.USER
        )

        self.user2 = User.objects.create_user(
            email='user2@test.local',
            password='TestPassword123!',
            first_name='Bob',
            role=User.Role.USER
        )

        self.agent = User.objects.create_user(
            email='agent@test.local',
            password='TestPassword123!',
            first_name='Sarah',
            role=User.Role.AGENT
        )

        self.ticket1 = Ticket.objects.create(
            title='VPN connection dropped during call',
            description='The VPN client disconnects whenever audio/video streams begin.',
            category=Ticket.Category.NETWORK,
            priority=Ticket.Priority.HIGH,
            status=Ticket.Status.OPEN,
            created_by=self.user1,
            assigned_to=self.agent
        )

        self.ticket2 = Ticket.objects.create(
            title='Laptop monitor flickering',
            description='Second external display periodically goes blank.',
            category=Ticket.Category.HARDWARE,
            priority=Ticket.Priority.LOW,
            status=Ticket.Status.NEW,
            created_by=self.user2
        )

        self.tickets_url = '/api/tickets/'

    def test_create_ticket_auto_assigns_creator_and_history(self):
        """Verify ticket creation properly associates creator and records audit history."""
        self.client.force_authenticate(user=self.user1)
        payload = {
            'title': 'Cannot access Jira after SSO reset',
            'description': 'Receiving 403 Forbidden after updating password in Okta.',
            'category': Ticket.Category.ACCOUNT,
            'priority': Ticket.Priority.MEDIUM
        }
        response = self.client.post(self.tickets_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertTrue(response.data['ticket_number'].startswith('TIC-'))

        ticket_id = response.data['id']
        ticket = Ticket.objects.get(id=ticket_id)
        self.assertEqual(ticket.created_by, self.user1)
        self.assertEqual(ticket.status, Ticket.Status.NEW)

        # Verify audit history
        history_entry = TicketHistory.objects.filter(ticket=ticket, action=TicketHistory.Action.CREATED).first()
        self.assertIsNotNone(history_entry)

    def test_role_scoping_user_sees_own_only(self):
        """Verify standard user only retrieves their own tickets."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.tickets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket_ids = [t['id'] for t in response.data['results']]
        self.assertIn(self.ticket1.id, ticket_ids)
        self.assertNotIn(self.ticket2.id, ticket_ids)

    def test_role_scoping_agent_sees_all_tickets(self):
        """Verify support agents have full enterprise visibility."""
        self.client.force_authenticate(user=self.agent)
        response = self.client.get(self.tickets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket_ids = [t['id'] for t in response.data['results']]
        self.assertIn(self.ticket1.id, ticket_ids)
        self.assertIn(self.ticket2.id, ticket_ids)

    def test_agent_valid_status_transition(self):
        """Verify agent can transition OPEN -> IN_PROGRESS and history is recorded."""
        self.client.force_authenticate(user=self.agent)
        detail_url = f"/api/tickets/{self.ticket1.id}/"
        response = self.client.patch(detail_url, {'status': Ticket.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket1.refresh_from_db()
        self.assertEqual(self.ticket1.status, Ticket.Status.IN_PROGRESS)

        history = TicketHistory.objects.filter(ticket=self.ticket1, action=TicketHistory.Action.STATUS_CHANGED).first()
        self.assertIsNotNone(history)

    def test_invalid_status_transition_rejected(self):
        """Verify invalid transition (e.g. CLOSED to IN_PROGRESS directly) is rejected."""
        self.ticket1.status = Ticket.Status.CLOSED
        self.ticket1.save()

        self.client.force_authenticate(user=self.agent)
        detail_url = f"/api/tickets/{self.ticket1.id}/"
        response = self.client.patch(detail_url, {'status': Ticket.Status.IN_PROGRESS})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_and_retrieve_comments(self):
        """Verify posting a comment associates author, records audit trail, and appears in list."""
        self.client.force_authenticate(user=self.user1)
        comments_url = f"/api/tickets/{self.ticket1.id}/comments/"
        payload = {'text': 'I tested again on Wi-Fi and the issue still reproduces.'}

        response = self.client.post(comments_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], payload['text'])
        self.assertEqual(response.data['author']['email'], self.user1.email)

        # Verify comment listing
        list_response = self.client.get(comments_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        # Verify history was recorded
        history = TicketHistory.objects.filter(ticket=self.ticket1, action=TicketHistory.Action.COMMENT_ADDED).first()
        self.assertIsNotNone(history)

    def test_retrieve_ticket_history(self):
        """Verify chronological audit history endpoint returns records."""
        self.client.force_authenticate(user=self.user1)
        history_url = f"/api/tickets/{self.ticket1.id}/history/"
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
