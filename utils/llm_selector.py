#!/usr/bin/env python3
# proyecto_crewai/utils/llm_selector.py

import sys
import random
import requests
import json
import os

def obtener_modelos_disponibles_lmstudio():
    """
    Llama a LM Studio para obtener la lista de modelos
    disponibles. Devuelve una lista de cadenas con los nombres de los modelos.
    """
    try:
        # Configurar host de LM Studio (por defecto localhost:11434)
        lmstudio_host = os.getenv('LMSTUDIO_HOST', 'localhost:11434')
        if not lmstudio_host.startswith('http'):
            lmstudio_host = f'http://{lmstudio_host}'
        
        # Hacer petición a la API de LM Studio
        url = f"{lmstudio_host}/v1/models"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parsear la respuesta JSON
        data = response.json()
        modelos = [model["id"] for model in data["data"]]
        return modelos
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] No se pudo conectar al servidor de LM Studio en {lmstudio_host}: {e}", file=sys.stderr)
        return []
    except (KeyError, json.JSONDecodeError) as e:
        print(f"[ERROR] Respuesta inesperada del servidor LM Studio: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] Error inesperado al conectar con LM Studio: {e}", file=sys.stderr)
        return []


def seleccionar_llm():
    """
    Selecciona 'gemma3:4b' si está en la lista de modelos disponibles.
    Si no está, selecciona uno al azar de la lista (si la lista no está vacía).
    Si no hay modelos disponibles, lanza RuntimeError.
    """
    modelos = obtener_modelos_disponibles_lmstudio()
    if not modelos:
        raise RuntimeError(
            "No se encontró ningún modelo en LM Studio.\n"
            "  • Asegúrate de tener LM Studio corriendo en localhost:11434.\n"
            "  • Y/o que hayas cargado al menos un modelo en LM Studio."
        )
    
    # Buscar modelo preferido (ajusta el nombre según LM Studio)
    modelo_preferido = "gemma3:4b"
    if modelo_preferido in modelos:
        return modelo_preferido
    else:
        elegido = random.choice(modelos)
        print(f"[WARNING] '{modelo_preferido}' no está disponible; usando modelo alternativo: {elegido}", file=sys.stderr)
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