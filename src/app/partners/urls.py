from django.urls import path
from .views import partner_list_create, partner_detail

urlpatterns = [
    path('', partner_list_create, name='partner-list-create'),
    path('<slug:slug>/', partner_detail, name='partner-detail'),
]
