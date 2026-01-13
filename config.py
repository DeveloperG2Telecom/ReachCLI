"""
Configurações do sistema de teste de conectividade HTTP/HTTPS
"""

# Configurações de conexão
PORTA_PADRAO = 8080
TIMEOUT_PADRAO = 5  # segundos

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
