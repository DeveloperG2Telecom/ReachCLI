"""
Configurações do sistema de teste de conectividade HTTP/HTTPS
"""

# Configurações de conexão
PORTA_PADRAO = 2265
TIMEOUT_PADRAO = 3  # segundos
# Portas padrão para teste (HTTP e HTTPS em cada porta)
PORTAS_PADRAO = [2265, 8080, 8888, 8443, 443, 80, 8530]

# Configurações de paralelismo
MAX_WORKERS_PADRAO = 20
MIN_WORKERS = 10
MAX_WORKERS = 50

# Arquivos
ARQUIVO_IPS = "ips.txt"
ARQUIVO_RESULTADOS = "results.csv"

# Configurações SSL
VERIFICAR_SSL = False  # Desabilitado para CPEs sem certificado válido

# Logging
NIVEL_LOG = "INFO"  # DEBUG, INFO, WARNING, ERROR
