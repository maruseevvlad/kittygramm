from django.contrib import admin

from .models import Event, EventComment, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'start_date', 'end_date', 'organizer', 'participants_count')
    list_filter = ('start_date', 'location')
    search_fields = ('title', 'description')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('participant', 'event', 'status', 'registered_at')
    list_filter = ('status',)


@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'event', 'created_at')
