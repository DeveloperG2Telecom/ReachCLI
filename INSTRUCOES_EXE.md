# Como Gerar o Executável (.exe)

## Método 1: Script Automatizado (Recomendado)

Execute no PowerShell ou CMD:
```bash
build_exe.bat
```

## Método 2: Script Simplificado

Se o método 1 não funcionar:
```bash
gerar_exe.bat
```

## Método 3: Manual (Se os scripts não funcionarem)

### Passo 1: Instalar PyInstaller
```bash
python -m pip install pyinstaller
```

### Passo 2: Gerar o Executável
```bash
python -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
```

## Método 4: Usando py launcher (Windows)

Se `python` não funcionar, tente `py`:
```bash
py -m pip install pyinstaller
py -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
```

## Localização do Executável

Após a compilação bem-sucedida, o arquivo estará em:
```
dist/ReachCLI.exe
```

## Solução de Problemas

### "Python não foi encontrado"
- Certifique-se de que o Python está instalado
- Adicione o Python ao PATH do sistema
- Ou use o launcher `py` do Windows

### "PyInstaller não é reconhecido"
- Use `python -m PyInstaller` em vez de apenas `pyinstaller`
- Ou instale: `python -m pip install pyinstaller`

### Erro ao compilar
- Verifique se todos os arquivos estão presentes:
  - `app_desktop.py`
  - `services/http_tester.py`
  - `utils/file_reader.py`
  - `config.py`

## Testando o Executável

Após gerar, teste executando:
```bash
dist\ReachCLI.exe
```

O executável pode ser copiado para qualquer computador Windows sem necessidade de instalar Python ou dependências.
