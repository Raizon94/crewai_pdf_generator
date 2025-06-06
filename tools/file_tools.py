#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import codecs
from pathlib import Path
from crewai.tools import tool

@tool("append_to_markdown")
def append_to_markdown(content: str, **kwargs) -> str:
    """
    Herramienta simplificada para añadir contenido markdown al final de temp/temp_markdown.md.

    Esta versión detecta si el parámetro `content` es un JSON válido con una clave "content"
    y, en ese caso, extrae sólo ese valor; de lo contrario, añade el texto tal cual.

    Args:
        content (str): Contenido markdown a añadir (o bien un JSON con clave "content").
        **kwargs: Parámetros adicionales (se ignoran en esta versión).

    Returns:
        str: Mensaje de confirmación con estadísticas básicas.
    """

    # Intento de parsear `content` como JSON
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "content" in data:
            full_content = data["content"]
        else:
            # Si no es un dict con "content", uso el texto tal cual
            full_content = content
    except json.JSONDecodeError:
        # Si no es JSON, añado el texto directamente
        full_content = content

    # Ruta al archivo temp/temp_markdown.md (igual que antes)
    file_path = Path("temp") / "temp_markdown.md"
    os.makedirs(file_path.parent, exist_ok=True)

    # Escribo el contenido extraído (o el original) al final del fichero
    with codecs.open(file_path, "a", "utf-8") as f:
        f.write(full_content)
        f.write("\n")

    # Lectura completa del archivo para calcular estadísticas
    with codecs.open(file_path, "r", "utf-8") as f:
        texto_completo = f.read()

    palabras_nuevas = len(full_content.split())
    lineas_nuevas = len(full_content.splitlines())
    total_palabras = len(texto_completo.split())
    total_lineas = len(texto_completo.splitlines())

    return (
        f"✅ Contenido añadido: {palabras_nuevas} palabras, {lineas_nuevas} líneas. "
        f"Total ahora: {total_palabras} palabras, {total_lineas} líneas."
    )