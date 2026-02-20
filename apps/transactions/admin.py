from django.contrib import admin
from .models import Transaction, Category, BudgetLimit, PatrimoineEntry


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'icon', 'color_class')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display   = ('user', 'description', 'amount', 'type', 'category', 'date', 'source')
    list_filter    = ('type', 'source', 'category')
    search_fields  = ('description', 'user__username')
    date_hierarchy = 'date'


@admin.register(BudgetLimit)
class BudgetLimitAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount')


@admin.register(PatrimoineEntry)
class PatrimoineEntryAdmin(admin.ModelAdmin):
    list_display   = ('user', 'label', 'ptype', 'category', 'valeur', 'date')
    list_filter    = ('ptype', 'category')
    search_fields  = ('label', 'user__username')
    date_hierarchy = 'date'
