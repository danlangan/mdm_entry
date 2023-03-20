from hubspot import HubSpot
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import DataSourceSerializer
from entry_group_project.local_settings import *
# from .models import DataSource

@api_view(['GET'])
def get_hubspot_info(request):
    api_client = HubSpot(access_token=hubspot_key)
    all_contacts = api_client.crm.contacts.get_all()
    all_leads = api_client.crm.deals.get_all()
    contacts_serializer = DataSourceSerializer(all_contacts, many=True)
    leads_serializer = DataSourceSerializer(all_leads, many=True)

    custom_response = {
        "contacts" : contacts_serializer.data,
        "leads" : leads_serializer.data
    }

    return Response(custom_response)