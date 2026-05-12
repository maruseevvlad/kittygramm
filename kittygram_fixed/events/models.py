from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class Event(models.Model):
    """Кото-событие (встреча, выставка, прогулка)."""

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    location = models.CharField('Место проведения', max_length=300)
    start_date = models.DateTimeField('Дата начала')
    end_date = models.DateTimeField('Дата окончания')
    max_participants = models.PositiveIntegerField(
        'Макс. участников',
        null=True,
        blank=True,
        help_text='Оставьте пустым для неограниченного количества.',
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='Организатор',
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError(
                'Дата окончания должна быть позже даты начала.'
            )

    @property
    def participants_count(self):
        return self.registrations.filter(status='active').count()

    @property
    def is_past(self):
        return self.end_date < timezone.now()


class Registration(models.Model):
    """Регистрация участника на событие."""

    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('cancelled', 'Отменена'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Событие',
    )
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        verbose_name='Участник',
    )
    registered_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
    )

    class Meta:
        unique_together = ('event', 'participant')
        ordering = ['-registered_at']
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'

    def __str__(self):
        return f'{self.participant.username} → {self.event.title}'


class EventComment(models.Model):
    """Комментарий / отзыв к событию."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Событие',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_comments',
        verbose_name='Автор',
    )
    text = models.TextField('Текст', max_length=1000)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.author.username} к {self.event.title}'
