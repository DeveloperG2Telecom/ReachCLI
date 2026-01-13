"""
Script para gerar executável (.exe) da aplicação desktop
Execute: python build_exe.py
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """Instala PyInstaller se não estiver instalado"""
    try:
        import PyInstaller
        print("✓ PyInstaller já está instalado")
        return True
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✓ PyInstaller instalado com sucesso")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar PyInstaller")
            print("\nTente instalar manualmente:")
            print(f"  {sys.executable} -m pip install pyinstaller")
            return False

def build_executable():
    """Gera o executável usando PyInstaller"""
    
    print("="*60)
    print("Gerando executável da aplicação ReachCLI")
    print("="*60)
    print()
    
    # Verifica e instala PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    print()
    print("Executando PyInstaller...")
    print()
    
    # Comando PyInstaller usando sys.executable para garantir o Python correto
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=ReachCLI',
        '--onefile',
        '--windowed',  # Sem console (interface gráfica)
        '--add-data=services;services',  # Inclui diretório services
        '--add-data=utils;utils',  # Inclui diretório utils
        '--add-data=config.py;.',  # Inclui config.py
        '--hidden-import=services.http_tester',
        '--hidden-import=utils.file_reader',
        '--hidden-import=config',
        'app_desktop.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("="*60)
        print("✅ Executável gerado com sucesso!")
        print("="*60)
        print()
        print("Arquivo gerado em: dist/ReachCLI.exe")
        print()
        print("Você pode copiar o arquivo ReachCLI.exe para qualquer computador Windows.")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("="*60)
        print("❌ Erro ao gerar executável")
        print("="*60)
        print(f"\nCódigo de erro: {e.returncode}")
        print("\nVerifique se todos os arquivos estão presentes:")
        print("  - app_desktop.py")
        print("  - services/http_tester.py")
        print("  - utils/file_reader.py")
        print("  - config.py")
        sys.exit(1)
    except Exception as e:
        print()
        print("="*60)
        print("❌ Erro inesperado")
        print("="*60)
        print(f"\nErro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
