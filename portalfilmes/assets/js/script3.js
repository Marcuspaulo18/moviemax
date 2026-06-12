const APIURL = 'http://127.0.0.1:8000/apirecomenda/filme/?idefilme=';
const TMDB_API_KEY = '0952ce440e4c723a2cc5b6c3df8c6c27';
const TMDB_BASE_URL = 'https://api.themoviedb.org/3/movie/';
const TMDB_BACKDROP_W1280 = 'https://image.tmdb.org/t/p/w1280';
const TMDB_POSTER_W500 = 'https://image.tmdb.org/t/p/w500';

function voltarPagina() {
    window.history.back();
}

async function obterImagensDoTMDB(idefilme) {
    try {
        const resposta = await fetch(`${TMDB_BASE_URL}${idefilme}?api_key=${TMDB_API_KEY}`);
        if (resposta.ok) {
            const tmdbData = await resposta.json();
            return {
                backdrop: tmdbData.backdrop_path ? `${TMDB_BACKDROP_W1280}${tmdbData.backdrop_path}` : '',
                poster: tmdbData.poster_path ? `${TMDB_POSTER_W500}${tmdbData.poster_path}` : ''
            };
        }
    } catch (err) {
        console.error("Não foi possível carregar as imagens do TMDB para o id " + idefilme, err);
    }
    return { backdrop: '', poster: '' };
}

async function carregarPaginaFilme(ideFilme, mudarUrlNoHistorico = false) {
try {
    document.getElementById('loader').style.opacity = '1';
    document.getElementById('loader').style.display = 'flex';

    if (mudarUrlNoHistorico) {
        const novaUrl = `${window.location.pathname}?idefilme=${ideFilme}`;
        window.history.pushState({ idefilme: ideFilme }, '', novaUrl);
     }

    const response = await fetch(`${APIURL}${ideFilme}`);
    if (!response.ok) {
        document.getElementById('loader').innerText = "Filme não encontrado na base de dados.";
        return;
    }
    const dadosFilmeLocal = await response.json();

    const imagensTMDB = await obterImagensDoTMDB(ideFilme);

    const banner = document.getElementById('filmeBanner');
    if (imagensTMDB.backdrop) {
        banner.style.backgroundImage = `url('${imagensTMDB.backdrop}')`;
    } else {
        banner.style.backgroundImage = `linear-gradient(45deg, #111, #222)`;
    }

    document.getElementById('filmeTitulo').innerText = dadosFilmeLocal.titulo;
    document.getElementById('filmeNota').innerText = dadosFilmeLocal.notamedia.toFixed(1);

    const anoFilme = dadosFilmeLocal.datalancamento ? dadosFilmeLocal.datalancamento.substring(0, 4) : "----";
    document.getElementById('filmeAno').innerText = anoFilme;
    document.getElementById('filmeFichaAno').innerText = anoFilme;

    document.getElementById('filmeTagGenero').innerText = dadosFilmeLocal.generos.split(',')[0].trim();

    document.getElementById('filmeMiniSinopse').innerText = dadosFilmeLocal.resumo ? dadosFilmeLocal.resumo.substring(0, 140) + "..." : "Sem resumo.";

    document.getElementById('filmeResumoCompleto').innerText = dadosFilmeLocal.resumo || "Sinopse indisponível.";
    document.getElementById('filmeDiretor').innerText = dadosFilmeLocal.diretor;
    document.getElementById('filmeElenco').innerText = dadosFilmeLocal.elenco;
    document.getElementById('filmeListaGeneros').innerText = dadosFilmeLocal.generos;
    document.getElementById('filmeDuracao').innerText = dadosFilmeLocal.tempoduracao;

    const containerRec = document.getElementById('containerRecomendados');
    containerRec.innerHTML = '';


    const promessasDeCards = dadosFilmeLocal.recomendados.map(async (rec) => {
        const imgRec = await obterImagensDoTMDB(rec.idefilme);
        const urlPosterReal = imgRec.poster || 'https://via.placeholder.com/300x450?text=Sem+Imagem';
        return `
            <div class="rec-card" onclick="carregarPaginaFilme(${rec.idefilme}, true)">
                <div class="rec-poster" style="background-image: url('${urlPosterReal}');"></div>
                <p style="padding: 12px 10px 5px 10px; margin: 0; font-size: 0.85rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${rec.titulo}">
                    ${rec.titulo}
                </p>
            </div>
        `;
    });

    const htmlGerado = await Promise.all(promessasDeCards);
    containerRec.innerHTML = htmlGerado.join('');

    document.getElementById('loader').style.opacity = '0';
    setTimeout(() => document.getElementById('loader').style.display = 'none', 300);
    window.scrollTo({ top: 0, behavior: 'smooth' });

} catch (error) {
    console.error("Erro no fluxo do ecossistema de mídias:", error);
    document.getElementById('loader').innerText = "Erro ao carregar o filme.";
}
}


const urlParams = new URLSearchParams(window.location.search);
const idefilme = urlParams.get('idefilme');

if (idefilme) {
    carregarPaginaFilme(idefilme, false);
} else {
    alert("Nenhum ID de filme foi fornecido na URL.");
}

window.addEventListener('popstate', function(event) {
    // Pega o ID do filme da nova URL que acabou de mudar
    const urlParamsAtualizada = new URLSearchParams(window.location.search);
    const idFilmeAnterior = urlParamsAtualizada.get('idefilme');

    if (idFilmeAnterior) {
        // Carrega o filme antigo, mas com FALSE para não criar um looping no histórico
        carregarPaginaFilme(idFilmeAnterior, false);
    }
});