from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import EventFilter
from .models import Event, EventComment, Registration
from .permissions import IsCommentAuthor, IsOrganizer
from .serializers import (
    EventCommentSerializer,
    EventListSerializer,
    EventSerializer,
    RegistrationSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet для кото-событий.

    list:   GET /api/events/            — список событий (фильтры, пагинация)
    create: POST /api/events/           — создать событие
    read:   GET /api/events/{id}/       — детали события
    update: PUT/PATCH /api/events/{id}/ — редактировать (только организатор)
    delete: DELETE /api/events/{id}/    — удалить (только организатор)
    join:   POST /api/events/{id}/join/ — записаться
    leave:  DELETE /api/events/{id}/leave/ — отменить запись
    participants: GET /api/events/{id}/participants/ — участники
    comments: GET/POST /api/events/{id}/comments/ — комментарии
    """

    queryset = Event.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description']

    def get_permissions(self):
        """
        Дифференцированные права доступа по действиям:
        - update / partial_update / destroy — только организатор события
          (IsAuthenticated + IsOrganizer);
        - все остальные действия (list, retrieve, create, join, leave,
          participants, comments) — любой авторизованный пользователь
          (IsAuthenticated).
        Ограничение «только участники могут комментировать» проверяется
        непосредственно в обработчике comments() для POST-запросов.
        """
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [IsAuthenticated, IsOrganizer]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    # ----- Кастомное действие: записаться -----
    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, pk=None):
        event = self.get_object()

        # Проверка: событие не в прошлом
        if event.end_date < timezone.now():
            return Response(
                {'detail': 'Нельзя записаться на прошедшее событие.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверка: не записан ли уже
        existing = Registration.objects.filter(
            event=event, participant=request.user
        ).first()

        if existing and existing.status == 'active':
            return Response(
                {'detail': 'Вы уже зарегистрированы на это событие.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверка: лимит мест
        if event.max_participants is not None:
            active_count = event.registrations.filter(status='active').count()
            if active_count >= event.max_participants:
                return Response(
                    {'detail': 'Все места на событие заняты.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Если ранее отменял — реактивируем
        if existing and existing.status == 'cancelled':
            existing.status = 'active'
            existing.save()
            registration = existing
        else:
            registration = Registration.objects.create(
                event=event, participant=request.user
            )

        serializer = RegistrationSerializer(registration)
        return Response(
            {
                'detail': 'Вы успешно записаны на событие.',
                **serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    # ----- Кастомное действие: отменить запись -----
    @action(detail=True, methods=['delete'], url_path='leave')
    def leave(self, request, pk=None):
        event = self.get_object()
        registration = Registration.objects.filter(
            event=event, participant=request.user, status='active'
        ).first()

        if not registration:
            return Response(
                {'detail': 'Вы не зарегистрированы на это событие.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration.status = 'cancelled'
        registration.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ----- Список участников -----
    @action(detail=True, methods=['get'], url_path='participants')
    def participants(self, request, pk=None):
        event = self.get_object()
        registrations = event.registrations.filter(status='active')
        serializer = RegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    # ----- Комментарии -----
    @action(detail=True, methods=['get', 'post'], url_path='comments')
    def comments(self, request, pk=None):
        event = self.get_object()

        if request.method == 'GET':
            comments = event.comments.all()
            serializer = EventCommentSerializer(comments, many=True)
            return Response(serializer.data)

        # POST — только участники могут комментировать
        is_participant = Registration.objects.filter(
            event=event, participant=request.user, status='active'
        ).exists()

        if not is_participant:
            return Response(
                {'detail': 'Только участники события могут оставлять комментарии.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EventCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
