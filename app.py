"""
Aplicação Flask para Interface Web de Teste de Conectividade HTTP/HTTPS
"""

from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import logging

from services.http_tester import HTTPTester
from utils.file_reader import validar_ipv4
import config

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Configura logging
logging.basicConfig(level=logging.INFO)


def processar_lista_ips(texto_ips: str) -> List[str]:
    """
    Processa texto com IPs (um por linha) e retorna lista de IPs válidos.
    
    Args:
        texto_ips: String com IPs separados por quebra de linha
        
    Returns:
        Lista de IPs IPv4 válidos
    """
    ips_validos = []
    linhas = texto_ips.strip().split('\n')
    
    for linha in linhas:
        ip = linha.strip()
        # Ignora linhas vazias e comentários
        if ip and not ip.startswith('#'):
            if validar_ipv4(ip):
                ips_validos.append(ip)
    
    return ips_validos


def calcular_workers(numero_ips: int) -> int:
    """Calcula número ideal de workers"""
    workers = max(config.MIN_WORKERS, min(numero_ips // 5, config.MAX_WORKERS))
    workers = min(workers, numero_ips, config.MAX_WORKERS)
    return max(workers, 1)


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/testar', methods=['POST'])
def testar_ips():
    """
    Endpoint para testar IPs.
    Recebe JSON com: { "ips": "string com IPs", "porta": 8080, "timeout": 5 }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'erro': 'Dados não fornecidos'}), 400
        
        texto_ips = data.get('ips', '')
        porta = data.get('porta', config.PORTA_PADRAO)
        timeout = data.get('timeout', config.TIMEOUT_PADRAO)
        verificar_ssl = data.get('verificar_ssl', config.VERIFICAR_SSL)
        
        if not texto_ips:
            return jsonify({'erro': 'Lista de IPs vazia'}), 400
        
        # Processa IPs
        ips = processar_lista_ips(texto_ips)
        
        if not ips:
            return jsonify({'erro': 'Nenhum IP válido encontrado'}), 400
        
        # Inicializa testador
        testador = HTTPTester(
            porta=porta,
            timeout=timeout,
            verificar_ssl=verificar_ssl
        )
        
        # Calcula workers
        num_workers = calcular_workers(len(ips))
        
        # Executa testes em paralelo
        resultados = []
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(testador.testar_ip, ip): ip for ip in ips}
            
            for future in as_completed(futures):
                ip = futures[future]
                try:
                    resultado = future.result()
                    resultados.append(resultado)
                except Exception as e:
                    logging.error(f"Erro ao testar {ip}: {str(e)}")
                    resultados.append({
                        'ip': ip,
                        'http': f'Erro: {str(e)}',
                        'https': f'Erro: {str(e)}'
                    })
        
        # Ordena por IP
        resultados.sort(key=lambda x: x['ip'])
        
        # Formata resultados para o frontend
        resultados_formatados = []
        for r in resultados:
            http_status = r.get('http', 'N/A')
            https_status = r.get('https', 'N/A')
            
            # Determina status geral
            status_geral = 'OK'
            if 'Timeout' in http_status and 'Timeout' in https_status:
                status_geral = 'Timeout'
            elif 'OK' not in http_status and 'OK' not in https_status:
                status_geral = 'Error'
            
            resultados_formatados.append({
                'ip': r['ip'],
                'http': http_status,
                'https': https_status,
                'status': status_geral
            })
        
        return jsonify({
            'sucesso': True,
            'total': len(resultados_formatados),
            'resultados': resultados_formatados
        })
        
    except Exception as e:
        logging.error(f"Erro no endpoint /api/testar: {str(e)}")
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
