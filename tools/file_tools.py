#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
from crewai.tools import tool
from pathlib import Path

@tool("append_to_markdown")
def append_to_markdown(content: str, **kwargs) -> str:
    """
    Herramienta simplificada para añadir contenido markdown al final de temp/temp_markdown.md.
    
    Args:
        content (str): Contenido markdown a añadir.
        **kwargs: Parámetros adicionales que se concatenarán al contenido.
    
    Returns:
        str: Mensaje de confirmación con estadísticas básicas.
    """

    # Concatenar todos los parámetros adicionales al contenido principal
    full_content = content
    if kwargs:
        for key, value in kwargs.items():
            if isinstance(value, str) and value.strip():
                full_content += f" {value}"

    # Ruta al archivo markdown
    temp_dir = os.path.join("temp")
    file_path = os.path.join(temp_dir, "temp_markdown.md")
    file_path = str(Path(file_path).expanduser().resolve())

    try:
        os.makedirs(temp_dir, exist_ok=True)
        with codecs.open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{full_content}\n\n")

        # Calcular estadísticas simples
        added_words = len(full_content.split())
        added_lines = len(full_content.splitlines())

        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            full = f.read()
            total_words = len(full.split())
            total_lines = len(full.splitlines())

        return (
            f"✅ Contenido añadido: {added_words} palabras, {added_lines} líneas. "
            f"Total ahora: {total_words} palabras, {total_lines} líneas."
        )

    except Exception as e:
        return f"❌ Error al escribir el archivo: {e}"