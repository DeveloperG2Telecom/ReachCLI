@echo off
REM Script simplificado para gerar executavel
REM Use este se o build_exe.bat nao funcionar

echo ============================================================
echo Gerando executavel - Metodo Simplificado
echo ============================================================
echo.
echo Instalando PyInstaller (se necessario)...
python -m pip install pyinstaller
echo.
echo Gerando executavel...
echo.

python -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py

if errorlevel 1 (
    echo.
    echo ERRO! Tente executar manualmente:
    echo.
    echo python -m pip install pyinstaller
    echo python -m PyInstaller --name=ReachCLI --onefile --windowed --add-data="services;services" --add-data="utils;utils" --add-data="config.py;." --hidden-import=services.http_tester --hidden-import=utils.file_reader --hidden-import=config app_desktop.py
) else (
    echo.
    echo ============================================================
    echo SUCESSO! Executavel gerado em: dist\ReachCLI.exe
    echo ============================================================
)

pause
