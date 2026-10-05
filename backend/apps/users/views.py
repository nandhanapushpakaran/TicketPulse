from django.db import models
from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserAdminUpdateSerializer,
)
from .permissions import IsAdminRole, IsAgentOrAdminRole


class RegisterView(generics.CreateAPIView):
    """Register a new user account. Returns user data and JWT tokens upon success."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens immediately upon registration
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['full_name'] = user.full_name

        response_data = {
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful.'
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Authenticate with email and password to receive JWT tokens and user profile."""
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Retrieve or update current authenticated user's profile."""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    User management for Administrators.
    Provides listing, filtering, detail, and role/status update capabilities.
    Also provides an 'agents' action for support staff to populate assignment dropdowns.
    """

    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserAdminUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        is_active = self.request.query_params.get('is_active')

        if role:
            queryset = queryset.filter(role=role.upper())
        if is_active is not None:
            if is_active.lower() in ('true', '1'):
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ('false', '0'):
                queryset = queryset.filter(is_active=False)
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[IsAgentOrAdminRole])
    def agents(self, request):
        """Returns all active agents and admins suitable for ticket assignment."""
        agents = User.objects.filter(
            role__in=[User.Role.AGENT, User.Role.ADMIN],
            is_active=True
        ).order_by('first_name', 'email')
        serializer = UserSerializer(agents, many=True)
        return Response(serializer.data)
