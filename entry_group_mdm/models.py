from django.db import models
from mdm_datatype.models import DataSource
# Create your models here.

class DataEntry(models.Model):
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    data_description = models.CharField(max_length=255)
    invoice = models.BooleanField(null=True)
    discounts = models.IntegerField(null=True)
    refunds = models.IntegerField(null=True)
    payment_status = models.BooleanField(null=True)
    payment_transactions = models.IntegerField(null=True)
    leads = models.CharField(max_length=255, null=True)
    contacts = models.CharField(max_length=255, null=True)
    bank_reconciliation_status = models.BooleanField(null=True)
