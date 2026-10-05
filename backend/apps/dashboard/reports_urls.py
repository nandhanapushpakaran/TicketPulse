from django.urls import path
from .reports_views import ReportsAnalyticsView

urlpatterns = [
    path('', ReportsAnalyticsView.as_view(), name='reports-analytics'),
]
