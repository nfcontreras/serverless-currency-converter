#!/usr/bin/env python3
"""
Script para configurar y levantar el ambiente de desarrollo local.
Instala dependencias y configura el proyecto para desarrollo.
"""

import os
import sys
import subprocess
import json
import platform

def run_command(command, cwd=None, shell=True):
    """Ejecuta un comando y maneja errores."""
    try:
        print(f"🔄 Ejecutando: {command}")
        result = subprocess.run(
            command, 
            shell=shell, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Verifica que estén instalados los requisitos previos."""
    requirements = {
        "python": ["python", "--version"],
        "pip": ["pip", "--version"], 
        "node": ["node", "--version"],
        "npm": ["npm", "--version"]
    }
    
    missing = []
    for name, cmd in requirements.items():
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"✅ {name} está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {name} NO está instalado")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Faltan requisitos: {', '.join(missing)}")
        print("\nInstala los siguientes:")
        if "node" in missing or "npm" in missing:
            print("- Node.js: https://nodejs.org/")
        if "python" in missing:
            print("- Python 3.12+: https://python.org/")
        return False
    
    return True

def setup_python_env():
    """Configura el entorno Python."""
    print("\n🐍 Configurando entorno Python...")
    
    # Instalar dependencias Python
    if not run_command(["pip", "install", "-r", "requirements.txt"]):
        print("❌ Error instalando dependencias Python")
        return False
    
    # Instalar boto3 para DynamoDB local
    if not run_command(["pip", "install", "boto3"]):
        print("❌ Error instalando boto3")
        return False
        
    print("✅ Entorno Python configurado")
    return True

def setup_node_env():
    """Configura el entorno Node.js."""
    print("\n📦 Configurando entorno Node.js...")
    
    # Instalar serverless globalmente si no está
    try:
        subprocess.run(["serverless", "--version"], capture_output=True, check=True)
        print("✅ Serverless ya está instalado")
    except:
        print("🔄 Instalando Serverless Framework...")
        if not run_command(["npm", "install", "-g", "serverless"]):
            print("❌ Error instalando Serverless")
            return False
    
    # Instalar dependencias del proyecto
    if not run_command(["npm", "install"]):
        print("❌ Error instalando dependencias Node.js")
        return False
        
    print("✅ Entorno Node.js configurado")
    return True

def create_env_file():
    """Crea archivo de variables de entorno para desarrollo local."""
    print("\n📄 Creando archivo .env para desarrollo local...")
    
    env_content = """# Variables de entorno para desarrollo local
IS_OFFLINE=true
EXCHANGE_API_BASE=https://open.er-api.com/v6/latest
EXCHANGE_API_TIMEOUT=5
DYNAMODB_ENDPOINT=http://localhost:8000

# Variables de AWS para DynamoDB local
AWS_ACCESS_KEY_ID=fake
AWS_SECRET_ACCESS_KEY=fake
AWS_DEFAULT_REGION=us-east-1
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado")

def create_dev_scripts():
    """Crea scripts de desarrollo."""
    print("\n📜 Creando scripts de desarrollo...")
    
    # Script para Windows
    start_dev_bat = """@echo off
echo 🚀 Iniciando servidor de desarrollo...
echo.
echo 📍 Endpoints disponibles:
echo   - http://localhost:3000/dev/convert       (POST)
echo   - http://localhost:3000/dev/rates         (GET)  
echo   - http://localhost:3000/dev/history       (GET/POST)
echo   - http://localhost:3000/dev/history/{id}  (GET/PUT/DELETE)
echo.
echo 💡 Para probar la API:
echo   - Usa Postman, curl o el script test_api_client.py
echo   - DynamoDB local corre en puerto 8000
echo.
echo 🛑 Para detener: Ctrl+C
echo.

rem Configurar variables de entorno
set IS_OFFLINE=true
set DYNAMODB_ENDPOINT=http://localhost:8000

rem Iniciar servidor
npm run dev
"""
    
    with open("start-dev.bat", "w") as f:
        f.write(start_dev_bat)
    
    # Script para Linux/Mac
    start_dev_sh = """#!/bin/bash
echo "🚀 Iniciando servidor de desarrollo..."
echo ""
echo "📍 Endpoints disponibles:"
echo "  - http://localhost:3000/dev/convert       (POST)"
echo "  - http://localhost:3000/dev/rates         (GET)"
echo "  - http://localhost:3000/dev/history       (GET/POST)"
echo "  - http://localhost:3000/dev/history/{id}  (GET/PUT/DELETE)"
echo ""
echo "💡 Para probar la API:"
echo "  - Usa Postman, curl o el script test_api_client.py"
echo "  - DynamoDB local corre en puerto 8000"
echo ""
echo "🛑 Para detener: Ctrl+C"
echo ""

# Configurar variables de entorno
export IS_OFFLINE=true
export DYNAMODB_ENDPOINT=http://localhost:8000

# Iniciar servidor
npm run dev
"""
    
    with open("start-dev.sh", "w") as f:
        f.write(start_dev_sh)
    
    # Hacer ejecutable en sistemas Unix
    if platform.system() != "Windows":
        os.chmod("start-dev.sh", 0o755)
    
    print("✅ Scripts de desarrollo creados")

def update_test_client():
    """Actualiza el cliente de pruebas para desarrollo local."""
    print("\n🧪 Configurando cliente de pruebas para desarrollo local...")
    
    # Leer el archivo actual
    with open("test_api_client.py", "r") as f:
        content = f.read()
    
    # Reemplazar la URL por la URL local
    content = content.replace(
        'BASE_URL = "https://tu-api-gateway-url.amazonaws.com/dev"',
        'BASE_URL = "http://localhost:3000/dev"'
    )
    
    # Escribir el archivo actualizado
    with open("test_api_client_local.py", "w") as f:
        f.write(content)
    
    print("✅ Cliente de pruebas local creado: test_api_client_local.py")

def main():
    """Función principal."""
    print("🚀 Configurador de Ambiente Local - Currency Converter")
    print("=" * 55)
    
    # Verificar requisitos
    if not check_requirements():
        sys.exit(1)
    
    # Configurar entornos
    if not setup_python_env():
        sys.exit(1)
    
    if not setup_node_env():
        sys.exit(1)
    
    # Crear archivos de configuración
    create_env_file()
    create_dev_scripts()
    update_test_client()
    
    print("\n🎉 ¡Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Para iniciar el servidor de desarrollo:")
    
    if platform.system() == "Windows":
        print("   > start-dev.bat")
    else:
        print("   > ./start-dev.sh")
        print("   o")
        print("   > npm run dev")
    
    print("\n2. Para probar la API:")
    print("   > python test_api_client_local.py")
    
    print("\n3. Endpoints disponibles en:")
    print("   http://localhost:3000/dev/")
    
    print("\n4. DynamoDB local en:")
    print("   http://localhost:8000/")
    
    print("\n💡 Consejos:")
    print("- El servidor incluye datos de prueba en DynamoDB local")
    print("- Los cambios en el código se reflejan automáticamente")
    print("- Los logs aparecen en la terminal")
    print("- No afecta nada en AWS/producción")

if __name__ == "__main__":
    main()