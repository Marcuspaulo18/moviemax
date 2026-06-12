
const APP = {
    APIURL: '/apirecomenda/filmes/',

    state: {
        paginaAtual: 1,
        totalPaginas: 1,
        filtroGeneroAtual: '',
        filtroTituloAtual: '',
        carregando: false
    },

    elementos: {},

    init: function() {
        console.log('Inicializando moviemax...');
        this.cacheDOMElements();
        this.adicionarEventListeners();
        this.buscarFilmes(1);
    },

    cacheDOMElements: function() {
        this.elementos = {
            filtroGenero: document.getElementById('filtroGenero'),
            filtroTitulo: document.getElementById('filtroTitulo'),
            btnPesquisar: document.getElementById('btnPesquisar'),
            btnLimpar: document.getElementById('btnLimpar'),
            conteudoPrincipal: document.getElementById('conteudoPrincipal'),
            statusInfo: document.getElementById('statusInfo'),
            paginacaoContainer: document.getElementById('paginacaoContainer'),
            infoPaginacao: document.getElementById('infoPaginacao'),
            btnAnterior: document.getElementById('btnAnterior'),
            btnProximo: document.getElementById('btnProximo')
        };
    },

    adicionarEventListeners: function() {
        this.elementos.btnPesquisar.addEventListener('click', () => this.executarPesquisa());
        this.elementos.btnLimpar.addEventListener('click', () => this.limparFiltros());

        this.elementos.btnAnterior.addEventListener('click', () => this.irParaPaginaAnterior());
        this.elementos.btnProximo.addEventListener('click', () => this.irParaProximaPagina());

        this.elementos.filtroGenero.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.executarPesquisa();
        });

        this.elementos.filtroTitulo.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.executarPesquisa();
        });
    }
};


APP.buscarEAtualizarPoster = function(titulo, cardElement) {
    const API_KEY = '0952ce440e4c723a2cc5b6c3df8c6c27';
    const url = `https://api.themoviedb.org/3/search/movie?api_key=${API_KEY}&query=${encodeURIComponent(titulo)}&language=pt-BR`;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Erro TMDb');
            return response.json();
        })
        .then(dados => {

            if (dados.results && dados.results.length > 0 && dados.results[0].poster_path) {
                const posterPath = dados.results[0].poster_path;
                const urlImagemFinal = `https://image.tmdb.org/t/p/w500${posterPath}`;

                const imgElement = cardElement.querySelector('.filme-poster-img');
                const placeholder = cardElement.querySelector('.filme-poster-placeholder');

                if (imgElement) {
                    imgElement.src = urlImagemFinal;
                    imgElement.alt = titulo;
                    imgElement.style.display = 'block';
                    if (placeholder) placeholder.style.display = 'none';
                }
            }
        })
        .catch(erro => {
            console.warn(`Não foi possível carregar o pôster para: ${titulo}`, erro);
        });
};

APP.buscarFilmes = function(pagina = 1) {
    if (this.state.carregando) return;

    this.state.carregando = true;
    this.state.paginaAtual = pagina;

    this.elementos.conteudoPrincipal.innerHTML = this.gerarHTMLCarregamento();

    let url = `${this.APIURL}?pagina=${pagina}`;

    if (this.state.filtroGeneroAtual) {
        url += `&genero=${encodeURIComponent(this.state.filtroGeneroAtual)}`;
    }

    if (this.state.filtroTituloAtual) {
        url += `&titulo=${encodeURIComponent(this.state.filtroTituloAtual)}`;
    }

    console.log('Buscando filmes:', url);

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(dados => {
        console.log('Dados recebidos:', dados);
        this.state.carregando = false;

        this.state.totalPaginas = parseInt(dados.totalpaginas, 10) || 1;
        this.state.paginaAtual = parseInt(dados.paginaatual, 10) || 1;

        this.renderizarFilmes(dados.listafilmes);
        this.atualizarStatus(dados);
        this.atualizarPaginacao(dados);

        window.scrollTo({ top: 0, behavior: 'smooth' });
    })
    .catch(erro => {
        console.error('Erro ao buscar filmes:', erro);
        this.state.carregando = false;
        this.mostrarErro(erro.message);
    });
};

APP.executarPesquisa = function() {
    this.state.filtroGeneroAtual = this.elementos.filtroGenero.value.trim();
    this.state.filtroTituloAtual = this.elementos.filtroTitulo.value.trim();
    this.buscarFilmes(1);
};

APP.limparFiltros = function() {
    this.elementos.filtroGenero.value = '';
    this.elementos.filtroTitulo.value = '';
    this.state.filtroGeneroAtual = '';
    this.state.filtroTituloAtual = '';
    this.buscarFilmes(1);
    this.elementos.filtroGenero.focus();
};

