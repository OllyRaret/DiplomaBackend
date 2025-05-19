from django.contrib import admin

from .models import Message, Invitation


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'is_read')


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('startup', 'specialist', 'is_accepted')
