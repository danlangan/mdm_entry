from rest_framework import serializers
from .models import DataEntry

class DataEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DataEntry
        fields = ['id', 'data_source', 'data_description', 'invoice', 'discounts', 'refunds', 'payment_status', 'payment_transactions', 'leads', 'contacts', 'bank_reconciliation_status']
        depth = 1
    data_source_id = serializers.IntegerField(write_only=True)