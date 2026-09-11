import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Simulador de Oferta e Demanda (Tempo Real)",
    page_icon="📈",
    layout="wide"
)

# HTML/JS com Chart.js e evento 'oninput' para atualização instantânea durante o arrasto do slider (sem soltar o mouse)
html_code = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { margin: 0; padding: 10px; background-color: #f8f9fa; color: #212529; }
        .container { display: flex; flex-direction: row; gap: 20px; flex-wrap: wrap; }
        .controls { flex: 1; min-width: 320px; background: #ffffff; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); max-height: 85vh; overflow-y: auto; }
        .graph-panel { flex: 2; min-width: 450px; background: #ffffff; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; flex-direction: column; }
        h2 { margin-top: 0; color: #1e293b; font-size: 1.25rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }
        h3 { font-size: 0.95rem; margin: 12px 0 6px 0; color: #475569; }
        .slider-group { margin-bottom: 10px; }
        .slider-label { display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; color: #334155; }
        input[type=range] { width: 100%; margin: 4px 0; cursor: pointer; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 15px; }
        .stat-card { background: #f1f5f9; padding: 10px; border-radius: 6px; text-align: center; }
        .stat-card div:first-child { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
        .stat-card div:last-child { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-top: 2px; }
        .status-box { margin-top: 12px; padding: 10px; border-radius: 6px; font-weight: 600; font-size: 0.9rem; text-align: center; }
        .status-equilibrio { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .status-surplus { background-color: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }
        .status-shortage { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
        canvas { max-height: 480px; width: 100% !important; }
    </style>
</head>
<body>

<div class="container">
    <div class="controls">
        <h2>🎛️ Variáveis de Mercado</h2>
        
        <h3>1. Preço do Próprio Bem</h3>
        <div class="slider-group">
            <div class="slider-label"><span>Preço Atual (P)</span><span id="val_p">50</span></div>
            <input type="range" id="p_atual" min="10" max="100" value="50" step="1" oninput="updateAll()">
        </div>

        <h3>2. Determinantes da Demanda (Deslocam D)</h3>
        <div class="slider-group">
            <div class="slider-label"><span>Gostos e Preferências</span><span id="val_gostos">0</span></div>
            <input type="range" id="gostos" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
        <div class="slider-group">
            <div class="slider-label"><span>Número de Consumidores</span><span id="val_cons">0</span></div>
            <input type="range" id="consumidores" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
        <div class="slider-group">
            <div class="slider-label"><span>Preço de Bens Relacionados</span><span id="val_bens">0</span></div>
            <input type="range" id="bens_relacionados" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
        <div class="slider-group">
            <div class="slider-label"><span>Expectativas dos Consumidores</span><span id="val_exp_c">0</span></div>
            <input type="range" id="expectativas_cons" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>

        <h3>3. Determinantes da Oferta (Deslocam S)</h3>
        <div class="slider-group">
            <div class="slider-label"><span>Custo dos Insumos</span><span id="val_insumos">0</span></div>
            <input type="range" id="custo_insumos" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
        <div class="slider-group">
            <div class="slider-label"><span>Nível de Tecnologia</span><span id="val_tec">0</span></div>
            <input type="range" id="tecnologia" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
        <div class="slider-group">
            <div class="slider-label"><span>Número de Vendedores</span><span id="val_vend">0</span></div>
            <input type="range" id="vendedores" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
        <div class="slider-group">
            <div class="slider-label"><span>Expectativas dos Produtores</span><span id="val_exp_p">0</span></div>
            <input type="range" id="expectativas_prod" min="-20" max="20" value="0" step="1" oninput="updateAll()">
        </div>
    </div>

    <div class="graph-panel">
        <h2>📈 Curvas de Oferta e Demanda (Atualização Contínua)</h2>
        <div>
            <canvas id="marketChart"></canvas>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div>Preço Equilíbrio (P*)</div>
                <div id="stat_peq">R$ 0.00</div>
            </div>
            <div class="stat-card">
                <div>Qtd. Equilíbrio (Q*)</div>
                <div id="stat_qeq">0.0 un</div>
            </div>
            <div class="stat-card">
                <div>Qtd. Demandada (Qd)</div>
                <div id="stat_qd">0.0 un</div>
            </div>
            <div class="stat-card">
                <div>Qtd. Ofertada (Qs)</div>
                <div id="stat_qs">0.0 un</div>
            </div>
        </div>

        <div id="status_box" class="status-box status-equilibrio">
            Mercado em Equilíbrio
        </div>
    </div>
</div>

<script>
    const ctx = document.getElementById('marketChart').getContext('2d');
    
    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Demanda (D)',
                    borderColor: '#ef4444',
                    borderWidth: 3,
                    fill: false,
                    data: [],
                    pointRadius: 0
                },
                {
                    label: 'Oferta (S)',
                    borderColor: '#22c55e',
                    borderWidth: 3,
                    fill: false,
                    data: [],
                    pointRadius: 0
                },
                {
                    label: 'Ponto de Equilíbrio (E*)',
                    backgroundColor: '#0284c7',
                    borderColor: '#0284c7',
                    pointRadius: 7,
                    pointHoverRadius: 9,
                    data: [],
                    showLine: false
                },
                {
                    label: 'Ponto no Preço Atual (D)',
                    backgroundColor: '#b91c1c',
                    borderColor: '#b91c1c',
                    pointRadius: 6,
                    pointStyle: 'rectRot',
                    data: [],
                    showLine: false
                },
                {
                    label: 'Ponto no Preço Atual (S)',
                    backgroundColor: '#15803d',
                    borderColor: '#15803d',
                    pointRadius: 6,
                    pointStyle: 'rect',
                    data: [],
                    showLine: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Desativa animação para renderização instantânea a 60 FPS no arrasto
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: { display: true, text: 'Quantidade (Q)', font: { size: 14, weight: 'bold' } },
                    min: 0,
                    max: 160
                },
                y: {
                    title: { display: true, text: 'Preço (P)', font: { size: 14, weight: 'bold' } },
                    min: 0,
                    max: 120
                }
            },
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: Q=${context.parsed.x.toFixed(1)}, P=R$ ${context.parsed.y.toFixed(1)}`;
                        }
                    }
                }
            }
        }
    });

    function getVal(id) { return parseFloat(document.getElementById(id).value); }

    function updateAll() {
        const p_atual = getVal('p_atual');
        const gostos = getVal('gostos');
        const consumidores = getVal('consumidores');
        const bens_relacionados = getVal('bens_relacionados');
        const expectativas_cons = getVal('expectativas_cons');
        
        const custo_insumos = getVal('custo_insumos');
        const tecnologia = getVal('tecnologia');
        const vendedores = getVal('vendedores');
        const expectativas_prod = getVal('expectativas_prod');

        // Atualiza os labels numéricos dos sliders
        document.getElementById('val_p').innerText = p_atual;
        document.getElementById('val_gostos').innerText = gostos;
        document.getElementById('val_cons').innerText = consumidores;
        document.getElementById('val_bens').innerText = bens_relacionados;
        document.getElementById('val_exp_c').innerText = expectativas_cons;
        document.getElementById('val_insumos').innerText = custo_insumos;
        document.getElementById('val_tec').innerText = tecnologia;
        document.getElementById('val_vend').innerText = vendedores;
        document.getElementById('val_exp_p').innerText = expectativas_prod;

        // Deslocamentos das curvas (shifters)
        const shift_D = (1.5 * gostos) + (1.5 * consumidores) + (1.5 * bens_relacionados) + (1.2 * expectativas_cons);
        const shift_S = (1.5 * tecnologia) + (1.5 * vendedores) - (1.5 * custo_insumos) + (1.2 * expectativas_prod);

        const a_D = 120 + shift_D;
        const b_D = 1.2;
        const a_S = -20 + shift_S;
        const b_S = 1.2;

        // Cálculo do Ponto de Equilíbrio
        const P_eq = (a_D - a_S) / (b_D + b_S);
        const Q_eq = a_D - b_D * P_eq;

        // Quantidades no Preço Atual
        const Q_dem = Math.max(0, a_D - b_D * p_atual);
        const Q_ofe = Math.max(0, a_S + b_S * p_atual);

        // Pontos das curvas
        const data_D = [];
        const data_S = [];
        for (let P = 0; P <= 120; P += 1) {
            let Qd = a_D - b_D * P;
            let Qs = a_S + b_S * P;
            if (Qd >= 0) data_D.push({ x: Qd, y: P });
            if (Qs >= 0) data_S.push({ x: Qs, y: P });
        }

        chart.data.datasets[0].data = data_D;
        chart.data.datasets[1].data = data_S;
        chart.data.datasets[2].data = (P_eq >= 0 && Q_eq >= 0) ? [{ x: Q_eq, y: P_eq }] : [];
        chart.data.datasets[3].data = [{ x: Q_dem, y: p_atual }];
        chart.data.datasets[4].data = [{ x: Q_ofe, y: p_atual }];

        chart.update();

        // Atualização dos indicadores de texto
        document.getElementById('stat_peq').innerText = `R$ ${P_eq.toFixed(2)}`;
        document.getElementById('stat_qeq').innerText = `${Q_eq.toFixed(1)} un`;
        document.getElementById('stat_qd').innerText = `${Q_dem.toFixed(1)} un`;
        document.getElementById('stat_qs').innerText = `${Q_ofe.toFixed(1)} un`;

        const statusBox = document.getElementById('status_box');
        const diff = Q_ofe - Q_dem;
        if (Math.abs(p_atual - P_eq) < 0.5) {
            statusBox.className = "status-box status-equilibrio";
            statusBox.innerText = "✅ Mercado em Equilíbrio! (Qd = Qs)";
        } else if (p_atual > P_eq) {
            statusBox.className = "status-box status-surplus";
            statusBox.innerText = `⚠️ Excesso de Oferta (Surplus): +${diff.toFixed(1)} unidades sobram`;
        } else {
            statusBox.className = "status-box status-shortage";
            statusBox.innerText = `🚨 Escassez no Mercado (Shortage): Faltam ${Math.abs(diff).toFixed(1)} unidades`;
        }
    }

    // Inicializa
    updateAll();
</script>
</body>
</html>
"""

st.title("📈 Simulador Interativo de Oferta e Demanda (Arrasto Contínuo)")
st.markdown("""
Esta versão utiliza eventos client-side (`oninput`) em JavaScript para garantir que o gráfico seja atualizado **em tempo real a 60 FPS enquanto você arrasta os sliders**, sem necessidade de soltar o botão do mouse!
""")

components.html(html_code, height=750, scrolling=True)
