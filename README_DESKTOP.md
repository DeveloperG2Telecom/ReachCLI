# Aplicação Desktop - Teste de Conectividade HTTP/HTTPS

Interface desktop nativa para Windows com Tkinter. Não requer servidor web ou navegador.

## 🚀 Como Executar (Modo Desenvolvimento)

1. **Execute diretamente com Python**:
   ```bash
   python app_desktop.py
   ```

## 📦 Como Gerar o Executável (.exe)

### Opção 1: Usando o script batch (Windows)
```bash
build_exe.bat
```

### Opção 2: Usando Python
```bash
python build_exe.py
```

### Opção 3: Manualmente
```bash
# Instale o PyInstaller (se ainda não instalou)
pip install pyinstaller

# Gere o executável
pyinstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
```

O executável será gerado em: `dist/ReachCLI.exe`

## ✨ Funcionalidades

- ✅ **Interface desktop nativa** - Não precisa de navegador
- ✅ **Campo de texto** para inserir múltiplos IPs
- ✅ **Configurações ajustáveis**: Porta, Timeout, Verificação SSL
- ✅ **Tabela de resultados** com cores:
  - 🟢 **OK** (verde) - Conexão bem-sucedida
  - 🟡 **Timeout** (amarelo) - Requisição expirou
  - 🔴 **Error** (vermelho) - Erro de conexão
- ✅ **Estatísticas em tempo real** com percentuais
- ✅ **Exportação para CSV** com diálogo de salvamento
- ✅ **Execução paralela** otimizada
- ✅ **Barra de progresso** durante os testes

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

- Interface limpa e profissional
- Cores intuitivas para status
- Tabela com scroll
- Layout responsivo
- Barra de progresso animada

## 📝 Distribuição

O arquivo `ReachCLI.exe` pode ser copiado para qualquer computador Windows sem necessidade de instalar Python ou dependências.

**Nota**: O primeiro antivírus pode alertar sobre o executável gerado por PyInstaller. Isso é normal e pode ser ignorado (falso positivo). Se necessário, adicione uma exceção no antivírus.

## 🔧 Requisitos para Gerar o Executável

- Python 3.9+
- PyInstaller (`pip install pyinstaller`)
- Todas as dependências do `requirements.txt`

## 📦 Tamanho do Executável

O executável gerado terá aproximadamente 15-25 MB (inclui Python e todas as dependências).
