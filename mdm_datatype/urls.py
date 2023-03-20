from django.urls import path
from . import views

urlpatterns = [
    path('hubspot/', views.get_hubspot_info),
    path('axcelerate/', views.get_axcelerate_info),
    path('xero/', views.get_xero_info),
    path('eway/', views.get_eway_info)
]