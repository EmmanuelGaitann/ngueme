from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PushSubscription


@admin.register(User)
class FinAIUserAdmin(UserAdmin):
    list_display  = ('username', 'get_full_name', 'email', 'city', 'plan', 'is_active')
    list_filter   = ('plan', 'is_active', 'is_staff')
    fieldsets     = UserAdmin.fieldsets + (
        ('FIN.AI', {'fields': ('phone', 'city', 'country', 'profession', 'plan', 'monthly_income_target', 'avatar')}),
    )


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_agent', 'created_at')
    list_filter  = ('created_at',)
