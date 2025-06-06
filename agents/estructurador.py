#!/usr/bin/env python3
# proyecto_crewai/agents/estructurador.py

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

# ==================== AGENTE ESTRUCTURADOR ====================

def crear_agente_estructurador(modelo: str = None) -> Agent:
    """
    Crea y devuelve el agente especializado en estructurar documentos
    """
    try:
        llm = crear_llm_crewai(modelo_seleccionado=modelo)
        
        agent = Agent(
            role="Arquitecto de Documentos Técnicos",
            goal="Crear estructuras lógicas, coherentes y profesionales para documentos técnicos y científicos",
            backstory="""Eres un experto arquitecto de información con más de 15 años de experiencia 
            estructurando documentos académicos, científicos y técnicos. Tu especialidad es crear 
            títulos claros y lógicos que faciliten la comprensión de temas complejos.
            """,
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        return agent
        
    except Exception as e:
        raise RuntimeError(f"Error creando agente estructurador: {e}")


def crear_tarea_estructurar(topic: str, agent: Agent) -> Task:
    """
    Crea la tarea de estructuración para el agente
    """
    try:
        
        task = Task(
            description=f"""
            Crear una estructura simple y efectiva para un documento técnico sobre: {topic}
            
            INSTRUCCIONES:
            - Un título general
            - Crea entre 8-12 títulos principales
            - Los títulos deben seguir una secuencia lógica (desde introducción hasta conclusión)
            - Cada título debe ser descriptivo y específico al tema
            - Los títulos deben estar en español
            - Usa formato markdown con dos almohadillas (##) para cada título principal
            """,
            expected_output=f"""
            Una lista de 8-12 títulos principales en formato markdown para un documento sobre {topic}:
            
            # {topic}
            
            ## 1. Introducción
            
            ## 2. [Título específico relevante]
            
            ## 3. [Título específico relevante]
            
            ...
            
            ## [8-12]. Conclusiones
            
            Los títulos deben ser descriptivos, específicos al tema, y estar en un orden lógico.
            No incluir subtítulos ni descripciones adicionales.
            """,
            agent=agent
        )
        
        return task
        
    except Exception as e:
        raise RuntimeError(f"Error creando tarea de estructuración: {e}")


# ==================== FUNCIONES DE UTILIDAD ====================

def estructurar_documento(topic: str) -> str:
    """
    Función principal para estructurar un documento sobre un tema dado
    """
    try:
        from crewai import Crew, Process
        
        print(f"📋 Iniciando estructuración del documento sobre: {topic}")
        
        # Crear tarea
        task = crear_tarea_estructurar(topic)
        
        # Crear crew con un solo agente
        crew = Crew(
            agents=[task.agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        # Ejecutar
        resultado = crew.kickoff(inputs={"topic": topic})
        
        return resultado.raw if hasattr(resultado, 'raw') else str(resultado)
        
    except Exception as e:
        return f"Error en estructuración: {str(e)}"


def main():
    """
    Función main para probar el agente estructurador
    """
    print("🧪 Probando agente estructurador...")
    
    # Temas de prueba
    temas_prueba = [
        "Inteligencia Artificial en la Medicina",
        "Blockchain y Criptomonedas", 
        "Computación Cuántica"
    ]
    
    print("📝 Temas disponibles para prueba:")
    for i, tema in enumerate(temas_prueba, 1):
        print(f"  {i}. {tema}")
    
    try:
        # Usar el primer tema por defecto o permitir selección
        tema_seleccionado = temas_prueba[0]
        print(f"\n🎯 Usando tema: {tema_seleccionado}")
        
        # Estructurar documento
        resultado = estructurar_documento(tema_seleccionado)
        
        print("\n" + "="*60)
        print("📋 ESTRUCTURA GENERADA:")
        print("="*60)
        print(resultado)
        print("="*60)
        
        # Guardar resultado en archivo
        filename = f"estructura_{tema_seleccionado.replace(' ', '_').lower()}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(resultado)
        
        print(f"\n✅ Estructura guardada en: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
