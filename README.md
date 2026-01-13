# Sistema de Teste de Conectividade HTTP/HTTPS - IPv4

Sistema automatizado para testar acesso remoto a múltiplos clientes IPv4, verificando se respondem a requisições HTTP e HTTPS em uma porta específica.

## 🎯 Objetivo

Identificar problemas de conectividade (firewall, CGNAT, bloqueios, ausência de IPv6, etc.) em clientes IPv4 através de testes HTTP/HTTPS.

## 📋 Requisitos

- Python 3.9 ou superior
- Bibliotecas Python (instaladas via `requirements.txt`)

## 🚀 Instalação

1. Clone ou baixe este projeto
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 📁 Estrutura do Projeto

```
projeto_ipv4_test/
│
├── main.py                 # Arquivo principal
├── config.py               # Configurações
├── ips.txt                 # Lista de IPs para teste
├── results.csv             # Relatório de resultados (gerado)
├── requirements.txt        # Dependências Python
│
├── services/
│   └── http_tester.py     # Lógica de teste HTTP/HTTPS
│
└── utils/
    └── file_reader.py     # Leitura e validação de IPs
```

## ⚙️ Configuração

Edite o arquivo `config.py` para ajustar:

- **PORTA_PADRAO**: Porta de destino (padrão: 8080)
- **TIMEOUT_PADRAO**: Timeout em segundos (padrão: 5)
- **MAX_WORKERS_PADRAO**: Número de threads paralelas (padrão: 20)
- **VERIFICAR_SSL**: Verificar certificados SSL (padrão: False)
- **ARQUIVO_IPS**: Nome do arquivo com IPs (padrão: ips.txt)
- **ARQUIVO_RESULTADOS**: Nome do arquivo de saída (padrão: results.csv)

## 📝 Preparação do Arquivo de IPs

Edite o arquivo `ips.txt` e adicione um IP por linha:

```
187.10.10.1
200.150.30.5
179.40.22.9
```

- Linhas vazias são ignoradas
- Linhas começando com `#` são comentários
- Apenas IPs IPv4 válidos são processados

## ▶️ Execução

Execute o programa:

```bash
python main.py
```

## 📊 Saída

O sistema gera:

1. **Console**: Resultados em tempo real e estatísticas
2. **CSV**: Arquivo `results.csv` com todos os resultados

### Formato do CSV

```csv
IP,HTTP,HTTPS
187.10.10.1,OK (200),Timeout
200.150.30.5,Timeout,Timeout
179.40.22.9,OK (403),Erro SSL
```

### Tipos de Resultado

- **OK (código)**: Requisição bem-sucedida (ex: OK (200))
- **Timeout**: Requisição expirou
- **Conexão recusada**: Porta fechada ou firewall bloqueando
- **Erro SSL**: Problema com certificado SSL
- **Erro de conexão**: Outros erros de rede

## 🔧 Funcionalidades

- ✅ Leitura de IPs de arquivo
- ✅ Validação de IPs IPv4
- ✅ Teste HTTP e HTTPS simultâneo
- ✅ Execução paralela (multithreading)
- ✅ Tratamento de erros específicos
- ✅ Relatório CSV
- ✅ Estatísticas detalhadas
- ✅ Logging configurável

## 📌 Pontos de Atenção (Ambiente ISP)

- Muitos CPEs não possuem certificado SSL válido (SSL verification desabilitado por padrão)
- CGNAT pode impedir acesso externo
- Firewall pode aceitar TCP e bloquear HTTP
- HTTP costuma ser mais confiável que ICMP (ping)
- Timeout curto evita lentidão em massa

## 🚧 Funcionalidades Futuras

- [ ] Interface CLI com argumentos
- [ ] Suporte a IPv6
- [ ] Relatórios avançados (HTML, JSON)
- [ ] Retry automático
- [ ] Teste de múltiplas portas
- [ ] Exportação para banco de dados

## 📄 Licença

Este projeto foi desenvolvido para uso interno em ambiente ISP.
