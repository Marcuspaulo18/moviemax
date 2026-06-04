import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
import kagglehub
import os
import ast

destino = kagglehub.dataset_download("tmdb/tmdb-movie-metadata")

diretoriocredito = os.path.join(destino, "tmdb_5000_credits.csv")
diretoriofilme = os.path.join(destino, "tmdb_5000_movies.csv")

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', 20)

dadosfilme = pd.read_csv(diretoriofilme)
dadosnota = pd.read_csv(diretoriocredito)

dadosfilme = dadosfilme.fillna({
    'budget': 0,
    'homepage': '',
    'overview': '',
    'runtime': 0.0,
    'release_date': ''
})

# Mantido o padrão tudo junto e sem acentos
dadosfilme = dadosfilme.rename(columns={
    'id': 'idefilme',
    'title': 'titulo',
    'genres': 'generos',
    'budget': 'orcamento',
    'homepage': 'homepage',
    'keywords': 'palavraschave',
    'original_language': 'idiomaoriginal',
    'original_title': 'titulooriginal',
    'overview': 'resumo',
    'popularity': 'popularidade',
    'production_companies': 'companhiasproducao',
    'production_countries': 'paisesproducao',
    'release_date': 'datalancamento',
    'revenue': 'faturamento',
    'runtime': 'tempoduracao',
    'spoken_languages': 'idiomasfalados',
    'status': 'status',
    'tagline': 'slogan',
    'vote_average': 'notamedia',
    'vote_count': 'totalvotos'
})

dadosnota = dadosnota.rename(columns={
    'movie_id': 'idefilme',
    'title': 'titulo',
    'cast': 'elenco',
    'crew': 'equipe'
})

generos = {
    'Action': 'Acao',
    'Adventure': 'Aventura',
    'Animation': 'Animacao',
    'Children': 'Infantil',
    'Comedy': 'Comedia',
    'Crime': 'Crime',
    'Documentary': 'Documentario',
    'Drama': 'Drama',
    'Fantasy': 'Fantasia',
    'Film-Noir': 'Filme-Noir',
    'Horror': 'Terror',
    'Musical': 'Musical',
    'Mystery': 'Misterio',
    'Romance': 'Romance',
    'Sci-Fi': 'Ficcao Cientifica',
    'Thriller': 'Suspense',
    'War': 'Guerra',
    'Western': 'Faroeste',
    '(no genres listed)': 'sem genero'
}

for eng, pt in generos.items():
    dadosfilme['generos'] = dadosfilme['generos'].str.replace(eng, pt, regex=False)


class ListaFilmes(APIView):
    def get(self, request):

        gettitulo = request.query_params.get('titulo', None)
        getgenero = request.query_params.get('genero', None)

        try:
            paginaatual = int(request.query_params.get('pagina', 1))
            if paginaatual < 1: paginaatual = 1
        except ValueError:
            paginaatual = 1

        dadosfiltrados = dadosfilme.copy()

        if getgenero:
            dadosfiltrados = dadosfiltrados[
                dadosfiltrados['generos'].str.contains(getgenero, case=False, na=False)
            ]
        else:
            dadosfiltrados = dadosfiltrados.copy()

        if gettitulo:
            dadosfiltrados = dadosfiltrados[
                dadosfiltrados['titulo'].str.contains(gettitulo, case=False, na=False)
            ]
        else:
            dadosfiltrados = dadosfiltrados.copy()

        itensporpagina = 10

        total_itens = len(dadosfiltrados)
        total_paginas = (total_itens + itensporpagina - 1) // itensporpagina
        if total_paginas == 0: total_paginas = 1
        if paginaatual > total_paginas: paginaatual = total_paginas

        inicio = (paginaatual - 1) * itensporpagina
        fim = inicio + itensporpagina

        resultado = dadosfiltrados.iloc[inicio:fim]

        listapararetorno = resultado.to_dict(orient='records')

        for filme in listapararetorno:

            try:
                listageneros = ast.literal_eval(filme['generos'])
                filme['generos'] = [g['name'] for g in listageneros]
            except:
                filme['generos'] = []

            try:
                listaidiomas = ast.literal_eval(filme['idiomasfalados'])
                filme['idiomasfalados'] = [i['name'] for i in listaidiomas]
            except:
                filme['idiomasfalados'] = []

            try:
                listapalavras = ast.literal_eval(filme['palavraschave'])
                filme['palavraschave'] = [p['name'] for p in listapalavras]
            except:
                filme['palavraschave'] = []

            try:
                listapalavras = ast.literal_eval(filme['companhiasproducao'])
                filme['companhiasproducao'] = [p['name'] for p in listapalavras]
            except:
                filme['companhiasproducao'] = []

            try:
                listapalavras = ast.literal_eval(filme['paisesproducao'])
                filme['paisesproducao'] = [p['name'] for p in listapalavras]
            except:
                filme['paisesproducao'] = []

        total_itens = len(dadosfiltrados)

        if total_itens == 0:
            totalpaginas = 1
        else:
            totalpaginas = (total_itens + itensporpagina - 1) // itensporpagina

        return Response({
            "status": "sucesso",
            "paginaatual": paginaatual,
            "itensencontrados": total_itens,
            "totalpaginas": totalpaginas,
            "listafilmes": listapararetorno
        })