from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser, Report, Task, Vote

class UserAdmin(BaseUserAdmin):
    model = CustomUser

    # Fields to display in the list view
    list_display = ('email', 'first_name', 'last_name', 'zip_code', 'city', 'gender','role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')

    # Fields displayed in the detail view for existing users
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender','zip_code', 'city', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Fields displayed in the create user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'gender','zip_code', 'city', 'role', 'is_staff', 'is_active')
        }),
    )

    # Configuration for search and ordering
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

# Register the custom user model and unregister the Group model
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Report)
admin.site.register(Task)
admin.site.register(Vote)


admin.site.unregister(Group)
