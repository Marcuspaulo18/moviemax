import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from deep_translator import GoogleTranslator
import kagglehub
import os
import ast
from rest_framework import status
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

destino = kagglehub.dataset_download("tmdb/tmdb-movie-metadata")

diretoriocredito = os.path.join(destino, "tmdb_5000_credits.csv")
diretoriofilme = os.path.join(destino, "tmdb_5000_movies.csv")

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_columns', 20)

dadosfilme = pd.read_csv(diretoriofilme)
dadosnota = pd.read_csv(diretoriocredito)

dadosfilme = dadosfilme.infer_objects(copy=False) # Ajuda o pandas a entender os tipos de dados melhor
dadosfilme = dadosfilme.fillna("")

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

        dadosfiltrados = dadosfilme.copy()

        if getgenero:
            dadosfiltrados = dadosfiltrados[
                dadosfiltrados['generos'].str.contains(getgenero, case=False, na=False)
            ]

        if gettitulo:
            termos_busca = [gettitulo]

            try:
                traducao_en = GoogleTranslator(source='pt', target='en').translate(gettitulo)

                if traducao_en and traducao_en.lower() != gettitulo.lower():
                    termos_busca.append(traducao_en)
            except Exception as e:
                print(f"Erro temporário na tradução: {e}")

            expressao_regex = "|".join([f".*{t}.*" for t in termos_busca])

            dadosfiltrados = dadosfiltrados[
                dadosfiltrados['titulo'].str.contains(expressao_regex, case=False, na=False)
            ]

        itensporpagina = 24
        total_itens = len(dadosfiltrados)

        # Calcula o total de páginas real baseado nos itens filtrados
        total_paginas = (total_itens + itensporpagina - 1) // itensporpagina
        if total_paginas == 0:
            total_paginas = 1

        # 3. Validação e Captura da Página Atual
        try:
            paginaatual = int(request.query_params.get('pagina', 1))
            if paginaatual < 1:
                paginaatual = 1
        except ValueError:
            paginaatual = 1

        if paginaatual > total_paginas:
            paginaatual = total_paginas

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
                listacompanhias = ast.literal_eval(filme['companhiasproducao'])
                filme['companhiasproducao'] = [p['name'] for p in listacompanhias]
            except:
                filme['companhiasproducao'] = []

            try:
                listapaises = ast.literal_eval(filme['paisesproducao'])
                filme['paisesproducao'] = [p['name'] for p in listapaises]
            except:
                filme['paisesproducao'] = []

        return Response({
            "status": "sucesso",
            "paginaatual": paginaatual,
            "itensencontrados": total_itens,
            "totalpaginas": total_paginas,
            "listafilmes": listapararetorno
        })


