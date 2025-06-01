#!/usr/bin/env python3
# proyecto_crewai/utils/llm_selector.py

import sys
import random

# Intentamos importar el cliente de Ollama en Python. 
# Si no está instalado, informamos al usuario.
try:
    import ollama
except ImportError:
    print(
        "[ERROR] No se encontró el módulo 'ollama' en Python.\n"
        "  • Instálalo con: pip install ollama\n"
        "  • O revisa que tu entorno virtual contenga 'ollama'.",
        file=sys.stderr
    )
    sys.exit(1)


def obtener_modelos_disponibles_ollama():
    """
    Llama al cliente de Ollama para obtener la lista de modelos
    instalados localmente. Devuelve una lista de cadenas con los nombres de los modelos.
    """
    try:
        modelos_info = ollama.list()
        # La respuesta tiene un atributo 'models' que contiene una lista de objetos Model
        modelos = [m.model for m in modelos_info.models]
        return modelos
    except Exception as e:
        # Puede fallar si el demonio no está corriendo o hay otro problema de conexión
        print(f"[ERROR] No se pudo conectar al servidor de Ollama: {e}", file=sys.stderr)
        return []


def seleccionar_llm():
    """
    Selecciona 'llama3:latest' si está en la lista de modelos disponibles.
    Si no está, selecciona uno al azar de la lista (si la lista no está vacía).
    Si no hay modelos instalados, lanza RuntimeError.
    """
    modelos = obtener_modelos_disponibles_ollama()
    if not modelos:
        raise RuntimeError(
            "No se encontró ningún modelo de Ollama instalado.\n"
            "  • Asegúrate de tener el demonio de Ollama corriendo (ejecuta 'ollama serve').\n"
            "  • Y/o que hayas descargado al menos un modelo (por ejemplo: 'ollama pull llama3:latest')."
        )
    if "gemma3:4b" in modelos:
        return "gemma3:4b"
    else:
        elegido = random.choice(modelos)
        print(f"[WARNING] 'gemma3:4b' no está instalado; usando modelo alternativo: {elegido}", file=sys.stderr)
        return elegido


if __name__ == "__main__":
    """
    Si ejecutas este archivo con `./utils/llm_selector.py`, entrará aquí.
    Imprime por pantalla el modelo elegido o el motivo del fallo.
    """
    try:
        modelo = seleccionar_llm()
        print(modelo)
        sys.exit(0)
    except Exception as e:
        print(f"Error al seleccionar modelo: {e}", file=sys.stderr)
        sys.exit(1)