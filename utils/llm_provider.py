# proyecto_crewai/utils/llm_provider.py
# CONFIGURACIÓN OPTIMIZADA PARA RESPUESTAS LARGAS EN LM Studio

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .llm_selector import seleccionar_llm
from crewai import LLM


def crear_llm_crewai(modelo_seleccionado: str = None) -> LLM:
    """
    Crea y devuelve un LLM optimizado para respuestas largas usando LM Studio.
    - Ajusta automáticamente la URL base a /v1
    - Prefija el modelo con 'lm_studio/' para que LiteLLM detecte el provider
    - Configura timeout extendido
    """
    # Seleccionar modelo si no viene como parámetro
    if modelo_seleccionado is None:
        modelo_seleccionado = seleccionar_llm()
    prefijo_modelo = modelo_seleccionado
    # Asegurar que el modelo va con el prefijo lm_studio/
    if not modelo_seleccionado.startswith("lm_studio/"):
        prefijo_modelo = f"lm_studio/{modelo_seleccionado}"

    print(f"[INFO] Configurando LLM optimizado para LM Studio: {prefijo_modelo}")

    # Leer y normalizar URL de LM Studio
    lmstudio_base = os.getenv('LM_STUDIO_API_BASE', 'localhost:11434')
    if not lmstudio_base.startswith(('http://', 'https://')):
        lmstudio_base = f"http://{lmstudio_base}"
    if not lmstudio_base.rstrip('/').endswith('/v1'):
        lmstudio_base = lmstudio_base.rstrip('/') + '/v1'

    print(f"[INFO] Conectando a LM Studio en: {lmstudio_base}")

    # Crear instancia de LLM con los argumentos que CrewAI espera
    llm = LLM(
        model="lm_studio/meta-llama-3.1-8b-instruct",
        base_url="http://localhost:11434/v1",  # Asegurarse de que la URL termina en /v1
        api_key="lm-studio",
        timeout=600,
        # Otros parámetros opcionales:
        # max_tokens=4096,
        # temperature=0.7,
        # top_p=0.9,
    )
    return llm


def main() -> bool:
    """
    Prueba de creación del LLM optimizado.
    """
    try:
        print("Probando LLM optimizado para respuestas largas...")
        llm = crear_llm_crewai()
        print("LLM optimizado creado exitosamente:")
        print(f"  • Modelo   : {llm.model}")
        print(f"  • Base URL : {llm.base_url}")
        print(f"  • Timeout  : {llm.timeout} segundos")
        return True
    except Exception as e:
        print(f"Error configurando LLM: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