APP.irParaPaginaAnterior = function() {
    if (this.state.paginaAtual > 1) {
        this.buscarFilmes(this.state.paginaAtual - 1);
    }
};


APP.irParaProximaPagina = function() {
    if (this.state.paginaAtual < this.state.totalPaginas) {
        this.buscarFilmes(this.state.paginaAtual + 1);
    }
};

APP.renderizarFilmes = function(filmes) {
    if (!filmes || filmes.length === 0) {
        this.mostrarVazio();
        return;
    }

    const grid = document.createElement('div');
    grid.className = 'filmes-grid';

    filmes.forEach((filme) => {
        const card = this.criarCartaoFilme(filme);
        grid.appendChild(card);

        if (filme.titulo) {
            this.buscarEAtualizarPoster(filme.titulo, card);
        }
    });

    this.elementos.conteudoPrincipal.innerHTML = '';
    this.elementos.conteudoPrincipal.appendChild(grid);
};


APP.criarCartaoFilme = function(filme) {
    const card = document.createElement('div');
    card.style.cursor = 'pointer';
    card.className = 'filme-card';

    card.setAttribute('data-id', filme.idefilme);

    const generos = Array.isArray(filme.generos) ? filme.generos.slice(0, 3) : [];
    const generosHTML = generos.length > 0
        ? generos.map(g => `<span class="genero-tag">${APP.sanitizarHTML(g)}</span>`).join('')
        : '<span class="genero-tag">Sem gênero</span>';

    card.innerHTML = `
        <div class="filme-poster-container">
            <img src="" alt="Carregando..." class="filme-poster-img" style="display:none;">
            <div class="filme-poster-placeholder">🎬</div>
        </div>
        <div class="filme-info">
            <div class="filme-titulo" style="font-weight: bold; margin-top: 5px;">${APP.sanitizarHTML(filme.titulo)}</div>
            <div class="filme-generos">${generosHTML}</div>
        </div>
    `;

    card.addEventListener('click', function() {
        window.location.href = `http://127.0.0.1:8000/portalfilmes/filmes.html?idefilme=${filme.idefilme}`;
    });

    return card;
};

APP.atualizarStatus = function(dados) {
    const totalFilmes = dados.itensencontrados;
    const paginaAtualInfo = dados.paginaatual;

    let textoFiltros = '';
    if (this.state.filtroGeneroAtual || this.state.filtroTituloAtual) {
        const filtros = [];

        if (this.state.filtroGeneroAtual) {
            filtros.push(`gênero: <strong>${APP.sanitizarHTML(this.state.filtroGeneroAtual)}</strong>`);
        }

        if (this.state.filtroTituloAtual) {
            filtros.push(`título: <strong>${APP.sanitizarHTML(this.state.filtroTituloAtual)}</strong>`);
        }

        textoFiltros = ` - Filtros: ${filtros.join(', ')}`;
    }

    this.elementos.statusInfo.innerHTML = `
        <span class="status-texto">
            Mostrando filmes da página <strong>${paginaAtualInfo}</strong>
            | Total encontrado: <strong>${totalFilmes}</strong> filmes${textoFiltros}
        </span>
    `;
};

APP.atualizarPaginacao = function(dados) {
    const paginaAtualInfo = parseInt(dados.paginaatual, 10);
    const totalPaginasInfo = parseInt(dados.totalpaginas, 10);

    this.elementos.infoPaginacao.textContent =
        `Página ${paginaAtualInfo} de ${totalPaginasInfo}`;

    this.elementos.btnAnterior.disabled = (paginaAtualInfo <= 1);
    this.elementos.btnProximo.disabled = (paginaAtualInfo >= totalPaginasInfo);

    if (totalPaginasInfo > 1) {
        this.elementos.paginacaoContainer.style.display = 'flex';
    } else {
        this.elementos.paginacaoContainer.style.display = 'none';
    }
};


APP.gerarHTMLCarregamento = function() {
    return `
        <div class="carregando">
            <div class="spinner"></div>
            <p>Carregando filmes...</p>
        </div>
    `;
};

APP.mostrarVazio = function() {
    const html = `
        <div class="vazio">
            <div class="vazio-icone">🎬</div>
            <p class="vazio-texto">Nenhum filme encontrado</p>
            <p>Tente ajustar seus filtros</p>
        </div>
    `;
    this.elementos.conteudoPrincipal.innerHTML = html;
};

APP.mostrarErro = function(mensagem) {
    const html = `
        <div class="vazio">
            <div class="vazio-icone">⚠️</div>
            <p class="vazio-texto">Erro ao carregar filmes</p>
            <p>${APP.sanitizarHTML(mensagem)}</p>
        </div>
    `;
    this.elementos.conteudoPrincipal.innerHTML = html;
};


APP.sanitizarHTML = function(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        APP.init();
    });
} else {
    APP.init();
}