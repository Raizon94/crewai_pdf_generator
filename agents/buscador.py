#!/usr/bin/env python3
# proyecto_crewai/agents/buscador.py (VERSIÓN AUTOMÁTICA - AGENTE REACT)

import os
import sys
from crewai import Agent, Task
# AÑADIR IMPORT PARA SERPER DEV TOOL
from crewai_tools import SerperDevTool

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.llm_provider import crear_llm_crewai
    from tools.search_tools import buscar_web, buscar_y_descargar_imagen
except ImportError:
    print("[ERROR] No se pudieron importar las dependencias necesarias")
    sys.exit(1)

# ==================== AGENTE BUSCADOR AUTOMÁTICO ====================

def crear_agente_buscador_automatico(modelo: str = None, llm_instance=None) -> Agent:
    """
    Crea agente buscador que usa automáticamente las @tools según su criterio (ReAct)
    """
    try:
        # Usar LLM pasado como parámetro o crear uno nuevo si no se proporciona
        if llm_instance is not None:
            llm = llm_instance
        else:
            llm = crear_llm_crewai(modelo_seleccionado=modelo)
        
        # INICIALIZAR SERPER DEV TOOL (lee SERPER_API_KEY del .env automáticamente)
        search_tool = SerperDevTool()
        
        agent = Agent(
            role="Investigador Digital Especializado",
            goal="Buscar información técnica rigurosa y relevante usando herramienta de búsqueda web",
            backstory="""Eres un investigador digital experto con acceso a herramientas de búsqueda web avanzadas.
            Tu especialidad es encontrar información técnica actualizada sobre diversos temas.
            """,
            llm=llm,
            # CAMBIAR tools=[buscar_web] POR LA TOOL OFICIAL:
            tools=[search_tool],  # SerperDevTool en lugar de buscar_web
            verbose=True,
            allow_delegation=False,
            max_iter=3,
            max_execution_time=300
        )
        
        return agent
        
    except Exception as e:
        raise RuntimeError(f"Error creando agente buscador automático: {e}")


def crear_tarea_investigacion_automatica(seccion: str, topic: str, agent: Agent) -> Task:
    """
    Crea tarea que confía en el agente para decidir cómo buscar automáticamente
    """
    try:
        task = Task(
            description=f"""
            Investigar sobre: "{seccion}" relacionado con {topic}.

            OBJETIVO:
            Buscar información técnica, estadísticas y ejemplos sobre "{seccion}".
            # NOTA: El agente ahora usará SerperDevTool automáticamente para buscar en Internet
            Investiga a fondo y recopila datos relevantes sobre este tema usando tu herramienta de búsqueda para buscar en Internet.
            """,
            expected_output=f"""
            Hechos y datos útiles sobre "{seccion}".
            
            Aproximadamente 50-150 palabras: SOLO PUNTOS CLAVE
            Traduce la investigación que recuperes al idioma español si es necesario.
            """,
            agent=agent
        )
        
        return task
        
    except Exception as e:
        raise RuntimeError(f"Error creando tarea de investigación automática: {e}")

