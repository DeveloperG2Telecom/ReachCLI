"""
Utilitário para leitura e validação de arquivos de IPs
"""

import re
from typing import List


def validar_ipv4(ip: str) -> bool:
    """
    Valida se uma string é um endereço IPv4 válido.
    
    Args:
        ip: String contendo o endereço IP
        
    Returns:
        True se o IP é válido, False caso contrário
    """
    padrao_ipv4 = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if not re.match(padrao_ipv4, ip):
        return False
    
    partes = ip.split('.')
    for parte in partes:
        try:
            numero = int(parte)
            if numero < 0 or numero > 255:
                return False
        except ValueError:
            return False
    
    return True


def ler_ips_do_arquivo(caminho_arquivo: str) -> List[str]:
    """
    Lê endereços IPv4 de um arquivo de texto.
    
    Args:
        caminho_arquivo: Caminho para o arquivo contendo os IPs
        
    Returns:
        Lista de IPs válidos encontrados no arquivo
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
    """
    ips_validos = []
    ips_invalidos = []
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            for numero_linha, linha in enumerate(arquivo, start=1):
                # Remove espaços em branco e quebras de linha
                ip = linha.strip()
                
                # Ignora linhas vazias e comentários
                if not ip or ip.startswith('#'):
                    continue
                
                # Valida o IP
                if validar_ipv4(ip):
                    ips_validos.append(ip)
                else:
                    ips_invalidos.append((numero_linha, ip))
        
        # Avisa sobre IPs inválidos
        if ips_invalidos:
            print(f"[AVISO] {len(ips_invalidos)} IP(s) invalido(s) encontrado(s) e ignorado(s)")
            for linha, ip in ips_invalidos:
                print(f"   Linha {linha}: {ip}")
        
        return ips_validos
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo {caminho_arquivo}: {str(e)}")
