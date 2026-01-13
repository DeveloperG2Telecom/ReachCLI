"""
Sistema de Teste de Conectividade HTTP/HTTPS para Clientes IPv4
"""

import csv
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict

import config
from services.http_tester import HTTPTester
from utils.file_reader import ler_ips_do_arquivo


def configurar_logging():
    """Configura o sistema de logging"""
    nivel = getattr(logging, config.NIVEL_LOG.upper(), logging.INFO)
    
    logging.basicConfig(
        level=nivel,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def calcular_workers(numero_ips: int) -> int:
    """
    Calcula o número ideal de workers baseado no número de IPs.
    
    Args:
        numero_ips: Quantidade de IPs a serem testados
        
    Returns:
        Número de workers a serem utilizados
    """
    # Usa uma heurística: 1 worker para cada 5 IPs, com limites
    workers = max(config.MIN_WORKERS, min(numero_ips // 5, config.MAX_WORKERS))
    
    # Se houver poucos IPs, usa no máximo o número de IPs
    workers = min(workers, numero_ips, config.MAX_WORKERS)
    
    return max(workers, 1)  # Garante pelo menos 1 worker


def gerar_relatorio_csv(resultados: List[Dict], caminho_arquivo: str):
    """
    Gera relatório CSV com os resultados dos testes.
    
    Args:
        resultados: Lista de dicionários com resultados
        caminho_arquivo: Caminho para salvar o arquivo CSV
    """
    try:
        with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo:
            campos = ['IP', 'HTTP', 'HTTPS']
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            
            escritor.writeheader()
            
            for resultado in resultados:
                escritor.writerow({
                    'IP': resultado['ip'],
                    'HTTP': resultado['http'],
                    'HTTPS': resultado['https']
                })
        
        logging.info(f"Relatório CSV salvo em: {caminho_arquivo}")
        
    except Exception as e:
        logging.error(f"Erro ao gerar relatório CSV: {str(e)}")


def exibir_resultados_console(resultados: List[Dict]):
    """
    Exibe resultados no console de forma formatada.
    
    Args:
        resultados: Lista de dicionários com resultados
    """
    print("\n" + "="*70)
    print("RESULTADOS DOS TESTES DE CONECTIVIDADE")
    print("="*70)
    print(f"{'IP':<20} {'HTTP':<25} {'HTTPS':<25}")
    print("-"*70)
    
    for resultado in resultados:
        ip = resultado['ip']
        http = resultado['http'] or 'N/A'
        https = resultado['https'] or 'N/A'
        print(f"{ip:<20} {http:<25} {https:<25}")
    
    print("="*70)


def exibir_estatisticas(resultados: List[Dict]):
    """
    Exibe estatísticas dos testes realizados.
    
    Args:
        resultados: Lista de dicionários com resultados
    """
    total = len(resultados)
    
    # Conta resultados HTTP
    http_ok = sum(1 for r in resultados if r['http'] and 'OK' in r['http'])
    http_timeout = sum(1 for r in resultados if r['http'] == 'Timeout')
    http_recusado = sum(1 for r in resultados if r['http'] == 'Conexão recusada')
    
    # Conta resultados HTTPS
    https_ok = sum(1 for r in resultados if r['https'] and 'OK' in r['https'])
    https_timeout = sum(1 for r in resultados if r['https'] == 'Timeout')
    https_recusado = sum(1 for r in resultados if r['https'] == 'Conexão recusada')
    https_ssl_erro = sum(1 for r in resultados if r['https'] == 'Erro SSL')
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS")
    print("="*70)
    print(f"Total de IPs testados: {total}")
    print(f"\nHTTP:")
    print(f"  [OK] OK: {http_ok} ({http_ok*100/total:.1f}%)")
    print(f"  [TIMEOUT] Timeout: {http_timeout} ({http_timeout*100/total:.1f}%)")
    print(f"  [FALHA] Conexao recusada: {http_recusado} ({http_recusado*100/total:.1f}%)")
    print(f"\nHTTPS:")
    print(f"  [OK] OK: {https_ok} ({https_ok*100/total:.1f}%)")
    print(f"  [TIMEOUT] Timeout: {https_timeout} ({https_timeout*100/total:.1f}%)")
    print(f"  [FALHA] Conexao recusada: {https_recusado} ({https_recusado*100/total:.1f}%)")
    print(f"  [SSL] Erro SSL: {https_ssl_erro} ({https_ssl_erro*100/total:.1f}%)")
    print("="*70)


def main():
    """Função principal do programa"""
    configurar_logging()
    
    print("="*70)
    print("SISTEMA DE TESTE DE CONECTIVIDADE HTTP/HTTPS - IPv4")
    print("="*70)
    print(f"Arquivo de IPs: {config.ARQUIVO_IPS}")
    print(f"Porta: {config.PORTA_PADRAO}")
    print(f"Timeout: {config.TIMEOUT_PADRAO}s")
    print(f"Verificar SSL: {config.VERIFICAR_SSL}")
    print("="*70)
    
    # Lê IPs do arquivo
    try:
        logging.info(f"Lendo IPs do arquivo: {config.ARQUIVO_IPS}")
        ips = ler_ips_do_arquivo(config.ARQUIVO_IPS)
        
        if not ips:
            print("[ERRO] Nenhum IP valido encontrado no arquivo!")
            sys.exit(1)
        
        print(f"\n[OK] {len(ips)} IP(s) valido(s) encontrado(s)")
        
    except FileNotFoundError as e:
        logging.error(str(e))
        print(f"[ERRO] Erro: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro ao ler arquivo: {str(e)}")
        print(f"[ERRO] Erro: {str(e)}")
        sys.exit(1)
    
    # Calcula número de workers
    num_workers = calcular_workers(len(ips))
    print(f"[OK] Executando testes com {num_workers} worker(s) em paralelo")
    
    # Inicializa o testador
    testador = HTTPTester(
        porta=config.PORTA_PADRAO,
        timeout=config.TIMEOUT_PADRAO,
        verificar_ssl=config.VERIFICAR_SSL
    )
    
    # Executa testes em paralelo
    resultados = []
    inicio = datetime.now()
    
    print(f"\n[INICIANDO] Iniciando testes... ({inicio.strftime('%H:%M:%S')})")
    print("-"*70)
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submete todas as tarefas
        futures = {executor.submit(testador.testar_ip, ip): ip for ip in ips}
        
        # Processa resultados conforme completam
        for i, future in enumerate(as_completed(futures), 1):
            ip = futures[future]
            try:
                resultado = future.result()
                resultados.append(resultado)
                
                # Exibe progresso
                http_status = resultado['http'] or 'N/A'
                https_status = resultado['https'] or 'N/A'
                print(f"[{i}/{len(ips)}] {ip:<20} HTTP: {http_status:<20} HTTPS: {https_status}")
                
            except Exception as e:
                logging.error(f"Erro ao testar {ip}: {str(e)}")
                resultados.append({
                    'ip': ip,
                    'http': f'Erro: {str(e)}',
                    'https': f'Erro: {str(e)}'
                })
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print("-"*70)
    print(f"[OK] Testes concluidos em {duracao:.2f} segundos")
    
    # Ordena resultados por IP para facilitar leitura
    resultados.sort(key=lambda x: x['ip'])
    
    # Exibe resultados
    exibir_resultados_console(resultados)
    exibir_estatisticas(resultados)
    
    # Gera relatório CSV
    try:
        gerar_relatorio_csv(resultados, config.ARQUIVO_RESULTADOS)
        print(f"\n[OK] Relatorio salvo em: {config.ARQUIVO_RESULTADOS}")
    except Exception as e:
        logging.error(f"Erro ao gerar relatório: {str(e)}")
        print(f"[AVISO] Nao foi possivel salvar o relatorio CSV")
    
    print("\n[CONCLUIDO] Processo finalizado!")


if __name__ == "__main__":
    main()
