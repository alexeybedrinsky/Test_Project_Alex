from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import NetworkNode, Product


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'city', 'debt', 'supplier_link')
    list_filter = ('level', 'city')
    search_fields = ('name', 'city')
    actions = ['clear_debt']

    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse("admin:yourappname_networknode_change", args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "-"
    supplier_link.short_description = "Поставщик"

    def clear_debt(self, request, queryset):
        updated = queryset.update(debt=0)
        self.message_user(request, f'Задолженность очищена у {updated} звеньев сети.')
    clear_debt.short_description = "Очистить задолженность у выбранных звеньев"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'release_date')
    search_fields = ('name', 'model')
