from django.urls import path
from .views import ListaFilmes

urlpatterns = [
    path('filmes/', ListaFilmes.as_view(), name='listafilmes'),
]