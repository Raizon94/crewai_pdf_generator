#!/usr/bin/env python3
# proyecto_crewai/agents/buscador.py (VERSIÓN AUTOMÁTICA - AGENTE REACT)

import os
import sys
from crewai import Agent, Task

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.llm_provider import crear_llm_crewai
    from tools.search_tools import buscar_web  # Herramienta personalizada con control
except ImportError:
    print("[ERROR] No se pudieron importar las dependencias necesarias")
    sys.exit(1)

# ==================== AGENTE BUSCADOR AUTOMÁTICO ====================

def crear_agente_buscador_automatico(modelo: str = None, llm_instance=None) -> Agent:
    """
    Crea agente buscador que usa automáticamente las @tools según su criterio (ReAct)
    Versión CONTROLADA para evitar loops infinitos
    """
    try:
        # Usar LLM pasado como parámetro o crear uno nuevo si no se proporciona
        if llm_instance is not None:
            llm = llm_instance
        else:
            llm = crear_llm_crewai(modelo_seleccionado=modelo)
        
        # USAR HERRAMIENTAS PERSONALIZADAS EN LUGAR DE SERPERDEVTOOL
        # Esto nos da más control sobre el comportamiento
        agent = Agent(
            role="Investigador Digital Especializado",
            goal="Buscar información técnica rigurosa y relevante usando herramienta de búsqueda web UNA SOLA VEZ",
            backstory="""Eres un investigador digital experto con acceso a herramientas de búsqueda web avanzadas.
            Tu especialidad es encontrar información técnica actualizada sobre diversos temas.
            
            INSTRUCCIONES CRÍTICAS:
            - Realiza UNA SOLA búsqueda web por tarea
            - Una vez que obtengas resultados, analízalos y proporciona un resumen
            - NO busques múltiples veces
            - Si los primeros resultados son suficientes, NO busques más
            - Tu objetivo es ser eficiente, no exhaustivo
            - Después de usar la herramienta de búsqueda UNA VEZ, proporciona tu análisis final
            """,
            llm=llm,
            # USAR HERRAMIENTA PERSONALIZADA EN LUGAR DE SERPERDEVTOOL
            tools=[buscar_web],  # Herramienta personalizada con más control
            verbose=True,
            allow_delegation=False,
            max_iter=1,  # SOLO UNA ITERACIÓN para evitar loops
            max_execution_time=120  # TIEMPO LIMITADO
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

            PROCESO ESPECÍFICO Y OBLIGATORIO:
            1. Realiza UNA búsqueda web sobre "{seccion}" en el contexto de {topic} usando la herramienta buscar_web
            2. Analiza los resultados obtenidos de esa ÚNICA búsqueda
            3. Extrae los puntos clave más relevantes de esos resultados
            4. Finaliza tu tarea con un resumen - NO busques más información

            RESTRICCIONES CRÍTICAS:
            - MÁXIMO 1 uso de la herramienta buscar_web
            - NO realices búsquedas adicionales bajo ninguna circunstancia
            - Trabaja únicamente con los resultados de la primera búsqueda
            - Tu respuesta final debe ser un análisis de lo encontrado, no más búsquedas

            CONSULTA PARA BUSCAR: "{seccion} {topic}"
            """,
            expected_output=f"""
            Resumen conciso sobre "{seccion}" basado en UNA ÚNICA búsqueda web:
            
            - 3-5 puntos clave específicos sobre el tema
            - Datos técnicos o estadísticas relevantes (si están disponibles)
            - Ejemplos concretos relacionados con {topic}
            - Texto en ESPAÑOL, aproximadamente 50-150 palabras
            
            FORMATO REQUERIDO:
            "Información encontrada sobre [seccion]:
            • Punto clave 1
            • Punto clave 2  
            • Punto clave 3
            [etc.]"
            
            IMPORTANTE: Este es tu resultado final - NO busques más información.
            """,
            agent=agent
        )
        
        return task
        
    except Exception as e:
        raise RuntimeError(f"Error creando tarea de investigación automática: {e}")

