import base64
from hubspot import HubSpot
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import DataSourceSerializer
from entry_group_project.local_settings import *
import requests, json
from base64 import b64encode
from django.http import JsonResponse
from django_cron import CronJobBase, Schedule
import time, datetime, schedule

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

    return JsonResponse(custom_response)

@api_view(['GET'])
def get_axcelerate_info(request):
    api_endpoint = 'https://api.axcelerate.com.au/api/v2/'
    username = 'dan.langan@valenta.io'
    password = '<insert-password-here>' # I believe that this needs to be the overall password for the admin account that I am inside of

    # set the API method and parameters for retrieving the web services token
    api_method = 'login'
    params = {'userName': username, 'password': password}

    # make the API request
    response = requests.post(api_endpoint + api_method, json=params)

    # check if the request was successful
    if response.status_code == requests.codes.ok:
        # extract the web services token from the response data
        web_services_token = response.json()['webServicesToken']
    else:
        # handle the error
        print('API request failed with status code ' + str(response.status_code))

    # set the API method and parameters for retrieving the API token
    api_method = 'tokens'
    params = {'webServicesToken': web_services_token}

    # make the API request
    response = requests.post(api_endpoint + api_method, json=params)

    # check if the request was successful
    if response.status_code == requests.codes.ok:
        # extract the API token from the response data
        api_token = response.json()['apiToken']
    else:
        # handle the error
        print('API request failed with status code ' + str(response.status_code))


    # set the API endpoint and authentication token
    api_endpoint = 'https://api.axcelerate.com.au/api/v2/'
    auth_token = f'{api_token}'

    # set the API method and parameters
    api_method = 'enrolmentfinance'
    params = {
        'enrolmentID': '<insert-enrolment-id-here>', ## this shows up in documentation but I am not sure where to grab it inside of the axcelerate account
        'invoices': True,
        'receivables': True,
        'refunds': True
    }

    # make the API request
    response = requests.post(api_endpoint + api_method, headers={'Authorization': 'Bearer ' + auth_token}, json=params)

    # check if the request was successful
    if response.status_code == requests.codes.ok:
        # extract the response data as a JSON object
        response_data = response.json()
        # extract the invoices, receivables, and refunds from the response data
        invoices = response_data.get('invoices', [])
        receivables = response_data.get('receivables', [])
        refunds = response_data.get('refunds', [])
    else:
        # handle the error
        print('API request failed with status code ' + str(response.status_code))

    return Response(invoices, receivables, refunds)

@api_view(['GET'])
def get_xero_info(request):
    api_endpoint = 'https://identity.xero.com/connect/token'
    # the next three things below am I still looking on how to identify
    client_id = '<insert-client-id-here>'
    client_secret = '<insert-client-secret-here>'
    redirect_uri = '<insert-redirect-uri-here>'
    scope = 'offline_access accounting.contacts.read accounting.transactions.read'

    # set the OAuth 2.0 parameters
    oauth2_params = {
        'grant_type': 'authorization_code',
        'code': '<insert-authorization-code-here>', ##need to find inside of documentation
        'redirect_uri': redirect_uri
    }

    # set the headers for authenticating with the Xero API
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + b64encode((client_id + ':' + client_secret).encode('utf-8')).decode('utf-8')
    }

    # make the OAuth 2.0 request to exchange the authorization code for an access token
    response = requests.post(api_endpoint, data=oauth2_params, headers=headers)

    # check if the request was successful
    if response.status_code == requests.codes.ok:
        # extract the access token from the response data
        access_token = response.json()['access_token']
        # save the access token to a file or database for future use
        with open('xero_access_token.json', 'w') as f:
            json.dump({'access_token': access_token}, f)
    else:
        # handle the error
        print('OAuth 2.0 request failed with status code ' + str(response.status_code))

    ## add the code needed to make api calls from here down 

@api_view(['GET'])
def get_eway_info(request):
   
    bpg_username = bpg_username_login
    bpg_password = bpg_password_login
    bpg_api_key = bpg_eway_key
    bpg_api_password = bpg_eway_password
    mrt_username = mrt_username_login
    mrt_password = mrt_password_login
    mrt_api_key = mrt_eway_key
    mrt_api_password = mrt_eway_password
    
    current_date = datetime.date.today()

    bpg_endpoint = "https://api.ewaypayments.com/transactions"
    mrt_endpoint = "https://api.ewaypayments.com/transactions"

    bpg_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Basic " + base64.b64encode(f"{bpg_api_key}:{bpg_api_password}".encode()).decode(),
    }
    bpg_params = {
        "UserName": bpg_username,
        "Password": bpg_password,
        "TransactionType": "Purchase,MOTO,Recurring",
        "IncludeDetail": True,
        "StartDate": str(current_date),
        "EndDate": str(current_date)
    }
    mrt_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Basic " + base64.b64encode(f"{mrt_api_key}:{mrt_api_password}".encode()).decode(),
    }
    mrt_params = {
        "UserName": mrt_username,
        "Password": mrt_password,
        "TransactionType": "Purchase,MOTO,Recurring",
        "IncludeDetail": True,
        "StartDate": str(current_date),
        "EndDate": str(current_date)
    }

    bpg_response = requests.get(bpg_endpoint, headers=bpg_headers, params=bpg_params)
    bpg_response.raise_for_status()
    bpg_transactions = json.loads(bpg_response.text)

    mrt_response = requests.get(mrt_endpoint, headers=mrt_headers, params=mrt_params)
    mrt_response.raise_for_status()
    mrt_transactions = json.loads(mrt_response.text)

    return JsonResponse({"bpg_transactions": bpg_transactions, "mrt_transactions": mrt_transactions})

def job(request):
    result = get_eway_info()
    return result

schedule.every(6).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)


