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

def crear_agente_estructurador():
    """
    Crea y devuelve el agente especializado en estructurar documentos
    """
    try:
        llm = crear_llm_crewai()
        
        agent = Agent(
            role="Arquitecto de Documentos Técnicos",
            goal="Crear estructuras lógicas, coherentes y profesionales para documentos técnicos y científicos",
            backstory="""Eres un experto arquitecto de información con más de 15 años de experiencia 
            estructurando documentos académicos, científicos y técnicos. Tu especialidad es crear 
            esquemas claros y lógicos que faciliten la comprensión de temas complejos.
            
            Tienes un doctorado en Ciencias de la Información y has trabajado como editor senior 
            en revistas científicas de prestigio. Conoces perfectamente las mejores prácticas 
            para organizar contenido técnico de manera que sea accesible tanto para expertos 
            como para lectores interesados en el tema.
            
            Tu filosofía es que una buena estructura es la base de cualquier documento exitoso.""",
            llm=llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        return agent
        
    except Exception as e:
        raise RuntimeError(f"Error creando agente estructurador: {e}")


def crear_tarea_estructurar(topic: str):
    """
    Crea la tarea de estructuración para el agente
    """
    try:
        agent = crear_agente_estructurador()
        
        task = Task(
            description=f"""
            Crear una estructura detallada y profesional para un documento técnico sobre: {topic}
            
            PASOS A SEGUIR:
            1. Analizar en profundidad el tema propuesto
            2. Identificar los conceptos fundamentales y aspectos clave a cubrir
            3. Organizar el contenido en una jerarquía lógica y coherente
            4. Crear títulos y subtítulos descriptivos y atractivos
            5. Asegurar que la estructura tenga un flujo narrativo natural
            6. Incluir secciones de introducción, desarrollo y conclusión
            7. Verificar que la estructura sea apropiada para el nivel técnico del tema
            
            CONSIDERACIONES IMPORTANTES:
            - La estructura debe ser adecuada para un documento de 8-12 páginas
            - Cada sección debe tener un propósito claro y diferenciado
            - Los títulos deben ser descriptivos pero concisos
            - Debe haber equilibrio entre secciones teóricas y prácticas
            - Considerar la inclusión de ejemplos, casos de uso o aplicaciones
            
            FORMATO REQUERIDO:
            - Usar formato markdown con niveles jerárquicos claros
            - Máximo 8 secciones principales (##)
            - Incluir subsecciones (###) solo cuando sea necesario
            - Cada sección debe tener un título descriptivo y explicativo
            """,
            expected_output=f"""
            Una estructura completa en formato markdown que incluya:
            
            # [Título Principal del Documento sobre {topic}]
            
            ## 1. Introducción
            [Breve descripción del propósito de esta sección]
            
            ## 2. [Conceptos Fundamentales/Marco Teórico]
            ### 2.1 [Subtema si es necesario]
            ### 2.2 [Subtema si es necesario]
            
            ## 3. [Sección de Desarrollo Principal]
            
            ## 4. [Metodología/Implementación/Técnicas]
            
            ## 5. [Aplicaciones/Casos de Uso/Ejemplos]
            
            ## 6. [Ventajas y Limitaciones/Análisis Crítico]
            
            ## 7. [Tendencias Futuras/Perspectivas]
            
            ## 8. Conclusiones
            
            REQUISITOS:
            - Mínimo 6 secciones principales, máximo 8
            - Títulos específicos y descriptivos (no genéricos)
            - Estructura lógica y progresiva
            - Balance entre teoría y práctica
            - Apropiado para audiencia técnica
            - Elige tu mismo los nombres de las secciones y subsecciones, lo de antes era solo un ejemplo para que entiendas el formato.

            IMPORTANTE: Esta estructura es solo un ejemplo, puedes adaptarla según el tema específico.
            Tu respuesta debe ser una estructura completa y detallada, lista para ser usada como base para el documento. Segun lo anterior
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
