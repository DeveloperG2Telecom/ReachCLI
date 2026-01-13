"""
Serviço de teste de conectividade HTTP/HTTPS
"""

import requests
import ssl
from typing import Dict, Optional
from urllib3.exceptions import InsecureRequestWarning

# Suprime avisos de SSL não verificado
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class HTTPTester:
    """Classe responsável por testar conectividade HTTP/HTTPS em IPs"""
    
    def __init__(self, porta: int = 8080, timeout: int = 5, verificar_ssl: bool = False):
        """
        Inicializa o testador HTTP.
        
        Args:
            porta: Porta de destino para os testes
            timeout: Timeout em segundos para as requisições
            verificar_ssl: Se deve verificar certificados SSL
        """
        self.porta = porta
        self.timeout = timeout
        self.verificar_ssl = verificar_ssl
    
    def testar_ip(self, ip: str) -> Dict[str, str]:
        """
        Testa conectividade HTTP e HTTPS para um IP específico.
        
        Args:
            ip: Endereço IPv4 a ser testado
            
        Returns:
            Dicionário com resultados dos testes HTTP e HTTPS
            Formato: {'http': 'resultado', 'https': 'resultado'}
        """
        resultados = {
            'ip': ip,
            'http': None,
            'https': None
        }
        
        # Testa HTTP
        resultados['http'] = self._testar_protocolo(ip, 'http')
        
        # Testa HTTPS
        resultados['https'] = self._testar_protocolo(ip, 'https')
        
        return resultados
    
    def _testar_protocolo(self, ip: str, protocolo: str) -> str:
        """
        Testa um protocolo específico (HTTP ou HTTPS) para um IP.
        
        Args:
            ip: Endereço IPv4
            protocolo: 'http' ou 'https'
            
        Returns:
            String descrevendo o resultado do teste
        """
        url = f"{protocolo}://{ip}:{self.porta}"
        
        try:
            resposta = requests.get(
                url,
                timeout=self.timeout,
                verify=self.verificar_ssl,
                allow_redirects=False
            )
            
            # Sucesso - retorna código HTTP
            return f"OK ({resposta.status_code})"
            
        except requests.exceptions.ConnectTimeout:
            return "Timeout"
            
        except requests.exceptions.ConnectionError as e:
            # Tenta identificar o tipo específico de erro de conexão
            erro_str = str(e).lower()
            if 'refused' in erro_str or 'connection refused' in erro_str:
                return "Conexão recusada"
            elif 'timed out' in erro_str or 'timeout' in erro_str:
                return "Timeout"
            else:
                return "Erro de conexão"
            
        except requests.exceptions.SSLError:
            return "Erro SSL"
            
        except requests.exceptions.Timeout:
            return "Timeout"
            
        except requests.exceptions.TooManyRedirects:
            return "Muitos redirecionamentos"
            
        except Exception as e:
            # Captura outros erros genéricos
            tipo_erro = type(e).__name__
            return f"Erro: {tipo_erro}"
    
    def testar_multiplos_ips(self, ips: list) -> list:
        """
        Testa múltiplos IPs (método auxiliar para uso sequencial).
        Para execução paralela, use testar_ip() com ThreadPoolExecutor.
        
        Args:
            ips: Lista de endereços IPv4
            
        Returns:
            Lista de dicionários com resultados
        """
        resultados = []
        for ip in ips:
            resultado = self.testar_ip(ip)
            resultados.append(resultado)
        return resultados
