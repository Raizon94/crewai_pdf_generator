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

def crear_agente_buscador_automatico():
    """
    Crea agente buscador que usa automáticamente las @tools según su criterio (ReAct)
    """
    try:
        llm = crear_llm_crewai()
        
        agent = Agent(
            role="Investigador Digital Especializado",
            goal="Buscar información técnica rigurosa y relevante sobre {topic} usando herramientas de búsqueda web",
            backstory="""Eres un investigador digital experto con acceso a herramientas de búsqueda web avanzadas.
            Tu especialidad es encontrar información técnica actualizada sobre {topic}.
            
            Tienes acceso a herramientas de búsqueda que te permiten:
            - Buscar información específica en internet
            - Encontrar datos técnicos y estadísticas relevantes
            - Obtener ejemplos prácticos y casos de uso
            - Identificar tendencias actuales y perspectivas futuras
            
            Utilizas estas herramientas de manera inteligente para recopilar información completa 
            y técnicamente precisa sobre cualquier aspecto de {topic} que se te solicite.
            
            Eres autónomo y decides cuándo y cómo usar las herramientas disponibles según 
            las necesidades de cada búsqueda específica.""",
            llm=llm,
            tools=[buscar_web],  # El agente decidirá automáticamente cuándo usarlas
            verbose=True,
            allow_delegation=False,
            max_iter=1,
            max_execution_time=300
        )
        
        return agent
        
    except Exception as e:
        raise RuntimeError(f"Error creando agente buscador automático: {e}")
def crear_agente_buscador_imagen():
    """
    Crea agente buscador que usa automáticamente la herramienta de búsqueda de imágenes
    """
    try:
        llm = crear_llm_crewai()
        tools = [buscar_y_descargar_imagen]
        
        agent = Agent(
            role="Buscador de Imágenes Especializado",
            goal="Buscar y descargar una imagen relevante para el tema {topic}",
            backstory="""Eres un buscador de imágenes experto con acceso a herramientas avanzadas de búsqueda visual.
            Tu especialidad es encontrar imágenes técnicas y diagramas relevantes sobre {topic}.
            
            Tienes acceso a herramientas que te permiten:
            - Buscar imágenes específicas en internet
            - Descargar imágenes relevantes para ilustrar documentos técnicos
            
            Utilizas estas herramientas de manera inteligente para obtener la imagen más adecuada 
            y técnicamente precisa sobre cualquier aspecto de {topic} que se te solicite.
            
            Eres autónomo y decides cuándo y cómo usar las herramientas disponibles según 
            las necesidades de cada búsqueda específica.""",
            llm=llm,
            tools=tools,  # El agente decidirá automáticamente cuándo usarlas
            verbose=True,
            allow_delegation=False,
            max_iter=1,
            max_execution_time=300
        )
        
        return agent
        
    except Exception as e:
        raise RuntimeError(f"Error creando agente buscador de imágenes: {e}")


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

            INSTRUCCIONES PARA USAR LA HERRAMIENTA DE BÚSQUEDA:
            
            1. DEBES usar EXACTAMENTE este formato cuando uses la herramienta:
               Action: BuscadorWeb
               Action Input: {{"query": "tu consulta aquí como texto simple"}}
            
            2. NUNCA uses este formato incorrecto:
               Action: BuscadorWeb
               Action Input: {{"query": {{"description": "tu consulta"}}}}
            
            3. NUNCA uses este formato incorrecto:
               Action: BuscadorWeb
               Action Input: {{"description": "tu consulta"}}
            
            4. El valor para "query" DEBE SER UN STRING SIMPLE, nunca un objeto/diccionario.
            
            EJEMPLOS DE USO CORRECTO:
            
            Action: BuscadorWeb
            Action Input: {{"query": "{seccion} definición"}}
            
            Action: BuscadorWeb
            Action Input: {{"query": "{seccion} aplicaciones en {topic}"}}
            
            Action: BuscadorWeb
            Action Input: {{"query": "{seccion} estadísticas actuales"}}
            
            EJEMPLO DE PROCESO COMPLETO DE BÚSQUEDA:
            
            1. Piensa qué información específica necesitas: "Quiero datos sobre {seccion}"
            2. Formula una consulta simple y directa
            3. Usa la herramienta con el formato correcto:
               Action: BuscadorWeb
               Action Input: {{"query": "{seccion} datos estadísticas"}}
            4. Analiza los resultados y haz más búsquedas si es necesario
            
            IMPORTANTE: 
            - SOLO usa consultas como strings simples dentro de "query"
            - Haz múltiples búsquedas para información más completa
            - Consultas cortas y específicas funcionan mejor que largas
            """,
            expected_output=f"""
            Investigación sobre "{seccion}" con:
            - Definiciones técnicas
            - Aplicaciones prácticas
            - Datos y estadísticas
            - Ejemplos reales
            - Fuentes consultadas
            
            Aproximadamente 300-500 palabras.
            """,
            agent=agent
        )
        
        return task
        
    except Exception as e:
        raise RuntimeError(f"Error creando tarea de investigación automática: {e}")

