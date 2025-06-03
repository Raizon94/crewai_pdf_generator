# Generador de Documentos PDF con CrewAI y Streamlit

Esta aplicación web, construida con Streamlit, utiliza CrewAI y modelos de lenguaje locales (a través de Ollama) para generar documentos PDF detallados sobre un tema proporcionado por el usuario.

## Requisitos Previos e Instalación

1. **Python:** Asegúrate de tener Python 3.9 o superior instalado.
2. **Clona o descarga el repositorio.**
3. **Instala las dependencias:**  
   Abre una terminal en la carpeta raíz del proyecto y ejecuta:
   ```bash
   pip install -r requirements.txt
   ```
   Las principales dependencias son:
   - `crewai` (0.118.0)
   - `crewai-tools` (0.42.2)
   - `ollama` (0.5.1)
   - `streamlit` (1.45.1)
   - `requests` (2.32.3)
   - `markdown` (3.8)
   - `weasyprint` (65.1)
   - `google-search-results` (2.4.2)
   - `python-dotenv` (para cargar variables de entorno)

   El archivo `requirements.txt` puede incluir extras como `crewai[llm]`, `crewai[tools]` y `crewai[integrations]` para asegurar la funcionalidad completa.

4. **Configura Ollama:**
   - Descarga e instala Ollama desde [ollama.com](https://ollama.com/).
   - Descarga el modelo recomendado ejecutando:
     ```bash
     ollama pull gemma3:4b
     ```
     También puedes usar `gemma3:1b` como alternativa.
   - Asegúrate de que Ollama esté ejecutándose en `http://localhost:11434`.

5. **Configura la API Key de Serper:**
   - Regístrate en [Serper](https://serper.dev) y obtén una API key.
   - Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
     ```
     SERPER_API_KEY="tu_clave_de_api_aqui"
     ```
   - Reemplaza `"tu_clave_de_api_aqui"` por tu clave real.

## Cómo Ejecutar la Aplicación

1. Navega a la carpeta raíz del proyecto en tu terminal.
2. Ejecuta:
   ```bash
   streamlit run app.py
   ```
3. Abre tu navegador en la URL que indique Streamlit (usualmente `http://localhost:8501`).

## Funcionalidades Principales

- **Interfaz Web Intuitiva:** Construida con Streamlit.
- **Selección de Modelos LLM:** El usuario puede elegir entre los modelos disponibles en Ollama.
- **Generación Automatizada de Contenido:** CrewAI orquesta agentes para investigar, estructurar y redactar el documento.
- **Exportación a PDF:** El documento final se convierte y descarga como PDF.
- **Optimizado para `gemma3:4b`:** Se recomienda este modelo para mejores resultados.

## Autores

Desarrollado por **William Atef Tadrous** y **Julián Cussianovich** para la asignatura **AIN** (Grupo: 3CO11).

## Tecnologías Utilizadas

- **Python**
- **Streamlit:** Interfaz web.
- **CrewAI:** Orquestación de agentes de IA.
- **Ollama:** Ejecución local de LLMs.
- **Langchain:** Integración de cadenas de LLM (usado por CrewAI).

## Estructura del Proyecto

- `app.py`: Script principal de la aplicación Streamlit.
- `README.md`: Documentación del proyecto.
- `requirements.txt`: Dependencias de Python.
- `agents/`: Define los agentes de CrewAI:
  - `buscador.py`: Agente "Investigador Digital Especializado" (búsqueda web) y "Buscador de Imágenes Especializado" (búsqueda y descarga de imágenes).
  - `escritor.py`: Agente "Redactor Técnico Especializado en Español" (redacción y guardado de contenido).
  - `estructurador.py`: Agente "Arquitecto de Documentos Técnicos" (estructura inicial del documento).
- `flows/`:
  - `documento_flow.py`: Orquesta el flujo de generación del documento, gestionando la secuencia de tareas entre los agentes.
- `output/`: Carpeta donde se guardan los PDFs generados.
- `temp/`: Carpeta para archivos temporales (ej. `temp_markdown.md`).
- `tools/`: Herramientas personalizadas para los agentes:
  - `file_tools.py`: Herramientas para manipulación de archivos, como `append_to_markdown`.
  - `pdf_tool.py`: Conversión de Markdown a PDF.
  - `search_tools.py`: Herramientas de búsqueda web e imágenes.
- `utils/`: Utilidades varias:
  - `fix_encoding.py`: Corrige problemas de codificación en el Markdown.
  - `llm_provider.py`: Configura la instancia del LLM para CrewAI.
  - `llm_selector.py`: Detecta y lista los modelos LLM disponibles en Ollama.

## Descripción de los Agentes

### Agente Estructurador (`estructurador.py`)
- **Rol:** Arquitecto de Documentos Técnicos.
- **Función:** Crea una estructura lógica y profesional en Markdown para el documento.

### Agente Buscador (`buscador.py`)
- **Investigador Digital Especializado:** Busca información técnica relevante usando la herramienta `buscar_web`.
- **Buscador de Imágenes Especializado:** Busca y descarga una imagen relevante usando `buscar_y_descargar_imagen`.

### Agente Escritor (`escritor.py`)
- **Rol:** Redactor Técnico Especializado en Español.
- **Función:** Redacta contenido profesional en español para cada sección y lo añade al Markdown usando `append_to_markdown`.

## Flujo de Trabajo (`flows/documento_flow.py`)

El flujo principal sigue estos pasos:

1. **Limpieza y Estructuración:** Limpia la carpeta temporal y genera la estructura del documento.
2. **Procesamiento de Secciones:** Para cada sección, el agente buscador investiga y el agente escritor redacta el contenido.
3. **Búsqueda de Imagen de Portada:** Descarga una imagen relevante para el tema.
4. **Compilación del PDF:** Convierte el Markdown final a PDF, incluyendo la imagen de portada.
5. **Organización Final:** Mueve el PDF a la carpeta `output/` y muestra estadísticas del proceso.

El estado del flujo se gestiona con la clase `DocumentoState`, que almacena información como el tema, la estructura, las secciones, la imagen de portada y la ruta del PDF final.

## Herramientas Personalizadas (`tools/`)

- **`append_to_markdown(content: str)`:** Añade contenido al final del archivo Markdown temporal.
- **`generar_pdf_desde_markdown(markdown_content: str, imagen_portada: str, output_pdf_path: str)`:** Convierte Markdown a PDF, incluyendo una portada con imagen.
- **`buscar_web(query: str)`:** Realiza búsquedas web usando la API de Serper.
- **`buscar_y_descargar_imagen(topic: str)`:** Busca y descarga una imagen relevante usando la API de Serper.

## Utilidades (`utils/`)

- **`fix_markdown_encoding()`:** Corrige problemas de codificación en el archivo Markdown.
- **`crear_llm_crewai(modelo_seleccionado=None)`:** Configura el LLM para CrewAI usando Ollama.
- **`obtener_modelos_disponibles_ollama()`:** Lista los modelos LLM instalados en Ollama.
- **`seleccionar_llm()`:** Selecciona el modelo LLM a utilizar, priorizando `gemma3:4b`.
