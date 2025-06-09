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

def crear_agente_escritor(modelo: str = None, llm_instance=None) -> Agent:
    """
    Crea y devuelve el agente especializado en redacción técnica
    """
    try:
        # Usar LLM pasado como parámetro o crear uno nuevo si no se proporciona
        if llm_instance is not None:
            llm = llm_instance
        else:
            llm = crear_llm_crewai(modelo_seleccionado=modelo)
        
        # Importar la tool de append
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from tools.file_tools import append_to_markdown
        
        agent = Agent(
            role="Redactor Técnico Especializado en Español",
            goal="Redactar contenido técnico profesional en español con codificación UTF-8 correcta. MÍNIMO 200 palabras por sección.",
            backstory="""Eres un redactor técnico senior especializado en crear documentación técnica en español.
            
            REQUISITOS DE LONGITUD:
            - Cada sección debe tener mínimo 200 palabras de contenido sustancial
            - Preferiblemente entre 400-600 palabras para ser completa
            - El texto debe estar en español correcto
            
            Tu especialidad es redactar textos técnicos bien estructurados, detallados y de alta calidad,
            asegurando que cada sección cumple con los requisitos de longitud y contiene información
            relevante y rigurosa sobre el tema.
            Lo único que debes hacer es usar la herramienta append_to_markdown para añadir el contenido que redactes. Recuerda que solo has de usarla al final pasándole el contenido como String.
            ATENCIÓN: SOLO USAR LA HERRAMIENTA 1 VEZ AL FINAL PARA NO AÑADIR CONTENIDO INCOMPLETO.
            Al finalizar, asegúrate de que tu Final Answer sea: "Contenido añadido exitosamente al archivo markdown.".

            """,
            llm=llm,
            tools=[append_to_markdown],
            verbose=True,
            allow_delegation=False,
            max_iter=1,
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
            TAREA: Redactar la sección "{seccion}" sobre {topic} y guardarla en el archivo.

            Redacta contenido técnico profesional en formato markdown para la sección especificada.
            El contenido debe ser en español, tener entre 400-600 palabras y utilizar el formato:
            
            ## {seccion}
            
            [Contenido detallado sobre el tema]
            
            Guarda el contenido usando la herramienta append_to_markdown cuando hayas terminado y estés seguro de que es contenido válido.
            """,
            expected_output=f"""
            Una sección bien redactada sobre "{seccion}" con:
            - Contenido técnico detallado en español
            - Longitud entre 400-600 palabras
            - Formato markdown correcto
            - Confirmación de que el contenido ha sido añadido exitosamente
            """,
            agent=agent
        )
        
        return task
        
    except Exception as e:
        raise RuntimeError(f"Error creando tarea de redacción: {e}")
