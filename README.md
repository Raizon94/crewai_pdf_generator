<!-- filepath: /Users/bilian/Desktop/proyecto_crewai/README.md -->
# Generador de Documentos PDF con CrewAI y Streamlit

Este proyecto es una aplicación web construida con Streamlit que utiliza el poder de CrewAI y modelos de lenguaje locales (a través de Ollama) para generar documentos PDF detallados sobre un tema proporcionado por el usuario.

## Requisitos Previos e Instalación

Antes de ejecutar la aplicación, asegúrate de tener Python instalado (preferiblemente 3.9 o superior) y luego instala las dependencias necesarias.

1.  **Clona el repositorio (si aplica) o descarga los archivos del proyecto.**
2.  **Instala las dependencias listadas en `requirements.txt`:**
    Abre una terminal en la carpeta raíz del proyecto y ejecuta:
    ```bash
    pip install -r requirements.txt
    ```
    Esto instalará las siguientes bibliotecas principales (las versiones pueden variar según tu entorno y el momento de la instalación, las que se muestran a continuación son las usadas en el entorno de desarrollo al momento de esta documentación):

    *   `crewai` (Versión usada: 0.118.0)
    *   `crewai-tools` (Versión usada: 0.42.2)
    *   `ollama` (Versión usada: 0.5.1)
    *   `streamlit` (Versión usada: 1.45.1)
    *   `requests` (Versión usada: 2.32.3)
    *   `Markdown` (Versión usada: 3.8) - Nota: `markdown` (minúscula) también podría estar en `requirements.txt`, refiriéndose a la misma o una dependencia.
    *   `weasyprint` (Versión usada: 65.1)
    *   `google-search-results` (Versión usada: 2.4.2) - Dependencia para la herramienta de búsqueda Serper.

    El archivo `requirements.txt` también puede incluir `crewai[llm]`, `crewai[tools]`, y `crewai[integrations]` para asegurar que se instalen todas las extras necesarias para el funcionamiento completo de CrewAI con LLMs locales y sus herramientas.

