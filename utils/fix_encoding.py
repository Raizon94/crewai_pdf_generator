#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs
import re

def fix_markdown_encoding():
    """Corrige la codificación y limpia el archivo markdown"""
    file_path = "temp/temp_markdown.md"
    
    if not os.path.exists(file_path):
        return "Archivo no encontrado"
    
    # Leer el archivo como bytes
    with open(file_path, 'rb') as f:
        content_bytes = f.read()
    
    # Decodificar como latin-1
    content = content_bytes.decode('latin-1')
    
    # Reemplazos de caracteres mal codificados
    replacements = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã±': 'ñ', 'Ã': 'Á', 'Ã‰': 'É', 'Ã': 'Í', 'Ã“': 'Ó',
        'Ãš': 'Ú', 'Ã‘': 'Ñ', 'Ã¼': 'ü', 'Ã§': 'ç',
        'â€™': '’', 'â€œ': '“', 'â€': '”', 'â€“': '–', 'â€”': '—',
        'â€˜': '‘', 'â€¢': '•', 'â€¦': '…', 'â€': '"', 'â': '"',
        'Âº': 'º', 'Â': '', '�': ''
    }
    for wrong, correct in replacements.items():
        content = content.replace(wrong, correct)
    
    # Eliminar comentarios HTML tipo <!-- ... -->
    content = re.sub(r'<!--.*?-->\s*', '', content, flags=re.DOTALL)
    
    # Eliminar residuos como ”} o "} al final de línea o párrafo
    content = re.sub(r'[”"}]+\s*$', '', content, flags=re.MULTILINE)
    
    # Eliminar líneas vacías múltiples
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Strip general
    content = content.strip() + '\n'
    
    # Backup
    backup_path = f"{file_path}.backup"
    os.rename(file_path, backup_path)
    
    # Guardar limpio en UTF-8
    with codecs.open(file_path, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    return f"✅ Archivo corregido, limpio y guardado en UTF-8. Backup en {backup_path}"

if __name__ == "__main__":
    result = fix_markdown_encoding()
    print(result)