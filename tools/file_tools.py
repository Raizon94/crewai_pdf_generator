#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import codecs
from crewai.tools import tool
    
@tool("append_to_markdown")
def append_to_markdown(content: str) -> str:
    """
    Herramienta para añadir contenido markdown al final del archivo temp/temp_markdown.md.
    
    Args:
        content (str): Contenido markdown (como string) a añadir al archivo.
    
    Returns:
        str: Mensaje de confirmación con estadísticas del archivo.
    """
    # Debug: Imprimir el tipo y contenido recibido
    print(f"[DEBUG] Tipo recibido: {type(content)}")
    print(f"[DEBUG] Contenido recibido: {content}")
    
    # Manejar caso donde se recibe un diccionario en lugar de string
    if isinstance(content, dict):
        print("[DEBUG] Recibido diccionario, intentando extraer contenido...")
        # Buscar claves comunes que podrían contener el contenido
        for key in ['content', 'text', 'markdown', 'description', 'value']:
            if key in content and isinstance(content[key], str):
                content = content[key]
                break
        else:
            # Si no se encuentra, convertir todo el diccionario a string
            content = str(content)
    
    # Convertir a string si no lo es
    if not isinstance(content, str):
        content = str(content)
    
    # Decodificar escapes Unicode antes de cualquier otro procesamiento
    if isinstance(content, str) and '\\u' in content:
        try:
            content = content.encode().decode('unicode_escape')
        except Exception as e:
            print(f"Error decodificando Unicode: {e}")
    
    # Extraer contenido si es JSON
    if isinstance(content, str) and content.strip().startswith('{') and content.strip().endswith('}'):
        try:
            data = json.loads(content)
            all_content = []
            
            # Procesar todas las claves del JSON
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 10:
                        all_content.append(value)
            
            if all_content:
                content = ''.join(all_content)
        except Exception as e:
            print(f"Error procesando JSON: {e}")
    
    # Limpiar el contenido final
    content = content.strip()
    
    # Verificar que tenemos contenido válido
    if not content or len(content) < 10:
        return f" Error: Contenido muy corto o vacío. Recibido: '{content[:100]}...'"
    
    # Asegurar codificación correcta al escribir
    file_path = "temp/temp_markdown.md"
    
    try:
        os.makedirs("temp", exist_ok=True)
        
        # Escribir con codificación UTF-8 explícita y BOM
        with codecs.open(file_path, 'a', encoding='utf-8-sig') as f:
            f.write(f"\n\n{content}\n\n")
        
        # Verificar estadísticas
        with codecs.open(file_path, 'r', encoding='utf-8-sig') as f:
            full_content = f.read()
            words = len(full_content.split())
            lines = len(full_content.splitlines())
        
        return f" Contenido añadido exitosamente. Estadísticas: {words} palabras, {lines} líneas."
        
    except Exception as e:
        return f" Error: {str(e)}"