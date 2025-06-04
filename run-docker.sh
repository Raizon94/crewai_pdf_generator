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
    echo "   Especialmente necesitas configurar SERPER_API_KEY."
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

echo "🔍 Verificando conexión con Ollama..."
if curl -f http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama está ejecutándose y disponible"
else
    echo "⚠️  Ollama no parece estar ejecutándose en localhost:11434"
    echo "   Por favor asegúrate de tener Ollama instalado y ejecutándose:"
    echo "   - Instalar: https://ollama.com/"
    echo "   - Ejecutar: ollama serve"
    echo "   - Descargar modelo: ollama pull gemma3:4b"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🚀 Iniciando los servicios..."
docker compose up

echo "🌐 La aplicación estará disponible en: http://localhost:8501"
