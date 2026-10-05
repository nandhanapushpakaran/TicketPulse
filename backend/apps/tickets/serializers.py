from rest_framework import serializers
from .models import Ticket, Comment, TicketHistory
from apps.users.serializers import UserSerializer

class TicketListSerializer(serializers.ModelSerializer):
    """Optimized serializer for ticket listing tables and cards."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'title',
            'category',
            'priority',
            'status',
            'created_by',
            'assigned_to',
            'comments_count',
            'created_at',
            'updated_at',
            'resolved_at',
        ]
        read_only_fields = ['id', 'ticket_number', 'created_by', 'created_at', 'updated_at', 'resolved_at']


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for submitting a new ticket."""

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'title',
            'description',
            'category',
            'priority',
            'created_at',
        ]
        read_only_fields = ['id', 'ticket_number', 'created_at']

    def validate_title(self, value):
        val = value.strip()
        if len(val) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return val

    def validate_description(self, value):
        val = value.strip()
        if len(val) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return val


class TicketDetailSerializer(serializers.ModelSerializer):
    """Detailed ticket serializer with embedded nested data."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'ticket_number',
            'title',
            'description',
            'category',
            'priority',
            'status',
            'created_by',
            'assigned_to',
            'assigned_to_id',
            'created_at',
            'updated_at',
            'resolved_at',
        ]
        read_only_fields = ['id', 'ticket_number', 'created_by', 'created_at', 'updated_at', 'resolved_at']


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer handling ticket updates with workflow transition validation."""

    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            'title',
            'description',
            'category',
            'priority',
            'status',
            'assigned_to_id',
        ]

    def validate_status(self, new_status):
        instance = self.instance
        if instance and not instance.can_transition_to(new_status):
            raise serializers.ValidationError(
                f"Invalid status transition from '{instance.status}' to '{new_status}'. "
                f"Allowed transitions: {', '.join(instance.VALID_TRANSITIONS.get(instance.status, [])) or 'None'}."
            )
        return new_status


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for displaying comments with author details."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'author', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'ticket', 'author', 'created_at', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for submitting a new comment."""

    class Meta:
        model = Comment
        fields = ['text']

    def validate_text(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Comment cannot be empty.")
        return val


class TicketHistorySerializer(serializers.ModelSerializer):
    """Serializer for rendering chronological audit trail entries."""

    user = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = TicketHistory
        fields = ['id', 'ticket', 'user', 'action', 'action_display', 'details', 'created_at']
        read_only_fields = ['id', 'ticket', 'user', 'action', 'action_display', 'details', 'created_at']

