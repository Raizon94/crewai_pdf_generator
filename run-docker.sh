#!/bin/bash

# Script para ejecutar la aplicación con Docker
# Uso: ./run-docker.sh

echo "🚀 Iniciando CrewAI PDF Generator con Docker..."

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar que Docker Compose esté disponible
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose no está disponible. Por favor instala Docker Compose."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "⚠️  Por favor edita el archivo .env con tus credenciales antes de continuar."
    echo "   Necesitas configurar:"
    echo "   - SERPER_API_KEY (para búsquedas web)"
    echo "   - GEMINI_API_KEY (para el modelo de IA)"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Crear directorios necesarios
mkdir -p output temp

echo "🔧 Construyendo la imagen Docker..."
docker compose build

echo "🚀 Iniciando los servicios..."
docker compose up

echo "🌐 La aplicación estará disponible en: http://localhost:8501"
