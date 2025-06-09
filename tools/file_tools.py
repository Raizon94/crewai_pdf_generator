#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import codecs
from pathlib import Path
from crewai.tools import tool

@tool("append_to_markdown")
def append_to_markdown(content: str):
    """
    Herramienta para añadir contenido JSON parseado al final de temp/temp_markdown.md.
    
    Parsea el JSON recibido y extrae el contenido de texto real,
    manejando correctamente los caracteres Unicode escapados.

    Args:
        content: String que contiene el contenido a procesar
        

    Returns:
        str: Mensaje de confirmación con estadísticas básicas.
    """
    
   
    
    
    
    # Ruta al archivo temp/temp_markdown.md
    file_path = Path("temp") / "temp_markdown.md"
    os.makedirs(file_path.parent, exist_ok=True)

    # Escribir el contenido parseado al final del fichero
    with codecs.open(file_path, "a", "utf-8") as f:
        f.write(content)
        f.write("\n\n")  # Doble salto de línea para separar contenidos

    return f"Contenido añadido exsitosamente"