from hubspot import HubSpot
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import DataSourceSerializer
from entry_group_project.local_settings import *
import requests, json
from base64 import b64encode
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
    # Define the eWay API endpoint URLs
    base_url = "https://api.ewaypayments.com"
    token_url = f"{base_url}/oauth/token"

    # Define your eWay API credentials
    client_id = "" 
    client_secret = ""
    username = "your_username"
    password = "your_password"

    # Define the OAuth2 authentication parameters
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password",
        "username": username,
        "password": password
    }

    # Send a POST request to the token endpoint with the auth data to get the access token
    response = requests.post(token_url, data=auth_data)

    # Check the status code of the response to ensure that the request was successful
    if response.status_code == 200:
        # If the request was successful, extract the access token from the response JSON
        access_token = response.json()["access_token"]
        print("Access token:", access_token)
        
        # Define the API endpoint URL for making GET requests to the eWay API
        api_url = f"{base_url}/Transaction"

        # Define the headers with the access token and content type
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Define the query parameters for the API request
        params = {
            "TransactionType": "Purchase"
        }

        # Send a GET request to the API endpoint with the headers and params to get the transactions
        response = requests.get(api_url, headers=headers, params=params)

        # Check the status code of the response to ensure that the request was successful
        if response.status_code == 200:
            # If the request was successful, extract the transactions from the response JSON
            transactions = response.json()["Transactions"]
            print(f"Retrieved {len(transactions)} transactions:")
            for transaction in transactions:
                print(json.dumps(transaction, indent=4))
        else:
            # If the request failed, print the error message
            error_message = response.json()["Errors"][0]["Message"]
            print(f"Failed to get transactions. Error message: {error_message}")
    else:
        # If the request failed, print the error message
        error_message = response.json()["error_description"]
        print(f"Failed to authenticate. Error message: {error_message}")

    return transactions