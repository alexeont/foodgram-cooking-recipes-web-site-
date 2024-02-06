from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ngettext

from .models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username',
                    'first_name',
                    'last_name',
                    'recipes_count',
                    'subs_count')
    readonly_fields = ('recipes_count',
                       'subs_count')
    actions = ('ban_users',)

    @admin.action(description='Заблокировать пользователей')
    def ban_users(self, request, queryset):
        updated = queryset.update(is_active=False)
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

    @admin.display(description='Cоздано рецептов:')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Подписчиков:')
    def subs_count(self, obj):
        return obj.subs_author.count()