3.  **Configura Ollama:***

    **Nota:** Aunque el proyecto está optimizado para `gemma3:4b`, también se ha comprobado que `gemma3:1b` funciona muy bien e incluso, en muchas ocasiones, supera los resultados obtenidos con `gemma3:4b`. Por lo tanto, puedes utilizar con confianza `gemma3:1b` como alternativa.
    *   Asegúrate de tener Ollama instalado y ejecutándose en tu sistema. Puedes descargarlo desde [ollama.com](https://ollama.com/).
    *   Descarga al menos un modelo de lenguaje. **EL PROYECTO ESTÁ OPTIMIZADO Y UTILIZA PRINCIPALMENTE EL MODELO `gemma3:4b`**. Puedes usar otros, pero este es el recomendado. Para descargar `gemma3:4b`, ejecuta en tu terminal:
        ```bash
        ollama pull gemma3:4b
        ```
    *   Verifica que el servidor de Ollama esté accesible en `http://localhost:11434`.

5.  **API Key de Serper:**
    *   El proyecto utiliza una API key de [Serper](https://serper.dev) para la funcionalidad de búsqueda web.
    *   Crea un archivo llamado `.env` en la raíz del proyecto.
    *   Añade tu API key de Serper al archivo `.env` de la siguiente manera:
        ```
        SERPER_API_KEY="tu_clave_de_api_aqui"
        ```
    *   Reemplaza `"tu_clave_de_api_aqui"` con tu clave real. Si no tienes una, puedes registrarte en Serper para obtener una clave gratuita.
    *   Asegúrate de que el paquete `python-dotenv` esté listado en tu `requirements.txt` y se instale (se añadirá si no está).

## Cómo Ejecutar la Aplicación

Una vez instaladas las dependencias y configurado Ollama:

1.  Navega a la carpeta raíz del proyecto en tu terminal.
2.  Ejecuta la aplicación Streamlit con el siguiente comando:
    ```bash
    streamlit run app.py
    ```
3.  Abre tu navegador web y ve a la dirección URL que Streamlit indique (usualmente `http://localhost:8501`).

## Funcionalidades Principales

*   **Interfaz Web Sencilla:** Interfaz de usuario intuitiva creada con Streamlit para una fácil interacción.
*   **Selección de Modelos LLM:** Permite al usuario seleccionar entre los modelos LLM disponibles en su instancia local de Ollama.
*   **Generación Automatizada de Contenido:** Utiliza un flujo de agentes de CrewAI para investigar, estructurar y redactar el contenido del documento.
*   **Exportación a PDF:** El documento final generado se convierte y se ofrece como un archivo PDF descargable.
*   **Optimizado para `gemma3:4b`:** **UTILIZA PRINCIPALMENTE EL MODELO `gemma3:4b`**. Aunque compatible con otros modelos, se recomienda `gemma3:4b` para obtener los mejores resultados.

## Autores y Contexto

Este trabajo fue realizado por **William Atef Tadrous** y **Julián Cussianovich** para la asignatura **AIN** (Grupo: **3CO11**).

## Tecnologías Utilizadas

*   **Python**
*   **Streamlit:** Para la interfaz de usuario web.
*   **CrewAI:** Para la orquestación de agentes de IA.
*   **Ollama:** Para la ejecución local de modelos de lenguaje grandes (LLMs).
*   **Langchain:** (Implícito por CrewAI) Para componentes de la cadena de LLM.

A continuación, procederé a analizar el resto de los archivos para documentar la estructura del proyecto y los detalles de cada componente.

## Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas y archivos principales:

*   `app.py`: Script principal de la aplicación Streamlit. Gestiona la interfaz de usuario, la selección del modelo LLM y el flujo de generación de documentos.
*   `README.md`: Este mismo archivo, con la documentación del proyecto.
*   `requirements.txt`: Lista las dependencias de Python necesarias para ejecutar el proyecto.
*   `agents/`: Contiene los scripts que definen los diferentes agentes de CrewAI.
    *   `buscador.py`: Define al agente "Investigador Digital Especializado", responsable de buscar información en la web utilizando la herramienta `buscar_web`, y al agente "Buscador de Imágenes Especializado" que utiliza `buscar_y_descargar_imagen`.
    *   `escritor.py`: Define al agente "Redactor Técnico Especializado en Español", encargado de redactar el contenido de cada sección del documento y guardarlo usando la herramienta `append_to_markdown`. Se enfoca en la calidad del contenido y la correcta codificación UTF-8.
    *   `estructurador.py`: Define al agente "Arquitecto de Documentos Técnicos", responsable de crear la estructura inicial del documento en formato Markdown.
*   `flows/`: Contiene los scripts que definen los flujos de trabajo (pipelines) de CrewAI.
    *   `documento_flow.py`: Orquesta la secuencia de tareas entre los diferentes agentes (estructurador, buscador, escritor) para generar el documento completo.
*   `output/`: Carpeta donde se guardan los documentos PDF generados.
*   `temp/`: Carpeta utilizada para almacenar archivos temporales, como el `temp_markdown.md` durante el proceso de generación.
*   `tools/`: Contiene herramientas personalizadas que los agentes pueden utilizar.
    *   `file_tools.py`: Probablemente contenga herramientas para la manipulación de archivos, como `append_to_markdown`.
    *   `pdf_tool.py`: Seguramente incluye la funcionalidad para convertir el archivo Markdown final a PDF.
    *   `search_tools.py`: Contiene las herramientas de búsqueda web (`buscar_web`) y búsqueda de imágenes (`buscar_y_descargar_imagen`).
*   `utils/`: Contiene scripts de utilidad.
    *   `fix_encoding.py`: Posiblemente para corregir problemas de codificación de caracteres.
    *   `llm_provider.py`: Gestiona la creación y configuración de la instancia del LLM para CrewAI a partir de los modelos de Ollama.
    *   `llm_selector.py`: Proporciona la lógica para detectar y listar los modelos LLM disponibles en la instancia local de Ollama.

## Descripción de los Agentes (Carpeta `agents/`)

Los agentes son la piedra angular de la funcionalidad de CrewAI en este proyecto. Cada uno tiene un rol y un objetivo específico:

### 1. Agente Estructurador (`estructurador.py`)

*   **Rol:** Arquitecto de Documentos Técnicos.
*   **Objetivo:** Crear una estructura lógica, coherente y profesional para el documento técnico sobre el tema proporcionado.
*   **Funcionamiento:** Analiza el tema, identifica conceptos clave y organiza el contenido en una jerarquía Markdown con secciones y subsecciones. Define la estructura base que luego será completada por otros agentes.

### 2. Agente Buscador (`buscador.py`)

Este archivo define dos tipos de agentes buscadores:

*   **Agente Investigador Digital Especializado:**
    *   **Rol:** Investigador Digital Especializado.
    *   **Objetivo:** Buscar información técnica rigurosa y relevante sobre el tema, utilizando herramientas de búsqueda web.
    *   **Herramientas:** `buscar_web`.
    *   **Funcionamiento:** Realiza búsquedas en internet para recopilar datos, estadísticas, ejemplos y tendencias sobre secciones específicas del documento.
*   **Agente Buscador de Imágenes Especializado:**
    *   **Rol:** Buscador de Imágenes Especializado.
    *   **Objetivo:** Buscar y descargar una imagen relevante para el tema.
    *   **Herramientas:** `buscar_y_descargar_imagen`.
    *   **Funcionamiento:** Busca y descarga una imagen adecuada para ilustrar el documento.

### 3. Agente Escritor (`escritor.py`)

*   **Rol:** Redactor Técnico Especializado en Español.
*   **Objetivo:** Redactar contenido técnico profesional en español (con correcta codificación UTF-8) para cada sección, asegurando una longitud mínima (200 palabras, preferiblemente 400-600).
*   **Herramientas:** `append_to_markdown`.
*   **Funcionamiento:** Toma la información recopilada (o la estructura) y redacta el contenido de forma detallada y profesional. Utiliza la herramienta `append_to_markdown` para ir construyendo el archivo `temp/temp_markdown.md`.

A continuación, analizaré la carpeta `flows/`.

## Flujo de Trabajo (`flows/documento_flow.py`)

El archivo `documento_flow.py` define la clase `DocumentoFlowCompleto`, que hereda de `Flow` de CrewAI. Esta clase orquesta todo el proceso de generación del documento, gestionando el estado y la secuencia de las tareas entre los diferentes agentes.

El flujo se define mediante una serie de pasos decorados con `@start` y `@listen`:

1.  **`limpiar_y_crear_estructura_documento()` (`@start`)**:
    *   **Acción Inicial:** Limpia la carpeta `temp/` (eliminándola y volviéndola a crear).
    *   **Estructuración:** Utiliza el `agente_estructurador` para generar la estructura del documento (lista de secciones) basándose en el `topic` proporcionado.
    *   **Inicialización:** Crea el archivo `temp/temp_markdown.md` y escribe el título principal del documento.
    *   **Estado:** Almacena la estructura completa, la lista de secciones, y reinicia el contador de la sección actual.
    *   **Transición:** Pasa a `procesar_seccion_individual`.

2.  **`procesar_seccion_individual()` (`@listen(limpiar_y_crear_estructura_documento)`)**:
    *   **Iteración:** Este paso se ejecuta para cada sección identificada en la estructura.
    *   **Verificación:** Comprueba si todas las secciones han sido procesadas. Si es así, transita a `todas_secciones_completadas` (que implícitamente lleva a `buscar_imagen_portada`).
    *   **Procesamiento de Sección:**
        *   Obtiene la sección actual de la lista.
        *   Crea un `Crew` específico para esta sección con el `agente_buscador` y el `agente_escritor`.
        *   **Tarea de Investigación:** El `agente_buscador` investiga la sección actual.
        *   **Tarea de Redacción:** El `agente_escritor` redacta el contenido de la sección, utilizando la información de la investigación, y lo añade a `temp/temp_markdown.md`.
    *   **Estado:** Incrementa el contador de la sección actual.
    *   **Transición:** Vuelve a llamarse a sí mismo (implícitamente a través del router de CrewAI o la lógica interna) hasta que todas las secciones se completan, luego pasa a `buscar_imagen_portada`.

3.  **`buscar_imagen_portada()` (`@listen(procesar_seccion_individual)`)**:
    *   **Acción:** Una vez todas las secciones han sido escritas, este paso utiliza la herramienta `_buscar_imagen_base` (probablemente del `agente_buscador_imagen` o una función directa de `tools.search_tools`) para encontrar y descargar una imagen de portada relacionada con el `topic`.
    *   **Estado:** Guarda la ruta de la imagen descargada (si se encuentra) en `self.state.imagen_portada`.
    *   **Transición:** Pasa a `compilar_documento_final`.

4.  **`compilar_documento_final()` (`@listen(buscar_imagen_portada)`)**:
    *   **Acción:** Lee el contenido completo del archivo `temp/temp_markdown.md`.
    *   Utiliza la herramienta `_generar_pdf_base` (de `tools.pdf_tool`) para convertir el contenido Markdown a un archivo PDF. Intenta incluir la imagen de portada descargada.
    *   **Estado:** Guarda la ruta del PDF generado en `self.state.pdf_final`.
    *   **Transición:** Pasa a `mover_pdf_y_mostrar_estadisticas_finales`.

5.  **`mover_pdf_y_mostrar_estadisticas_finales()` (`@listen(compilar_documento_final)`)**:
    *   **Organización:** Crea la carpeta `output/` si no existe.
    *   Mueve el PDF generado desde `temp/` a la carpeta `output/`, renombrándolo de forma descriptiva según el `topic`.
    *   **Información:** Imprime estadísticas finales del proceso, como el tema, número de secciones, conteo de palabras y líneas del Markdown, y el tamaño del PDF final.

### Estado del Flujo (`DocumentoState`)

La clase `DocumentoState` (un `BaseModel` de Pydantic) se utiliza para mantener y pasar información entre los diferentes pasos del flujo. Incluye campos como:

*   `topic`: El tema del documento.
*   `estructura_completa`: El string Markdown de la estructura generada.
*   `secciones_lista`: La lista de nombres de las secciones.
*   `seccion_actual`: Índice de la sección que se está procesando.
*   `archivo_markdown`: Ruta al archivo Markdown temporal (`temp/temp_markdown.md`).
*   `imagen_portada`: Ruta a la imagen de portada descargada.
*   `pdf_final`: Ruta al archivo PDF final generado.
*   `total_secciones`: Número total de secciones a procesar.

Este flujo asegura un proceso modular y robusto para la generación de documentos, desde la estructuración inicial hasta la compilación final del PDF.

## Herramientas Personalizadas (Carpeta `tools/`)

La carpeta `tools/` contiene módulos con funciones decoradas con `@tool` de CrewAI, lo que permite a los agentes utilizarlas para realizar acciones específicas.

### 1. Herramientas de Archivo (`file_tools.py`)

*   **`append_to_markdown(content: str) -> str`**
    *   **Propósito:** Añade el `content` (string en formato Markdown) al final del archivo `temp/temp_markdown.md`.
    *   **Funcionamiento:**
        *   Realiza una limpieza y decodificación del contenido de entrada (maneja JSON, escapes Unicode).
        *   Asegura que el contenido no esté vacío o sea demasiado corto.
        *   Crea la carpeta `temp/` si no existe.
        *   Añade el contenido al archivo usando codificación `utf-8-sig` (para manejar correctamente caracteres especiales y BOM).
        *   Retorna un mensaje de confirmación con estadísticas del archivo (palabras y líneas).
    *   **Uso Principal:** Utilizado por el `agente_escritor` para construir incrementalmente el documento Markdown.

### 2. Herramienta de PDF (`pdf_tool.py`)

*   **`generar_pdf_desde_markdown(markdown_content: str, imagen_portada: str = "temp/temp_image.jpg", output_pdf_path: str = "temp/final_documento.pdf") -> str`**
    *   **Propósito:** Convierte un string de contenido Markdown a un archivo PDF.
    *   **Funcionamiento (`_generar_pdf_base`):
        *   **Dependencias:** Utiliza las bibliotecas `weasyprint` y `markdown`.
        *   **Imagen de Portada:**
            *   Intenta usar la `imagen_portada` proporcionada.
            *   Si no se provee o no existe, busca imágenes en ubicaciones predefinidas (ej. `temp/temp_image.jpg`).
            *   Si se encuentra una imagen, la convierte a base64 y la incrusta en una página de portada HTML.
            *   La portada incluye el título del documento (extraído del primer H1 del Markdown) y la fecha actual.
        *   **Conversión Markdown a HTML:** Convierte el `markdown_content` a HTML usando la biblioteca `markdown` con extensiones como `tables`, `toc`, `fenced_code`, `codehilite`.
        *   **Estilos CSS:** Aplica un conjunto de estilos CSS para formatear el PDF (márgenes, fuentes, encabezados, tablas, numeración de página, etc.).
        *   **Generación PDF:** Utiliza `WeasyPrint` para renderizar el HTML (con la portada y el contenido) a un archivo PDF en la `output_pdf_path`.
        *   Retorna la ruta del archivo PDF generado o un string vacío si falla.
    *   **Uso Principal:** Utilizado en el `documento_flow.py` en el paso `compilar_documento_final` para generar el PDF.

### 3. Herramientas de Búsqueda (`search_tools.py`)

Este módulo define herramientas para interactuar con servicios de búsqueda web.

*   **`buscar_web(query: str) -> str`**
    *   **Propósito:** Realiza una búsqueda web utilizando la API de Google Serper (`google.serper.dev/search`).
    *   **Funcionamiento (`_buscar_web_base`):
        *   Utiliza una API Key de Serper (hardcodeada en el script).
        *   Envía la `query` a la API, solicitando resultados en español.
        *   Procesa los resultados orgánicos (título, snippet, link) y el Knowledge Graph si está disponible.
        *   Retorna un string formateado con la información encontrada o un mensaje de error.
    *   **Uso Principal:** Utilizado por el `agente_buscador` para recopilar información sobre el tema.

*   **`buscar_y_descargar_imagen(topic: str) -> str`**
    *   **Propósito:** Busca una imagen relevante para el `topic` utilizando la API de imágenes de Google Serper (`google.serper.dev/images`) y la descarga.
    *   **Funcionamiento (`_buscar_imagen_base`):
        *   Envía el `topic` (con "high quality" añadido) a la API de imágenes de Serper.
        *   Intenta descargar la primera imagen válida de los resultados.
        *   Guarda la imagen en la carpeta `temp/` con un nombre como `temp_image.jpg` (la extensión puede variar).
        *   Retorna un mensaje con la ruta de la imagen descargada o un mensaje de error.
    *   **Uso Principal:** Utilizado por el `agente_buscador_imagen` (o directamente en el flujo) para obtener una imagen de portada.

## Utilidades (Carpeta `utils/`)

La carpeta `utils/` contiene scripts con funciones de ayuda y configuración para el proyecto.

### 1. Corrector de Codificación (`fix_encoding.py`)

*   **`fix_markdown_encoding() -> str`**
    *   **Propósito:** Corregir problemas de codificación y limpiar el archivo `temp/temp_markdown.md`.
    *   **Funcionamiento:**
        *   Lee el archivo `temp/temp_markdown.md` en modo binario y lo decodifica como `latin-1` (una estrategia común para capturar bytes mal codificados).
        *   Realiza una serie de reemplazos para caracteres comunes mal codificados (ej. `Ã¡` por `á`).
        *   Elimina comentarios HTML (`<!-- ... -->`).
        *   Limpia residuos como `"}` al final de líneas.
        *   Normaliza múltiples saltos de línea a un máximo de dos.
        *   Crea un backup del archivo original (ej. `temp_markdown.md.backup`).
        *   Guarda el contenido corregido y limpio de nuevo en `temp/temp_markdown.md` con codificación `utf-8-sig`.
    *   **Uso Principal:** Se podría llamar después de que el `agente_escritor` complete sus tareas para asegurar que el Markdown final tenga la codificación correcta antes de la conversión a PDF, aunque no se ve explícitamente en el flujo principal, podría ser una utilidad para ejecutar manualmente o en un paso de post-procesamiento.

### 2. Proveedor de LLM (`llm_provider.py`)

*   **`crear_llm_crewai(modelo_seleccionado=None) -> LLM`**
    *   **Propósito:** Crea y configura una instancia del LLM para ser utilizada por los agentes de CrewAI, optimizada para respuestas largas.
    *   **Funcionamiento:**
        *   Si no se proporciona `modelo_seleccionado`, llama a `seleccionar_lllm()` de `llm_selector.py` para obtener uno.
        *   Configura el objeto `LLM` de CrewAI para usar un endpoint local de Ollama (`http://localhost:11434/v1`).
        *   Establece parámetros para evitar el truncamiento de respuestas y mejorar la consistencia:
            *   `max_tokens=4096`
            *   `temperature=0.3`
            *   `timeout=600` (10 minutos)
        *   Retorna la instancia del LLM configurada.
    *   **Uso Principal:** Llamado por los diferentes agentes (`buscador.py`, `escritor.py`, `estructurador.py`) al inicializarse para obtener su modelo de lenguaje.

### 3. Selector de LLM (`llm_selector.py`)

*   **`obtener_modelos_disponibles_ollama() -> list`**
    *   **Propósito:** Obtiene la lista de modelos de lenguaje instalados localmente en la instancia de Ollama.
    *   **Funcionamiento:** Utiliza la biblioteca `ollama` de Python para conectarse al servidor de Ollama y listar los modelos disponibles.
    *   Retorna una lista de nombres de modelos (ej. `['gemma3:4b', 'llama3:latest']`) o una lista vacía si hay un error de conexión.
*   **`seleccionar_llm() -> str`**
    *   **Propósito:** Selecciona un modelo LLM para usar, priorizando `gemma3:4b`.
    *   **Funcionamiento:**
        *   Llama a `obtener_modelos_disponibles_ollama()`.
        *   Si `gemma3:4b` está en la lista, lo retorna.
        *   Si no, y la lista no está vacía, elige un modelo al azar de los disponibles y muestra una advertencia.
        *   Si no hay modelos instalados, lanza un `RuntimeError`.
    *   **Uso Principal:** Utilizado por `llm_provider.py` para determinar qué modelo configurar si no se especifica uno explícitamente. También es usado en `app.py` para poblar el selector de modelos en la interfaz de Streamlit.
