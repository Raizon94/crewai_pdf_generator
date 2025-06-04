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
    print(f"[DEBUG] Longitud total: {len(str(content))} chars")
    print(f"[DEBUG] Primeros 300 chars: {str(content)[:300]}...")
    print(f"[DEBUG] Últimos 100 chars: ...{str(content)[-100:]}")
    
    original_content = content
    
    # Convertir a string si no lo es
    if not isinstance(content, str):
        content = str(content)
    
    # Decodificar escapes Unicode ANTES de cualquier procesamiento
    if '\\u' in content:
        try:
            content = content.encode('utf-8').decode('unicode_escape')
            print(f"[DEBUG] Después de decodificar Unicode: {len(content)} chars")
        except Exception as e:
            print(f"[DEBUG] Error decodificando Unicode: {e}")
    
    # NUEVO: Detectar si contiene estructura tipo JSON (aunque esté malformada)
    if content.strip().startswith('{') or '"content":' in content:
        print("[DEBUG] Detectado formato JSON/cuasi-JSON, procesando...")
        
        # Método 1: Intentar JSON válido primero
        json_processed = False
        if content.strip().startswith('{') and content.strip().endswith('}'):
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    all_texts = []
                    
                    def extract_all_text(obj):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                extract_all_text(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                extract_all_text(item)
                        elif isinstance(obj, str) and len(obj.strip()) > 10:
                            all_texts.append(obj.strip())
                    
                    extract_all_text(data)
                    
                    if all_texts:
                        content = '\n\n'.join(all_texts)
                        json_processed = True
                        print(f"[DEBUG] JSON válido procesado: {len(content)} chars")
                        
            except json.JSONDecodeError as e:
                print(f"[DEBUG] JSON inválido: {e}")
        
        # Método 2: Procesar JSON malformado con regex
        if not json_processed:
            print("[DEBUG] Procesando JSON malformado con regex...")
            
            # Extraer todos los valores entre comillas después de ":"
            # Patrón mejorado para capturar valores largos
            pattern = r':\s*"([^"]*(?:\\.[^"]*)*)"'
            matches = re.findall(pattern, content)
            
            if matches:
                extracted_texts = []
                for match in matches:
                    # Decodificar escapes en cada match
                    clean_text = match.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                    if len(clean_text.strip()) > 20:  # Solo textos significativos
                        extracted_texts.append(clean_text.strip())
                        print(f"[DEBUG] Texto extraído: {len(clean_text)} chars - {clean_text[:50]}...")
                
                if extracted_texts:
                    content = '\n\n'.join(extracted_texts)
                    print(f"[DEBUG] Regex procesado: {len(content)} chars de {len(extracted_texts)} fragmentos")
                    json_processed = True
            
            # Método 3: Si regex no funciona, extraer manualmente
            if not json_processed:
                print("[DEBUG] Usando extracción manual...")
                
                # Buscar el patrón {"content": "texto"
                content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)"', content)
                if content_match:
                    main_content = content_match.group(1)
                    
                    # Buscar más contenido después
                    remaining = content[content_match.end():]
                    additional_matches = re.findall(r':\s*"([^"]*(?:\\.[^"]*)*)"', remaining)
                    
                    all_parts = [main_content]
                    for match in additional_matches:
                        if len(match.strip()) > 20:
                            all_parts.append(match)
                    
                    # Limpiar y combinar
                    cleaned_parts = []
                    for part in all_parts:
                        clean_part = part.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                        if len(clean_part.strip()) > 10:
                            cleaned_parts.append(clean_part.strip())
                    
                    if cleaned_parts:
                        content = '\n\n'.join(cleaned_parts)
                        print(f"[DEBUG] Extracción manual: {len(content)} chars de {len(cleaned_parts)} partes")
                        json_processed = True
        
        if not json_processed:
            print("[DEBUG] No se pudo procesar como JSON, usando contenido original")
    
    # Limpiar caracteres problemáticos que puedan quedar
    if isinstance(content, str):
        content = content.replace('\\"', '"')
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', '\t')
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = content.strip()
    
    # Verificar que tenemos contenido válido
    if not content or len(content) < 10:
        print(f"[DEBUG] Contenido muy corto. Original completo: {original_content}")
        return f"❌ Error: Contenido muy corto o vacío. Recibido: '{content[:100]}...'"
    
    print(f"[DEBUG] Contenido final a escribir: {len(content)} chars")
    print(f"[DEBUG] Primeras líneas del contenido final:\n{content[:400]}...")
    
    # Escribir archivo
    temp_dir = os.path.join("temp")
    file_path = os.path.join(temp_dir, "temp_markdown.md")
    file_path = str(Path(file_path).expanduser().resolve())
    
    try:
        os.makedirs(temp_dir, exist_ok=True)
        
        with codecs.open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{content}\n\n")
        
        # Calcular estadísticas
        added_words = len(content.split())
        added_lines = len(content.splitlines())
        
        with codecs.open(file_path, 'r', encoding='utf-8') as f:
            full_content = f.read()
            total_words = len(full_content.split())
            total_lines = len(full_content.splitlines())
        
        print(f"[DEBUG] Estadísticas reales - Añadido: {added_words} palabras")
        
        return f"✅ Contenido añadido exitosamente. Añadido: {added_words} palabras, {added_lines} líneas. Total: {total_words} palabras, {total_lines} líneas."
        
    except Exception as e:
        print(f"[DEBUG] Error escribiendo archivo: {e}")
        return f"❌ Error escribiendo archivo: {str(e)}"