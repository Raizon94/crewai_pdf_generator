# 📄 CrewAI PDF Generator - Configuración Docker

## 🎯 Descripción

Este proyecto genera documentos PDF utilizando CrewAI y LLMs a través de Ollama. La configuración Docker permite ejecutar la aplicación de manera consistente en diferentes sistemas operativos.

**Desarrollado por:** William Atef Tadrous y Julián Cussianovich  
**Asignatura:** AIN - Grupo 3CO11  
**Optimizado para:** gemma3:1b y gemma3:4b

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   CrewAI        │    │   Ollama        │
│   (Docker)      │◄──►│   (Docker)      │◄──►│   (Host)        │
│   Puerto 8501   │    │   Agentes AI    │    │   Puerto 11434  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Ventajas de esta arquitectura:**
- ✅ Ollama ejecutándose nativamente para mejor rendimiento de GPU
- ✅ Aplicación containerizada para consistencia multiplataforma
- ✅ Modelos persistentes entre reinicios
- ✅ Fácil distribución y despliegue

## 🚀 Instalación y Configuración

### 1. Prerrequisitos

#### Para todos los sistemas:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) instalado nativamente

#### Verificación de Docker:
```bash
docker --version
docker compose version
```

#### Verificación de Ollama:
```bash
ollama --version
ollama list
```

### 2. Configuración de Ollama

#### Instalar y ejecutar Ollama:
```bash
# Descargar e instalar desde https://ollama.com/

# Ejecutar el servicio
ollama serve

# Descargar los modelos recomendados
ollama pull gemma3:1b
ollama pull gemma3:4b
```

#### Verificar que funciona:
```bash
curl http://localhost:11434/api/tags
```

### 3. Configuración del proyecto

#### Clonar y configurar:
```bash
# Navegar al directorio del proyecto
cd /ruta/a/crewai_pdf_generator

# Crear archivo de configuración
cp .env.example .env
```

#### Editar `.env` con tus credenciales:
```bash
# Obtener API key gratuita en https://serper.dev/
SERPER_API_KEY=tu_clave_serper_aqui

# Configuración Ollama (ya está configurada para localhost)
OLLAMA_HOST=localhost:11434
```

## 🖥️ Ejecución

### Opción 1: Scripts automáticos

#### En macOS/Linux:
```bash
chmod +x run-docker.sh
./run-docker.sh
```

#### En Windows:
```cmd
run-docker.bat
```

### Opción 2: Comandos manuales

```bash
# Construir la imagen
docker compose build

# Ejecutar los servicios
docker compose up

# Para ejecutar en segundo plano
docker compose up -d
```

### Acceder a la aplicación:
🌐 **http://localhost:8501**

## 🛠️ Comandos útiles

### Gestión de contenedores:
```bash
# Ver logs en tiempo real
docker compose logs -f

# Parar los servicios
docker compose down

# Rebuild completo
docker compose down
docker compose build --no-cache
docker compose up
```

### Diagnóstico:
```bash
# Verificar que Ollama esté disponible desde Docker
docker run --rm curlimages/curl curl -f http://host.docker.internal:11434/api/tags

# Ver contenedores ejecutándose
docker compose ps

# Acceder al contenedor para debugging
docker compose exec crewai-app bash
```

## 🔧 Configuración avanzada

### Variables de entorno disponibles:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SERPER_API_KEY` | API key para búsquedas web | Requerido |
| `OLLAMA_HOST` | Host de Ollama | `localhost:11434` |
| `STREAMLIT_SERVER_PORT` | Puerto de Streamlit | `8501` |

### Para Linux con Docker:
```bash
# En .env, cambiar:
OLLAMA_HOST=172.17.0.1:11434
```

### Para ejecutar en puerto diferente:
```bash
# En docker-compose.yml, cambiar:
ports:
  - "3000:8501"  # Acceder en http://localhost:3000
```

## 📁 Estructura de archivos

```
├── app.py                 # Aplicación principal Streamlit
├── Dockerfile             # Imagen Docker de la aplicación
├── docker-compose.yml     # Orquestación de servicios
├── requirements.txt       # Dependencias Python
├── .env.example          # Plantilla de configuración
├── run-docker.sh         # Script de ejecución (Unix)
├── run-docker.bat        # Script de ejecución (Windows)
├── agents/               # Agentes CrewAI
├── flows/                # Flujos de trabajo
├── tools/                # Herramientas
├── utils/                # Utilidades
├── output/               # PDFs generados (persistente)
└── temp/                 # Archivos temporales
```

## 🚨 Solución de problemas

### Error: "No se encontraron modelos Ollama"
```bash
# Verificar que Ollama esté ejecutándose
ollama serve

# Verificar modelos instalados
ollama list

# Descargar modelo si no existe
ollama pull gemma3:4b
```

### Error: "Connection refused to localhost:11434"
```bash
# En Windows/Mac, verificar que Docker pueda acceder al host
ping host.docker.internal

# En Linux, cambiar en .env:
OLLAMA_HOST=172.17.0.1:11434
```

### Error: "SERPER_API_KEY not configured"
```bash
# Obtener API key gratuita en https://serper.dev/
# Editar .env con la clave obtenida
```

### La aplicación es muy lenta
- Usar `gemma3:1b` en lugar de `gemma3:4b` para mayor velocidad
- Verificar que tienes suficiente RAM disponible
- Cerrar otras aplicaciones que usen mucha memoria

## 📊 Monitoreo

### Ver uso de recursos:
```bash
# Docker stats
docker stats

# Logs de la aplicación
docker compose logs crewai-app

# Logs de Ollama (fuera de Docker)
ollama logs
```

## 🔄 Actualizaciones

### Actualizar la aplicación:
```bash
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up
```

### Actualizar Ollama:
```bash
# Descargar nueva versión desde https://ollama.com/
ollama --version
```

## 📞 Soporte

Para problemas específicos:
1. Verificar logs: `docker compose logs`
2. Probar Ollama directamente: `curl http://localhost:11434/api/tags`
3. Revisar la configuración en `.env`
4. Reiniciar servicios: `docker compose restart`

---

**¡Listo para generar PDFs con IA! 🚀**
