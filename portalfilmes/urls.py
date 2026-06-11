
from django.urls import path

from portalfilmes import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard.html',views.dashboard,name='dashboard'),
    path('filmes.html', views.filmes, name='filmes')
]