class Clusterfilmes(APIView):
    def get(self, request, format=None):
        try:

            datasetunico = pd.merge(dadosfilme, dadosnota, on='idefilme')
            minimo = datasetunico['totalvotos'].quantile(0.25)
            cluster = datasetunico.loc[datasetunico['totalvotos'] >= minimo].copy()
            cluster = cluster.dropna(subset=['popularidade', 'notamedia'])
            cluster = cluster[cluster['popularidade'] <= 300]

            # 2. K-Means
            scaler = StandardScaler()
            dadosescalonados = scaler.fit_transform(cluster[['popularidade', 'notamedia']])
            kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
            cluster['cluster'] = kmeans.fit_predict(dadosescalonados)

            tradutor = GoogleTranslator(source='en', target='pt')

            # 3. GERAÇÃO DAS MÉTRICAS POR GRUPO
            metricasclusters = {}
            for i in range(4):
                grupo = cluster[cluster['cluster'] == i]

                if not grupo.empty:

                    maispopular = grupo.loc[grupo['popularidade'].idxmax()]
                    maisvisto = grupo.loc[grupo['totalvotos'].idxmax()]
                    maisvotado = grupo.loc[grupo['notamedia'].idxmax()]

                    try:
                        titpopular = tradutor.translate(maispopular['titulo_x'])
                        titvisto = tradutor.translate(maisvisto['titulo_x'])
                        titvotado = tradutor.translate(maisvotado['titulo_x'])
                    except Exception as e:
                        # Fallback caso a API de tradução falhe
                        titpopular = maispopular['titulo_x']
                        titvisto = maisvisto['titulo_x']
                        titvotado = maisvotado['titulo_x']

                    metricasclusters[f'grupo_{i}'] = {
                        'mediapopularidade': float(grupo['popularidade'].mean()),
                        'medianota': float(grupo['notamedia'].mean()),
                        'maispopular': {
                            'titulo': titpopular,
                            'valor': float(maispopular['popularidade'])
                        },
                        'maisvisto': {
                            'titulo': titvisto,
                            'valor': int(maisvisto['totalvotos'])
                        },
                        'maisbempontuado': {
                            'titulo': titvotado,
                            'valor': float(maisvotado['notamedia'])
                        }
                    }

            def extrair_top_10(df, coluna, ascendente=False):
                """Função auxiliar para ordenar e estruturar o top 10"""
                if ascendente:
                    df_ordenado = df.nsmallest(10, coluna)
                else:
                    df_ordenado = df.nlargest(10, coluna)

                tradutor = GoogleTranslator(source='en', target='pt')

                lista_retorno = []
                for _, row in df_ordenado.iterrows():
                    titulo_original = row['titulo_x']

                    try:
                        titulo_traduzido = tradutor.translate(titulo_original)
                        if not titulo_traduzido:
                            titulo_traduzido = titulo_original
                    except Exception as e:
                        print(f"Erro ao traduzir: {e}")
                        titulo_traduzido = titulo_original

                    lista_retorno.append({
                        'titulo': titulo_traduzido,  # Aqui entra o título traduzido
                        'valor': float(row[coluna]) if coluna != 'totalvotos' else int(row[coluna]),
                        'cluster': int(row['cluster'])
                    })
                return lista_retorno

            rankings_gerais = {
                'maiores': {
                    'mais_populares': extrair_top_10(cluster, 'popularidade'),
                    'mais_vistos': extrair_top_10(cluster, 'totalvotos'),
                    'mais_avaliados': extrair_top_10(cluster, 'notamedia')
                },
                'menores': {
                    'menos_populares': extrair_top_10(cluster, 'popularidade', ascendente=True),
                    'menos_vistos': extrair_top_10(cluster, 'totalvotos', ascendente=True),
                    'menos_avaliados': extrair_top_10(cluster, 'notamedia', ascendente=True)
                }
            }

            # 4. Formatação do JSON Final com os TRÊS blocos de dados
            filmes_lista = []
            for _, row in cluster.iterrows():
                filmes_lista.append({
                    'idefilme': int(row['idefilme']),
                    'titulo': row['titulo_x'],
                    'popularidade': float(row['popularidade']),
                    'notamedia': float(row['notamedia']),
                    'cluster': int(row['cluster'])
                })

            resposta_final = {
                'filmes': filmes_lista,
                'insights': metricasclusters,
                'rankings': rankings_gerais  # <-- Novo bloco enviado ao Front-end
            }

            return Response(resposta_final, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


import ast
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DetalheFilme(APIView):
    _base_processada = False
    _cluster_df = None
    _similaridade = None
    _indices = None

    @classmethod
    def _inicializar_motor_ia(cls):
        if cls._base_processada:
            return

        datasetunico = pd.merge(dadosfilme, dadosnota, on='idefilme')
        minimo = datasetunico['totalvotos'].quantile(0.25)

        df_filtrado = datasetunico.loc[datasetunico['totalvotos'] >= minimo].copy()
        df_filtrado = df_filtrado.dropna(subset=['popularidade', 'notamedia'])
        cls._cluster_df = df_filtrado[df_filtrado['popularidade'] <= 300].copy()

        textos_para_vetorizar = []

        for idx, row in cls._cluster_df.iterrows():
            # Captura a sinopse
            resumo = str(row['resumo']) if pd.notna(row['resumo']) else ""

            atores = []
            try:
                lista_elenco = ast.literal_eval(row['elenco'])
                atores = [actor['name'].replace(" ", "").lower() for actor in lista_elenco[:3]]
            except:
                pass

            diretor = ""
            try:
                lista_equipe = ast.literal_eval(row['equipe'])
                dir_nome = next((m['name'] for m in lista_equipe if m['job'] == 'Director'), "")
                diretor = dir_nome.replace(" ", "").lower()
            except:
                pass

            sopa_conteudo = f"{resumo} {' '.join(atores)} {diretor}"
            textos_para_vetorizar.append(sopa_conteudo)

        cls._cluster_df['sopa_metadados'] = textos_para_vetorizar

        vetor = TfidfVectorizer(stop_words='english')
        matrixvetorial = vetor.fit_transform(cls._cluster_df['sopa_metadados'])
        cls._similaridade = cosine_similarity(matrixvetorial, matrixvetorial)


        cls._indices = pd.Series(cls._cluster_df.index, index=cls._cluster_df['idefilme']).drop_duplicates()
        cls._base_processada = True

    def get(self, request, idefilme=None):
        try:
            self._inicializar_motor_ia()

            if idefilme is None:
                idefilme = request.GET.get('idefilme')

            if not idefilme:
                return Response({"error": "O parâmetro 'idefilme' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

            idefilme = int(idefilme)
            if idefilme not in self._indices:
                return Response(
                    {"error": f"Filme com ID {idefilme} não atende aos critérios do Cluster."},
                    status=status.HTTP_404_NOT_FOUND
                )

            idx_original = self._indices[idefilme]
            posicao_real = self._cluster_df.index.get_loc(idx_original)
            filme_alvo = self._cluster_df.iloc[posicao_real]

            # Parseamento padrão para exibição visual no front-end
            atores_str = "Não informado"
            try:
                lista_elenco = ast.literal_eval(filme_alvo['elenco'])
                atores_str = ", ".join([ator['name'] for actor in lista_elenco[:3]])
            except:
                pass

            diretor_str = "Não informado"
            try:
                lista_equipe = ast.literal_eval(filme_alvo['equipe'])
                diretor_str = next((m['name'] for m in lista_equipe if m['job'] == 'Director'), "Não informado")
            except:
                pass

            try:
                lista_generos = ast.literal_eval(filme_alvo['generos'])
                generos_limpos = ", ".join([g['name'] for g in lista_generos])
            except:
                generos_limpos = filme_alvo['generos']

            # Processa o Top 5 Filmes Similares calculados com base na Sopa
            scores = list(enumerate(self._similaridade[posicao_real]))
            scores = sorted(scores, key=lambda x: x[1], reverse=True)
            scores_recomendados = scores[1:6]

            recomendados = []
            for i, score in scores_recomendados:
                row = self._cluster_df.iloc[i]
                recomendados.append({
                    'idefilme': int(row['idefilme']),
                    'titulo': row['titulo_x'],
                    'notamedia': float(row['notamedia'])
                })

            return Response({
                'idefilme': int(filme_alvo['idefilme']),
                'titulo': filme_alvo['titulo_x'],
                'resumo': filme_alvo['resumo'],
                'notamedia': float(filme_alvo['notamedia']),
                'datalancamento': str(filme_alvo['datalancamento']),
                'tempoduracao': f"{int(filme_alvo['tempoduracao'])} minutos" if filme_alvo['tempoduracao'] else "---",
                'generos': generos_limpos,
                'elenco': elenco_formatado if 'elenco_formatado' in locals() else atores_str,
                'diretor': diretor_str,
                'recomendados': recomendados
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)