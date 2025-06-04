#!/usr/bin/env python3
# proyecto_crewai/agents/escritor.py (MEJORADO CON VALIDACIÓN DE LONGITUD)

import os
import sys
from crewai import Agent, Task

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.llm_provider import crear_llm_crewai
except ImportError:
    print("[ERROR] No se pudo importar llm_provider")
    sys.exit(1)

# ==================== AGENTE ESCRITOR ====================

def crear_agente_escritor():
    """
    Crea y devuelve el agente especializado en redacción técnica
    """
    try:
        llm = crear_llm_crewai()
        
        # Importar la tool de append
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from tools.file_tools import append_to_markdown
        
        agent = Agent(
            role="Redactor Técnico Especializado en Español",
            goal="Redactar contenido técnico profesional en español con codificación UTF-8 correcta. MÍNIMO 200 palabras por sección.",
            backstory="""Eres un redactor técnico senior especializado en crear documentación técnica en español.
            ADVERTENCIA: TU HERRAMIENTA USA UN ARGUMENTO CONTENT POSICIONAL, NO LA USES ANTES DE SABER QUE LE VAS A PASAR
            IMPORTANTE SOBRE CODIFICACIÓN:
            - Siempre usa caracteres españoles correctos: á, é, í, ó, ú, ñ
            - NO uses caracteres como Ã¡, Ã©, Ã­, Ã³, Ãº que son errores de codificación
            - Escribe directamente: "Introducción", "médico", "diagnóstico", "información"
            - NUNCA escribas: "IntroducciÃ³n", "mÃ©dico", "diagnÃ³stico", "informaciÃ³n"
            
            REQUISITOS DE LONGITUD CRÍTICOS:
            - Cada sección debe tener MÍNIMO 200 palabras de contenido sustancial
            - Preferiblemente entre 400-600 palabras para ser completa
            - NO escribas contenido superficial o demasiado breve
            - Si una sección es corta, se te pedirá que la reescribas
            
            FUNDAMENTAL:
            - Tu unica herramienta es append_to_markdown
            - El texto de salida debe ser traducido al idioma español
            - Debes usarla para guardar el contenido redactado al final
            - NO intentes usar otras herramientas o tools, ya que eso arruinaría el proceso
            - Debes pasarle como argumento un string con TODO el contenido redactado, incluyendo el título de la sección
            - PROHINIDO usar diccionarios o estructuras complejas, solo strings simples
            - El string debe contener MÍNIMO 200 palabras, preferiblemente 400-600
            - El formato debe ser algo como: append_to_markdown(content="## Título de la sección\n\n[Tu contenido aquí]")
            Tu proceso es:
            1. Redactar contenido técnico profesional EN ESPAÑOL CORRECTO con MÍNIMO 200 palabras
            2. Usar append_to_markdown para guardarlo inmediatamente. Solo tienes esta herramienta, no intentes usar otras. ¡IMPORTANTE!
            3. Confirmar que se guardó correctamente

            Recuerda que tu unica herramienta es append_to_markdown, y debes usarla para guardar el contenido redactado. No intentes usar ninguna otra herramienta o tool ya que fastidiarías todo nuestro trabajo.

            """,
            llm=llm,
            tools=[append_to_markdown],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            max_execution_time=600
        )
        
        return agent
        
    except Exception as e:
        raise RuntimeError(f"Error creando agente escritor: {e}")

def crear_tarea_redaccion_archivo(agent: Agent, seccion: str, topic: str):
    """
    Crea una tarea de redacción que escribe SOLO la nueva sección para ser añadida al archivo
    """
    try:
        task = Task(
            description=f"""
            TAREA ESPECÍFICA: Redactar la sección "{seccion}" sobre {topic} y guardarla en el archivo.

            REQUISITOS CRÍTICOS DE LONGITUD:
            - La sección debe tener MÍNIMO 200 palabras de contenido sustancial
            - Preferiblemente entre 400-600 palabras para ser completa y profesional
            - NO escribas contenido superficial, breve o de relleno
            - Desarrolla cada punto con ejemplos específicos y detalles técnicos

            PASO 1 - REDACTAR:
            Crear contenido markdown profesional para la sección "{seccion}".
            
            FORMATO EXACTO:
            ## {seccion}

            [Aquí tu contenido DETALLADO de 400-600 palabras sobre {seccion}]
            
            PASO 2 - GUARDAR OBLIGATORIO:
            Usar la herramienta append_to_markdown pasando TODO el contenido que redactaste.
            
            FORMATO CORRECTO PARA USAR LA HERRAMIENTA:
            append_to_markdown(content="## {seccion}\n\n[Tu contenido completo aquí]")
            
            EJEMPLO ESPECÍFICO:
            append_to_markdown(content="## Introducción\n\nLa inteligencia artificial en medicina representa...")
            
            IMPORTANTE:
            - Pasa el contenido como UN SOLO STRING
            - NO uses diccionarios o estructuras complejas
            - NO dejes parámetros vacíos
            - Incluye el título de la sección (##) y todo el contenido
            - El string debe contener MÍNIMO 200 palabras
            - El texto debe ser traducido al idioma español, no debe haber contenido en inglés
            """,
            expected_output=f"""
            DEBES ENTREGAR:
            1. El contenido markdown de la sección "{seccion}" (MÍNIMO 200 palabras, preferible 400-600) el contenido debe ser traducido al español
            2. Confirmación exitosa de la herramienta: "✅ Contenido añadido exitosamente a temp/temp_markdown.md"
            
            VALIDACIÓN: El archivo temp/temp_markdown.md debe crecer en tamaño con tu nueva sección.
            
            IMPORTANTE: Si escribes menos de 200 palabras, se te pedirá que reescribas la sección con más detalle.
            """,
            agent=agent
        )
        
        return task
        
    except Exception as e:
        raise RuntimeError(f"Error creando tarea de redacción: {e}")
