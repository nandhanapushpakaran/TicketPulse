from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for delivering user notification updates."""

    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)
    ticket_id = serializers.IntegerField(source='ticket.id', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'ticket',
            'ticket_id',
            'ticket_number',
            'notification_type',
            'title',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'ticket', 'ticket_id', 'ticket_number', 'notification_type', 'title', 'message', 'created_at']
