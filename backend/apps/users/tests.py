from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User

class UserAuthAndPermissionTests(APITestCase):
    """Test suite covering registration, JWT authentication, and role permissions."""

    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.users_url = reverse('user-list')

        self.user = User.objects.create_user(
            email='user@test.local',
            password='TestPassword123!',
            first_name='Regular',
            last_name='User',
            role=User.Role.USER
        )

        self.admin = User.objects.create_user(
            email='admin@test.local',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN,
            is_staff=True
        )

    def test_user_registration_success(self):
        """Verify successful user registration with USER role default."""
        payload = {
            'email': 'newuser@test.local',
            'first_name': 'New',
            'last_name': 'Account',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['role'], User.Role.USER)

        created_user = User.objects.get(email='newuser@test.local')
        self.assertEqual(created_user.role, User.Role.USER)

    def test_registration_password_mismatch(self):
        """Verify registration failure on password mismatch."""
        payload = {
            'email': 'mismatch@test.local',
            'first_name': 'Mis',
            'last_name': 'Match',
            'password': 'StrongPassword123!',
            'password_confirm': 'DifferentPassword123!'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Verify valid login returns access & refresh JWT tokens and user payload."""
        payload = {
            'email': 'user@test.local',
            'password': 'TestPassword123!'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'user@test.local')

    def test_login_invalid_credentials(self):
        """Verify invalid credentials return 401 Unauthorized."""
        payload = {
            'email': 'user@test.local',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_access_admin_user_list(self):
        """Verify standard USER cannot access /api/users/ endpoint."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_and_update_user_role(self):
        """Verify ADMIN can access /api/users/ and promote a user to AGENT."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        detail_url = reverse('user-detail', kwargs={'pk': self.user.id})
        update_res = self.client.patch(detail_url, {'role': User.Role.AGENT})
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.AGENT)
