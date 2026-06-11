const APIURL = 'http://127.0.0.1:8000/apirecomenda/dados/';

const clusterColors = [
    'rgba(68, 1, 84, 0.7)',   // Roxo
    'rgba(49, 104, 142, 0.7)', // Azul
    'rgba(53, 183, 121, 0.7)', // Verde
    'rgba(220, 190, 30, 0.7)'  // Amarelo Ajustado
];
const borderColors = ['#440154', '#31688e', '#35b779', '#fde725'];

async function fetchAndRender() {
    try {
        const response = await fetch(APIURL);
        const rawData = await response.json();

        const filmes = rawData.filmes;
        const insights = rawData.insights;

        document.getElementById('loading').style.display = 'none';
        document.getElementById('clusterChart').style.display = 'block';
        document.getElementById('titulo-insights').style.display = 'block';

        const ctx = document.getElementById('clusterChart');
        const datasets = [
            { label: 'Grupo 1', data: [], backgroundColor: clusterColors[0], borderColor: borderColors[0] },
            { label: 'Grupo 2', data: [], backgroundColor: clusterColors[1], borderColor: borderColors[1] },
            { label: 'Grupo 3', data: [], backgroundColor: clusterColors[2], borderColor: borderColors[2] },
            { label: 'Grupo 4', data: [], backgroundColor: clusterColors[3], borderColor: borderColors[3] }
        ];

        filmes.forEach(item => {
            datasets[item.cluster].data.push({
                x: item.popularidade, y: item.notamedia, titulo: item.titulo, id: item.idefilme
            });
        });

        new Chart(ctx, {
            type: 'scatter',
            data: { datasets: datasets },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Popularidade' }, min: -5, max: 300 },
                    y: { title: { display: true, text: 'Nota Média' } }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: context => `Filme: ${context.raw.titulo} | Pop: ${context.raw.x.toFixed(1)} | Nota: ${context.raw.y}`
                        }
                    }
                }
            }
        });

        const grid = document.getElementById('insightsGrid');
        grid.innerHTML = '';

        for (let i = 0; i < 4; i++) {
            const info = insights[`grupo_${i}`];
            if (!info) continue;

            const card = document.createElement('div');
            card.className = 'card';
            card.style.borderTopColor = borderColors[i];
            card.style.marginTop = 10;

            card.innerHTML = `
                <h3>Grupo ${i}</h3>
                <div class="metric-title">Médias do Grupo</div>
                <div class="metric-value">Nota: ${info.medianota.toFixed(2)} | Pop: ${info.mediapopularidade.toFixed(1)}</div>

                <div class="metric-title">Mais Popular do Grupo</div>
                <div class="metric-value"><span class="highlight-movie">${info.maispopular.titulo}</span> (${info.maispopular.valor.toFixed(1)}p)</div>

                <div class="metric-title">Mais Visto (Mais Votos)</div>
                <div class="metric-value"><span class="highlight-movie">${info.maisvisto.titulo}</span> (${info.maisvisto.valor.toLocaleString()} votos)</div>

                <div class="metric-title">Maior Nota Média</div>
                <div class="metric-value"><span class="highlight-movie">${info.maisbempontuado.titulo}</span> (Nota: ${info.maisbempontuado.valor})</div>

            `;
            grid.appendChild(card);
        }
        const rankings = rawData.rankings;


       const containerMaiores = document.getElementById('rankingsMaiores');
       containerMaiores.innerHTML = `
           <h2> Top 10 - Maiores Estatísticas Gerais</h2>
           <div class="rankings-grid">
               <div class="ranking-col">
                   <h3> Mais Populares</h3>
                   <ol>${rankings.maiores.mais_populares.map(f => `<li><span style="color:${borderColors[f.cluster]}">■</span> ${f.titulo} (${f.valor.toFixed(1)}p)</li>`).join('')}</ol>
               </div>
               <div class="ranking-col">
                   <h3> Mais Vistos (Votos)</h3>
                   <ol>${rankings.maiores.mais_vistos.map(f => `<li><span style="color:${borderColors[f.cluster]}">■</span> ${f.titulo} (${f.valor.toLocaleString()})</li>`).join('')}</ol>
               </div>
               <div class="ranking-col">
                   <h3> Maiores Notas</h3>
                   <ol>${rankings.maiores.mais_avaliados.map(f => `<li><span style="color:${borderColors[f.cluster]}">■</span> ${f.titulo} (${f.valor.toFixed(1)})</li>`).join('')}</ol>
               </div>
           </div>
       `;

       const containerMenores = document.getElementById('rankingsMenores');
       containerMenores.innerHTML = `
           <h2> Top 10 - Menores Estatísticas Gerais</h2>
           <div class="rankings-grid">
               <div class="ranking-col">
                   <h3> Menos Populares</h3>
                   <ol>${rankings.menores.menos_populares.map(f => `<li><span style="color:${borderColors[f.cluster]}">■</span> ${f.titulo} (${f.valor.toFixed(1)}p)</li>`).join('')}</ol>
               </div>
               <div class="ranking-col">
                   <h3> Menos Vistos (Votos)</h3>
                   <ol>${rankings.menores.menos_vistos.map(f => `<li><span style="color:${borderColors[f.cluster]}">■</span> ${f.titulo} (${f.valor.toLocaleString()})</li>`).join('')}</ol>
               </div>
               <div class="ranking-col">
                   <h3> Menores Notas</h3>
                   <ol>${rankings.menores.menos_avaliados.map(f => `<li><span style="color:${borderColors[f.cluster]}">■</span> ${f.titulo} (${f.valor.toFixed(1)})</li>`).join('')}</ol>
               </div>
           </div>
       `;

   } catch (error) {
       console.error(error);
       document.getElementById('loading').innerText = "Erro ao processar as métricas.";
   }
}

fetchAndRender();