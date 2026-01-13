# Interface Web - Teste de Conectividade HTTP/HTTPS

Interface web moderna e visualmente agradável para testar conectividade HTTP/HTTPS em múltiplos IPs IPv4.

## 🚀 Como Executar

1. **Instale as dependências** (se ainda não instalou):
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicie o servidor Flask**:
   ```bash
   python app.py
   ```

3. **Acesse no navegador**:
   ```
   http://localhost:5000
   ```

## ✨ Funcionalidades

- ✅ **Interface moderna e responsiva** com design gradiente
- ✅ **Campo de texto** para inserir múltiplos IPs (um por linha)
- ✅ **Configurações ajustáveis**: Porta, Timeout, Verificação SSL
- ✅ **Tabela de resultados** com status colorido:
  - 🟢 **OK** (verde) - Conexão bem-sucedida
  - 🟡 **Timeout** (amarelo) - Requisição expirou
  - 🔴 **Error** (vermelho) - Erro de conexão
- ✅ **Estatísticas em tempo real** com percentuais
- ✅ **Exportação para CSV** com um clique
- ✅ **Execução paralela** otimizada
- ✅ **Feedback visual** durante os testes (loading spinner)

## 📋 Como Usar

1. **Digite os IPs** no campo de texto (um por linha):
   ```
   187.10.10.1
   200.150.30.5
   179.40.22.9
   ```

2. **Ajuste as configurações** (opcional):
   - Porta de destino (padrão: 8080)
   - Timeout em segundos (padrão: 5)
   - Verificar SSL (desmarcado por padrão)

3. **Clique em "Executar Testes"**

4. **Visualize os resultados** na tabela:
   - Status HTTP e HTTPS para cada IP
   - Status geral (OK, Error, Timeout)
   - Estatísticas resumidas

5. **Exporte os resultados** clicando em "Exportar CSV" (opcional)

## 🎨 Características Visuais

- Design moderno com gradiente roxo/azul
- Cards com sombras e bordas arredondadas
- Badges coloridos para status
- Tabela responsiva com hover effects
- Animações suaves
- Layout adaptável para mobile

## 🔧 Tecnologias

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Testes**: Mesma lógica do sistema CLI (services/http_tester.py)

## 📝 Notas

- A interface usa a mesma lógica de testes do sistema CLI
- Os testes são executados em paralelo para melhor performance
- O servidor roda em modo debug por padrão (desative em produção)
- Acessível em `http://0.0.0.0:5000` (todas as interfaces de rede)
