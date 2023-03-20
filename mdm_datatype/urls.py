from django.urls import path
from . import views

urlpatterns = [
    path('data_source/', views.get_hubspot_info)
]