#!/usr/bin/env python3
# proyecto_crewai/utils/llm_provider.py (CONFIGURACIÓN OPTIMIZADA PARA RESPUESTAS LARGAS)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .llm_selector import seleccionar_llm

def crear_llm_crewai(modelo_seleccionado=None):
    """
    Crea LLM optimizado para respuestas largas sin truncamiento
    """
    try:
        if modelo_seleccionado is None:
            modelo_seleccionado = seleccionar_llm()
        print(f"[INFO] Configurando LLM optimizado: {modelo_seleccionado}")
        from crewai import LLM
        
        # Detectar si estamos en Docker o local
        ollama_host = os.getenv('OLLAMA_HOST', 'localhost:11434')
        if not ollama_host.startswith('http'):
            ollama_host = f"http://{ollama_host}"
        base_url = f"{ollama_host}/v1"
        
        print(f"[INFO] Conectando a Ollama en: {base_url}")
        
        # Configuración optimizada para respuestas largas
        llm = LLM(
            model=f"openai/{modelo_seleccionado}",
            base_url=base_url,
            api_key="ollama",
            # CONFIGURACIÓN ANTI-TRUNCAMIENTO
            max_tokens=2024,  # Máximo permitido para respuestas largas
            temperature=0.3,  # Menor para respuestas más consistentes
            timeout=600,  # 10 minutos timeout
            # CONFIGURACIONES ADICIONALES
            repetition_penalty=1.1,
            #system_template="",
            #prompt_template="{{user_input}}"
            think=False
        )
        
        return llm
        
    except Exception as e:
        raise RuntimeError(f"Error configurando LLM optimizado: {e}")

def main():
    try:
        print("Probando LLM optimizado para respuestas largas...")
        llm = crear_llm_crewai()
        print(f"LLM optimizado creado exitosamente")
        print(f"   Max tokens: 4096")
        print(f"   Timeout: 600 segundos")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
