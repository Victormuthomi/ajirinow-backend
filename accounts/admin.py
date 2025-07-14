from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FundiProfile, ClientProfile

class UserAdmin(BaseUserAdmin):
    list_display = (
        'phone_number',
        'name',
        'role',
        'is_on_trial',
        'is_subscribed',
        'is_active',
        'is_staff',
    )
    list_filter = ('role', 'is_active')
    search_fields = ('phone_number', 'name', 'id_number')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'is_on_trial', 'is_subscribed')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('name', 'id_number', 'role')}),
        ('Subscription & Trial', {
            'fields': (
                'trial_started',
                'trial_ends',
                'subscription_end',
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'id_number', 'role', 'password1', 'password2'),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(FundiProfile)
admin.site.register(ClientProfile)

