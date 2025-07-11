from django.db import models

class PackingCreditAdvice(models.Model):
    date = models.DateField(null=True, blank=True)
    customer_code = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    disbursement_id = models.CharField(max_length=100, null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    amount = models.CharField(max_length=100, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    export_order_no = models.CharField(max_length=100, null=True, blank=True)
    overseas_buyer_name = models.CharField(max_length=255, null=True, blank=True)
    transaction_account_dr = models.CharField(max_length=100, null=True, blank=True)
    transaction_amount_dr = models.CharField(max_length=100, null=True, blank=True)
    transaction_account_cr = models.CharField(max_length=100, null=True, blank=True)
    transaction_amount_cr = models.CharField(max_length=100, null=True, blank=True)
    tenure_days = models.CharField(max_length=50, null=True, blank=True)
    interest_rate = models.CharField(max_length=50, null=True, blank=True)
    bank_gstn = models.CharField(max_length=50, null=True, blank=True)
    customer_gstn = models.CharField(max_length=50, null=True, blank=True)

def __str__(self):
        return f"{self.customer_name} - {self.date}"
