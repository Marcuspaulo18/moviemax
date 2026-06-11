from django.urls import path
from .views import ListaFilmes, Clusterfilmes , DetalheFilme

urlpatterns = [
    path('filmes/', ListaFilmes.as_view(), name='listafilmes'),
    path('dados/', Clusterfilmes.as_view(), name='clusterfilmes'),
    path('filme/', DetalheFilme.as_view(), name='detalhefilme')
]