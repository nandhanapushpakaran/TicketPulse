from django.contrib import admin
from .models import Ticket, Comment, TicketHistory

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'text', 'created_at')

class TicketHistoryInline(admin.TabularInline):
    model = TicketHistory
    extra = 0
    readonly_fields = ('user', 'action', 'details', 'created_at')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'title', 'category', 'priority', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('ticket_number', 'title', 'description', 'created_by__email', 'assigned_to__email')
    inlines = [CommentInline, TicketHistoryInline]
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'resolved_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'author__email', 'ticket__ticket_number')

@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('details', 'user__email', 'ticket__ticket_number')
