@echo off
REM Script para ejecutar la aplicación con Docker en Windows
REM Uso: run-docker.bat

echo 🚀 Iniciando CrewAI PDF Generator con Docker...

REM Verificar que Docker esté instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está instalado. Por favor instala Docker Desktop primero.
    pause
    exit /b 1
)

REM Verificar que Docker Compose esté disponible
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose no está disponible. Por favor instala Docker Compose.
    pause
    exit /b 1
)

REM Crear archivo .env si no existe
if not exist .env (
    echo 📝 Creando archivo .env desde .env.example...
    copy .env.example .env
    echo ⚠️  Por favor edita el archivo .env con tus credenciales antes de continuar.
    echo    Especialmente necesitas configurar SERPER_API_KEY.
    set /p continuar="¿Continuar de todos modos? (y/N): "
    if /i not "%continuar%"=="y" exit /b 1
)

REM Crear directorios necesarios
if not exist output mkdir output
if not exist temp mkdir temp

echo 🔧 Construyendo la imagen Docker...
docker compose build

echo 🔍 Verificando conexión con Ollama...
curl -f http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama está ejecutándose y disponible
) else (
    echo ⚠️  Ollama no parece estar ejecutándose en localhost:11434
    echo    Por favor asegúrate de tener Ollama instalado y ejecutándose:
    echo    - Instalar: https://ollama.com/
    echo    - Ejecutar: ollama serve
    echo    - Descargar modelo: ollama pull gemma3:4b
    set /p continuar="¿Continuar de todos modos? (y/N): "
    if /i not "%continuar%"=="y" exit /b 1
)

echo 🚀 Iniciando los servicios...
docker compose up

echo 🌐 La aplicación estará disponible en: http://localhost:8501
pause
