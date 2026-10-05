from django.urls import path
from .views import UserManagementViewSet

user_list = UserManagementViewSet.as_view({
    'get': 'list',
})

user_detail = UserManagementViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

user_agents = UserManagementViewSet.as_view({
    'get': 'agents',
})

urlpatterns = [
    path('', user_list, name='user-list'),
    path('agents/', user_agents, name='user-agents'),
    path('<int:pk>/', user_detail, name='user-detail'),
]
