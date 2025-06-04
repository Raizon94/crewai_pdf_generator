#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import codecs
from crewai.tools import tool
from pathlib import Path
    
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
    print(f"[DEBUG] Primeros 200 chars: {str(content)[:200]}...")
    
    original_content = content
    
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
    
    # Decodificar escapes Unicode ANTES de procesar JSON
    if isinstance(content, str) and '\\u' in content:
        try:
            # Primero intentar decodificar los escapes Unicode
            content = content.encode('utf-8').decode('unicode_escape')
            print(f"[DEBUG] Después de decodificar Unicode: {content[:200]}...")
        except Exception as e:
            print(f"[DEBUG] Error decodificando Unicode (método 1): {e}")
            try:
                # Método alternativo para decodificar Unicode
                content = codecs.decode(content, 'unicode_escape')
                print(f"[DEBUG] Después de decodificar Unicode (método 2): {content[:200]}...")
            except Exception as e2:
                print(f"[DEBUG] Error decodificando Unicode (método 2): {e2}")
    
    # Extraer contenido si es JSON - DESPUÉS de decodificar Unicode
    if isinstance(content, str) and content.strip().startswith('{') and content.strip().endswith('}'):
        try:
            print("[DEBUG] Intentando parsear como JSON...")
            data = json.loads(content)
            
            if isinstance(data, dict):
                # Buscar todas las claves que contengan texto largo
                all_texts = []
                
                def extract_text_recursively(obj, key_path=""):
                    """Extraer texto recursivamente de un objeto JSON"""
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            new_path = f"{key_path}.{key}" if key_path else key
                            extract_text_recursively(value, new_path)
                    elif isinstance(obj, str) and len(obj.strip()) > 10:
                        print(f"[DEBUG] Texto encontrado en {key_path}: {len(obj)} chars")
                        all_texts.append(obj)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            extract_text_recursively(item, f"{key_path}[{i}]")
                
                extract_text_recursively(data)
                
                if all_texts:
                    # Unir todos los textos encontrados
                    content = '\n\n'.join(all_texts)
                    print(f"[DEBUG] Textos combinados: {len(content)} chars total")
                else:
                    # Si no se encuentra texto, usar el JSON completo como string
                    content = str(data)
                    
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Error parseando JSON: {e}")
            # Si no es JSON válido, usar el contenido tal como está
        except Exception as e:
            print(f"[DEBUG] Error procesando JSON: {e}")
    
    # Limpiar caracteres problemáticos que pueden quedar
    if isinstance(content, str):
        # Reemplazar comillas problemáticas
        content = content.replace('\\"', '"')
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        
        # Limpiar espacios y saltos de línea excesivos
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
    
    # Verificar que tenemos contenido válido
    if not content or len(content) < 10:
        print(f"[DEBUG] Contenido muy corto. Original: {original_content[:500]}...")
        return f"❌ Error: Contenido muy corto o vacío. Recibido: '{content[:100]}...'"
    
    print(f"[DEBUG] Contenido final a escribir: {len(content)} chars")
    print(f"[DEBUG] Primeras líneas del contenido final:\n{content[:300]}...")
    
    # Asegurar codificación correcta al escribir
    temp_dir = os.path.join("temp")
    file_path = os.path.join(temp_dir, "temp_markdown.md")
    file_path = str(Path(file_path).expanduser().resolve())
    
    try:
        os.makedirs(temp_dir, exist_ok=True)
        
        # Escribir con codificación UTF-8 explícita
        with codecs.open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{content}\n\n")
        
        # Verificar estadísticas del contenido añadido
        added_words = len(content.split())
        added_lines = len(content.splitlines())
        
        # Verificar estadísticas totales del archivo
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            total_words = len(full_content.split())
            total_lines = len(full_content.splitlines())
        
        return f"✅ Contenido añadido exitosamente. Añadido: {added_words} palabras, {added_lines} líneas. Total: {total_words} palabras, {total_lines} líneas."
        
    except Exception as e:
        print(f"[DEBUG] Error escribiendo archivo: {e}")
        return f"❌ Error escribiendo archivo: {str(e)}"