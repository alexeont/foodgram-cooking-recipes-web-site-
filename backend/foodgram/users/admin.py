from django.contrib import admin, messages
from django.utils.translation import ngettext

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    actions = ('ban_users',)

    @admin.action(description='Заблокировать пользователей')
    def ban_users(self, request, queryset):
        updated = queryset.update(is_active=False,
                                  is_in_black_list=True)
        self.message_user(
            request,
            ngettext(
                "%d пользователь был заблокирован",
                "Пользователей заблокировано: %d",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )
