import django_filters

from .models import Event


class EventFilter(django_filters.FilterSet):
    """Фильтры для списка событий."""

    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains',
        label='Место (содержит)',
    )
    start_date_after = django_filters.DateTimeFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Начало от',
    )
    start_date_before = django_filters.DateTimeFilter(
        field_name='start_date',
        lookup_expr='lte',
        label='Начало до',
    )

    class Meta:
        model = Event
        fields = ['location', 'start_date_after', 'start_date_before']
