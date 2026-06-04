
from django.urls import path

from portalfilmes import views

urlpatterns = [
    path('', views.index, name='index'),
]