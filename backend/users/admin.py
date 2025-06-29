from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Customize the admin interface for CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = UserAdmin.list_filter + ('is_active',) # Keep defaults and add more if needed
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',) # Order by email by default

    # Fieldsets for the change user page in admin
    # UserAdmin.fieldsets is a tuple of tuples. We want to replace the first one.
    # Default fieldsets:
    # (None, {'fields': ('username', 'password')}),
    # (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    # (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    # (_('Important dates'), {'fields': ('last_login', 'date_joined')})

    # Re-order to put email first as it's the USERNAME_FIELD
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username')}), # username is now optional here
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for the add user page in admin
    # Default add_fieldsets:
    # (None, {
    #     'classes': ('wide',),
    #     'fields': ('username', 'password', 'password2'),
    # })
    # We need to change 'username' to 'email' as it's the primary field.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'username', 'password', 'password2'),
            # username is optional but can be set at creation
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
