#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
from pathlib import Path
from crewai.tools import tool

@tool("append_to_markdown")
def append_to_markdown(content: str, **kwargs) -> str:
    """
    Herramienta para añadir cualquier cosa (sin filtrar ni parsear) al final de temp/temp_markdown.md.

    Ahora acepta cualquier tipo de entrada y la convierte a str para no borrar ni omitir nada.

    Args:
        content: Cualquier dato que se reciba. Se convertirá a string y se añadirá verbatim.
        **kwargs: Parámetros adicionales (se ignoran).

    Returns:
        str: Mensaje de confirmación con estadísticas básicas.
    """
    # Convertimos exactamente lo que venga a string
    full_content = str(content)

    # Ruta al archivo temp/temp_markdown.md
    file_path = Path("temp") / "temp_markdown.md"
    os.makedirs(file_path.parent, exist_ok=True)

    # Escribir el contenido al final del fichero sin filtrar nada
    with codecs.open(file_path, "a", "utf-8") as f:
        f.write(full_content)
        f.write("\n")

    # Leer todo el fichero para estadísticas
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