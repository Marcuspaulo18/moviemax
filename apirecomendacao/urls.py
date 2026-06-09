from django.urls import path
from .views import ListaFilmes, Clusterfilmes

urlpatterns = [
    path('filmes/', ListaFilmes.as_view(), name='listafilmes'),
    path('dados/', Clusterfilmes.as_view(), name='clusterfilmes'),
]