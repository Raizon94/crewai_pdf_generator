#!/usr/bin/env python3
# proyecto_crewai/agents/buscador.py (VERSIÓN AUTOMÁTICA - AGENTE REACT)

import os
import sys
from crewai import Agent, Task

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.llm_provider import crear_llm_crewai
    from tools.search_tools import buscar_web, buscar_y_descargar_imagen
except ImportError:
    print("[ERROR] No se pudieron importar las dependencias necesarias")
    sys.exit(1)

# ==================== AGENTE BUSCADOR AUTOMÁTICO ====================

def crear_agente_buscador_automatico(modelo: str = None) -> Agent:
    """
    Crea agente buscador que usa automáticamente las @tools según su criterio (ReAct)
    """
    try:
        llm = crear_llm_crewai(modelo_seleccionado=modelo)
        
        agent = Agent(
            role="Investigador Digital Especializado",
            goal="Buscar información técnica rigurosa y relevante usando herramienta de búsqueda web",
            backstory="""Eres un investigador digital experto con acceso a herramientas de búsqueda web avanzadas.
            Tu especialidad es encontrar información técnica actualizada sobre diversos temas.
            
            Tienes acceso a herramientas de búsqueda que te permiten:
            - Buscar información específica en internet
            - Encontrar datos técnicos y estadísticas relevantes
            - Obtener ejemplos prácticos y casos de uso
            - Identificar tendencias actuales y perspectivas futuras

            ATENCIÓN: NUNCA USAS LA HERRAMIENTA PASÁNDOLE ALGO QUE NO SEA UN STRING.
            NUNCA LE PASES ALGO COMO: {'description': 'Transfor...iration', 'type': 'str'}
            SOLO STRINGS PUROS, CON LA QUERY A BUSCAR.
          
            
            Eres autónomo y decides cuándo y cómo usar la herramienta disponible según 
            las necesidades de cada búsqueda específica.""",
            llm=llm,
            tools=[buscar_web],  # El agente decidirá automáticamente cuándo usarlas
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
            Investiga a fondo y recopila datos relevantes sobre este tema usando tu herramienta buscar_web para buscar en Internet.
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

