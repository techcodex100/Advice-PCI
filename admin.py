from django.contrib import admin
from .models import PackingCreditAdvice

@admin.register(PackingCreditAdvice)
class PackingCreditAdviceAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'disbursement_id', 'amount', 'due_date')
    search_fields = ('customer_name', 'disbursement_id', 'customer_code')
