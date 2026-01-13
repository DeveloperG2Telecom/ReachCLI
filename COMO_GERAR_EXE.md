# 🚀 Como Gerar o Executável (.exe) - Guia Completo

## ⚠️ Problema: "Python não foi encontrado"

Se você está recebendo este erro, o Python não está no PATH do sistema. Siga uma das soluções abaixo:

---

## ✅ SOLUÇÃO 1: Usar o Script Python Diretamente (RECOMENDADO)

O script `build_exe.py` instala automaticamente o PyInstaller e usa o Python correto.

### No PowerShell:
```powershell
# Navegue até a pasta do projeto
cd "C:\Users\ORIGEM DIGITAL\Desktop\PROJETOS KALLEBE\ReachCLI"

# Execute o script Python
python build_exe.py
```

### Se `python` não funcionar, tente:
```powershell
py build_exe.py
```

### Ou encontre o Python manualmente:
```powershell
# Encontre onde o Python está instalado
Get-Command python | Select-Object -ExpandProperty Source
# Ou
where.exe python

# Depois use o caminho completo, por exemplo:
C:\Users\ORIGEM DIGITAL\AppData\Local\Python\pythoncore-3.14-64\python.exe build_exe.py
```

---

## ✅ SOLUÇÃO 2: Instalar PyInstaller Manualmente Primeiro

1. **Abra o PowerShell ou CMD como Administrador**

2. **Encontre o Python:**
   ```powershell
   # Tente estes comandos até um funcionar:
   python --version
   py --version
   python3 --version
   ```

3. **Instale o PyInstaller:**
   ```powershell
   # Use o comando que funcionou acima:
   python -m pip install pyinstaller
   # OU
   py -m pip install pyinstaller
   ```

4. **Gere o executável:**
   ```powershell
   python -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
   ```

---

## ✅ SOLUÇÃO 3: Adicionar Python ao PATH

1. **Encontre onde o Python está instalado:**
   - Procure por "Python" no Menu Iniciar
   - Ou verifique: `C:\Users\ORIGEM DIGITAL\AppData\Local\Programs\Python\`
   - Ou: `C:\Python3x\`

2. **Adicione ao PATH:**
   - Pressione `Win + R`, digite `sysdm.cpl` e Enter
   - Vá em "Avançado" → "Variáveis de Ambiente"
   - Em "Variáveis do sistema", encontre "Path" e clique em "Editar"
   - Clique em "Novo" e adicione o caminho do Python (ex: `C:\Python39\` e `C:\Python39\Scripts\`)
   - Clique em "OK" em todas as janelas
   - **Reinicie o PowerShell/CMD**

3. **Teste:**
   ```powershell
   python --version
   ```

4. **Execute o script:**
   ```powershell
   python build_exe.py
   ```

---

## ✅ SOLUÇÃO 4: Usar o Python do Cursor/VS Code

Se você está usando o Cursor ou VS Code:

1. **Abra o Terminal Integrado** (Ctrl + `)

2. **Execute:**
   ```bash
   python build_exe.py
   ```

O terminal integrado geralmente já tem o Python configurado.

---

## ✅ SOLUÇÃO 5: Comando Completo Manual

Copie e cole este comando completo no PowerShell (substitua `python` por `py` se necessário):

```powershell
python -m pip install pyinstaller && python -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
```

---

## 📍 Onde Está o Executável?

Após a compilação bem-sucedida, o arquivo estará em:
```
dist\ReachCLI.exe
```

---

## 🧪 Testar o Executável

Após gerar, teste executando:
```powershell
.\dist\ReachCLI.exe
```

Ou simplesmente dê duplo clique no arquivo `ReachCLI.exe` na pasta `dist`.

---

## ❓ Ainda Não Funciona?

1. **Verifique se o Python está instalado:**
   - Abra o PowerShell
   - Digite: `Get-Command python*`
   - Se não aparecer nada, o Python não está instalado ou não está no PATH

2. **Instale o Python:**
   - Baixe de: https://www.python.org/downloads/
   - **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação

3. **Use o IDLE do Python:**
   - Abra o IDLE (procure "IDLE" no Menu Iniciar)
   - No IDLE, vá em File → Open → abra `build_exe.py`
   - Pressione F5 para executar

---

## 📝 Notas Importantes

- O executável gerado terá aproximadamente **15-25 MB**
- Pode levar **2-5 minutos** para compilar
- O primeiro antivírus pode alertar (falso positivo comum com PyInstaller)
- O executável pode ser copiado para qualquer Windows sem instalar Python

---

## 🎯 Método Mais Simples (Se Nada Funcionar)

1. Abra o **IDLE do Python** (procure no Menu Iniciar)
2. No IDLE, vá em **File → Open**
3. Abra o arquivo `build_exe.py`
4. Pressione **F5** para executar

O IDLE sempre encontra o Python corretamente!
