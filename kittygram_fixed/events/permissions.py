from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizer(BasePermission):
    """
    Разрешает редактирование/удаление только организатору события.
    Чтение доступно всем авторизованным.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.organizer == request.user


class IsCommentAuthor(BasePermission):
    """Удалять комментарий может только его автор."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
