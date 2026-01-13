// Elementos DOM
const ipsInput = document.getElementById('ips-input');
const btnTestar = document.getElementById('btn-testar');
const btnLimpar = document.getElementById('btn-limpar');
const btnExportar = document.getElementById('btn-exportar');
const loading = document.getElementById('loading');
const resultadosPanel = document.getElementById('resultados-panel');
const resultadosBody = document.getElementById('resultados-body');
const erroPanel = document.getElementById('erro-panel');
const erroTexto = document.getElementById('erro-texto');
const estatisticas = document.getElementById('estatisticas');

// Event listeners
btnTestar.addEventListener('click', executarTestes);
btnLimpar.addEventListener('click', limpar);
btnExportar.addEventListener('click', exportarCSV);

// Função para executar testes
async function executarTestes() {
    const ips = ipsInput.value.trim();
    
    if (!ips) {
        mostrarErro('Por favor, insira pelo menos um IP para testar.');
        return;
    }
    
    // Obtém configurações
    const porta = parseInt(document.getElementById('porta').value) || 8080;
    const timeout = parseInt(document.getElementById('timeout').value) || 5;
    const verificarSsl = document.getElementById('verificar-ssl').checked;
    
    // Esconde painéis anteriores
    resultadosPanel.classList.add('hidden');
    erroPanel.classList.add('hidden');
    
    // Mostra loading
    loading.classList.remove('hidden');
    btnTestar.disabled = true;
    
    try {
        const response = await fetch('/api/testar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ips: ips,
                porta: porta,
                timeout: timeout,
                verificar_ssl: verificarSsl
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.erro || 'Erro ao executar testes');
        }
        
        if (data.sucesso) {
            exibirResultados(data.resultados);
            calcularEstatisticas(data.resultados);
        }
        
    } catch (error) {
        mostrarErro('Erro ao executar testes: ' + error.message);
    } finally {
        loading.classList.add('hidden');
        btnTestar.disabled = false;
    }
}

// Função para exibir resultados na tabela
function exibirResultados(resultados) {
    resultadosBody.innerHTML = '';
    
    resultados.forEach(resultado => {
        const row = document.createElement('tr');
        
        // IP
        const tdIp = document.createElement('td');
        tdIp.textContent = resultado.ip;
        row.appendChild(tdIp);
        
        // HTTP
        const tdHttp = document.createElement('td');
        tdHttp.textContent = resultado.http || 'N/A';
        tdHttp.className = getClasseResultado(resultado.http);
        row.appendChild(tdHttp);
        
        // HTTPS
        const tdHttps = document.createElement('td');
        tdHttps.textContent = resultado.https || 'N/A';
        tdHttps.className = getClasseResultado(resultado.https);
        row.appendChild(tdHttps);
        
        // Status
        const tdStatus = document.createElement('td');
        const badge = document.createElement('span');
        badge.className = `status-badge status-${resultado.status.toLowerCase()}`;
        badge.textContent = resultado.status;
        tdStatus.appendChild(badge);
        row.appendChild(tdStatus);
        
        resultadosBody.appendChild(row);
    });
    
    resultadosPanel.classList.remove('hidden');
    
    // Scroll suave até os resultados
    resultadosPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Função para determinar classe CSS do resultado
function getClasseResultado(resultado) {
    if (!resultado) return '';
    
    if (resultado.includes('OK')) {
        return 'resultado-ok';
    } else if (resultado.includes('Timeout')) {
        return 'resultado-timeout';
    } else {
        return 'resultado-error';
    }
}

// Função para calcular e exibir estatísticas
function calcularEstatisticas(resultados) {
    const total = resultados.length;
    let ok = 0;
    let timeout = 0;
    let error = 0;
    
    resultados.forEach(r => {
        if (r.status === 'OK') {
            ok++;
        } else if (r.status === 'Timeout') {
            timeout++;
        } else {
            error++;
        }
    });
    
    estatisticas.innerHTML = `
        <div class="stat-badge stat-ok">
            OK: ${ok} (${((ok/total)*100).toFixed(1)}%)
        </div>
        <div class="stat-badge stat-timeout">
            Timeout: ${timeout} (${((timeout/total)*100).toFixed(1)}%)
        </div>
        <div class="stat-badge stat-error">
            Error: ${error} (${((error/total)*100).toFixed(1)}%)
        </div>
    `;
}

// Função para mostrar erro
function mostrarErro(mensagem) {
    erroTexto.textContent = mensagem;
    erroPanel.classList.remove('hidden');
    erroPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Função para limpar
function limpar() {
    ipsInput.value = '';
    resultadosPanel.classList.add('hidden');
    erroPanel.classList.add('hidden');
    resultadosBody.innerHTML = '';
    estatisticas.innerHTML = '';
}

// Função para exportar CSV
function exportarCSV() {
    const rows = Array.from(resultadosBody.querySelectorAll('tr'));
    
    if (rows.length === 0) {
        mostrarErro('Nenhum resultado para exportar.');
        return;
    }
    
    let csv = 'IP,HTTP,HTTPS,Status\n';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const ip = cells[0].textContent;
        const http = cells[1].textContent.replace(/,/g, ';');
        const https = cells[2].textContent.replace(/,/g, ';');
        const status = cells[3].textContent;
        
        csv += `"${ip}","${http}","${https}","${status}"\n`;
    });
    
    // Cria blob e faz download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `resultados_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
