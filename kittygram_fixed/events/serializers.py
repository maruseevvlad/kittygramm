from django.utils import timezone
from rest_framework import serializers

from .models import Event, EventComment, Registration


class EventSerializer(serializers.ModelSerializer):
    """Сериализатор события."""

    organizer = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    participants_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id',
            'title',
            'description',
            'location',
            'start_date',
            'end_date',
            'max_participants',
            'organizer',
            'participants_count',
            'is_registered',
            'created_at',
        )
        read_only_fields = ('organizer', 'created_at')

    def get_participants_count(self, obj):
        return obj.registrations.filter(status='active').count()

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.registrations.filter(
                participant=request.user, status='active'
            ).exists()
        return False

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                'Дата окончания должна быть позже даты начала.'
            )
        return attrs


class EventListSerializer(serializers.ModelSerializer):
    """Сокращённый сериализатор для списка событий."""

    organizer = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id',
            'title',
            'location',
            'start_date',
            'end_date',
            'max_participants',
            'organizer',
            'participants_count',
        )

    def get_participants_count(self, obj):
        return obj.registrations.filter(status='active').count()


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации."""

    participant = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Registration
        fields = ('id', 'event', 'participant', 'registered_at', 'status')
        read_only_fields = ('event', 'participant', 'registered_at', 'status')


class EventCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = EventComment
        fields = ('id', 'event', 'author', 'text', 'created_at')
        read_only_fields = ('event', 'author', 'created_at')
