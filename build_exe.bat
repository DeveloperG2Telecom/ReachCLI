@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo Gerando executavel da aplicacao ReachCLI
echo ============================================================
echo.

REM Tenta encontrar Python
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :found_python
)

echo ERRO: Python nao encontrado!
echo.
echo Por favor, instale o Python ou adicione-o ao PATH do sistema.
echo.
echo Alternativamente, execute manualmente:
echo   python -m pip install pyinstaller
echo   python -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
pause
exit /b 1

:found_python
echo Python encontrado: !PYTHON_CMD!
echo.

REM Verifica se PyInstaller esta instalado
!PYTHON_CMD! -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    !PYTHON_CMD! -m pip install pyinstaller
    if errorlevel 1 (
        echo ERRO ao instalar PyInstaller!
        pause
        exit /b 1
    )
    echo.
)

echo Executando PyInstaller...
echo.

!PYTHON_CMD! -m PyInstaller --name=ReachCLI ^
    --onefile ^
    --windowed ^
    --add-data="services;services" ^
    --add-data="utils;utils" ^
    --add-data="config.py;." ^
    --hidden-import=services.http_tester ^
    --hidden-import=utils.file_reader ^
    --hidden-import=config ^
    app_desktop.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERRO ao gerar executavel!
    echo ============================================================
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Executavel gerado com sucesso!
echo ============================================================
echo.
echo Arquivo: dist\ReachCLI.exe
echo.
echo Voce pode copiar o arquivo ReachCLI.exe para qualquer computador Windows.
echo.
pause
