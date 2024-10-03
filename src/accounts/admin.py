from django.contrib import admin
from accounts.models import Profile, CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_staff']
    list_filter = ['is_staff', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2', 'username')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
