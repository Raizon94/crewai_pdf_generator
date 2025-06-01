#!/usr/bin/env python3
# proyecto_crewai/tools/pdf_tool.py

import os
import sys
from crewai.tools import tool

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== FUNCIÓN BASE (para testing) ====================

def _generar_pdf_base(markdown_content: str, imagen_portada: str = None, output_pdf_path: str = "temp/final_documento.pdf") -> str:
    """Función base para generar PDF (sin decorador @tool)"""
    try:
        # Importar dependencias necesarias
        try:
            from weasyprint import HTML, CSS
            import markdown
        except ImportError as e:
            print(f"Error: Falta instalar dependencias: {e}")
            print("Instala con: pip install weasyprint markdown")
            return ""
        
        # Verificar y usar imagen de portada por defecto si existe
        if not imagen_portada or not os.path.exists(imagen_portada):
            # Buscar imagen de portada en ubicaciones comunes
            imagenes_posibles = [
                "temp/temp_image.jpg",
                "temp/temp_image.png", 
                "temp/temp_image.jpeg",
                "portada.jpg",
                "portada.png"
            ]
            
            imagen_portada = None
            for img_path in imagenes_posibles:
                if os.path.exists(img_path):
                    imagen_portada = img_path
                    print(f"Usando imagen de portada encontrada: {img_path}")
                    break
            
            if not imagen_portada:
                print("No se encontró imagen de portada, generando PDF sin imagen")
        else:
            print(f"Usando imagen de portada: {imagen_portada}")
        
        # Convertir markdown a HTML
        print("Convirtiendo markdown a HTML...")
        html_content = markdown.markdown(
            markdown_content, 
            extensions=['tables', 'toc', 'fenced_code', 'codehilite']
        )
        
        # CSS mejorado para el PDF
        css_styles = """
        @page {
            margin: 2.5cm;
            size: A4;
            @bottom-center {
                content: counter(page);
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            font-size: 11pt;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            font-size: 24pt;
            page-break-before: always;
        }
        
        h1:first-of-type {
            page-break-before: avoid;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 25px;
            font-size: 18pt;
        }
        
        h3 {
            color: #7f8c8d;
            margin-top: 20px;
            font-size: 14pt;
        }
        
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 15px;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        code {
            background-color: #f8f9fa;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
            margin: 15px 0;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table th, table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        .portada {
            text-align: center;
            page-break-after: always;
            padding-top: 50px;
            padding-bottom: 50px;
            min-height: 80vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .portada img {
            max-width: 500px;
            max-height: 400px;
            height: auto;
            width: auto;
            margin-bottom: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        .portada h1 {
            font-size: 32pt;
            margin-top: 20px;
            margin-bottom: 20px;
            border: none;
            page-break-before: avoid;
            color: #2c3e50;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .portada .fecha {
            font-size: 14pt;
            color: #7f8c8d;
            margin-top: 30px;
            font-style: italic;
        }
        """
        
        # Crear portada si hay imagen
        portada_html = ""
        if imagen_portada and os.path.exists(imagen_portada):
            # Obtener título del markdown (primera línea que empiece con #)
            titulo = "Documento"
            for line in markdown_content.split('\n'):
                line = line.strip()
                if line.startswith('# '):
                    titulo = line[2:].strip()
                    break
            
            # Obtener fecha actual
            from datetime import datetime
            fecha_actual = datetime.now().strftime("%B %Y")
            
            # Convertir imagen a base64 para WeasyPrint
            import base64
            try:
                with open(imagen_portada, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    
                    # Detectar tipo de imagen
                    img_ext = os.path.splitext(imagen_portada)[1].lower()
                    if img_ext in ['.jpg', '.jpeg']:
                        mime_type = 'image/jpeg'
                    elif img_ext == '.png':
                        mime_type = 'image/png'
                    elif img_ext == '.gif':
                        mime_type = 'image/gif'
                    else:
                        mime_type = 'image/jpeg'  # Por defecto
                    
                    img_src = f"data:{mime_type};base64,{img_base64}"
                    print(f"Imagen convertida a base64: {len(img_base64)} caracteres")
                    
                    portada_html = f"""
                    <div class="portada">
                        <img src="{img_src}" alt="Portada del documento">
                        <h1>{titulo}</h1>
                        <div class="fecha">{fecha_actual}</div>
                    </div>
                    """
                    print(f"Portada creada con título: '{titulo}'")
            except Exception as e:
                print(f"⚠️ Error procesando imagen: {e}")
                # Crear portada sin imagen
                portada_html = f"""
                <div class="portada">
                    <h1>{titulo}</h1>
                    <div class="fecha">{fecha_actual}</div>
                </div>
                """
                print(f"Portada creada sin imagen con título: '{titulo}'")
        else:
            # No hay imagen o no existe, crear portada simple
            titulo = "Documento"
            for line in markdown_content.split('\n'):
                line = line.strip()
                if line.startswith('# '):
                    titulo = line[2:].strip()
                    break
            
            from datetime import datetime
            fecha_actual = datetime.now().strftime("%B %Y")
            
            portada_html = f"""
            <div class="portada">
                <h1>{titulo}</h1>
                <div class="fecha">{fecha_actual}</div>
            </div>
            """
            print(f"Portada creada sin imagen con título: '{titulo}'")
        
        # Construir HTML completo
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Documento PDF</title>
            <style>{css_styles}</style>
        </head>
        <body>
            {portada_html}
            {html_content}
        </body>
        </html>
        """
        
        # Crear directorio de salida si no existe
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            print(f"📁 Creando directorio: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
        
        # Generar PDF
        print(f"Generando PDF en: {output_pdf_path}")
        html_doc = HTML(string=full_html)
        pdf_path = output_pdf_path
        
        print(f"Escribiendo PDF...")
        html_doc.write_pdf(pdf_path)
        print(f"PDF escrito")
        
        # Verificar que se generó correctamente
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 Archivo generado: {pdf_path} ({file_size} bytes)")
            if file_size > 1000:
                return pdf_path
            else:
                print(f"Archivo muy pequeño: {file_size} bytes")
                return ""
        else:
            print(f"El archivo no existe: {pdf_path}")
            return ""
    except Exception as e:
        print(f"Error generando PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""


# ==================== HERRAMIENTA PARA AGENTES ====================

@tool("GeneradorPDF")
def generar_pdf_desde_markdown(markdown_content: str, imagen_portada: str = "temp/temp_image.jpg", output_pdf_path: str = "temp/final_documento.pdf") -> str:
    """Convierte contenido markdown a PDF usando WeasyPrint.
    
    Args:
        markdown_content: Contenido en formato markdown para convertir a PDF
        imagen_portada: Ruta opcional de imagen para incluir en la portada (por defecto temp/temp_image.jpg)
        output_pdf_path: Ruta de salida para el PDF generado (por defecto temp/final_documento.pdf)
    
    Returns:
        Ruta del archivo PDF generado, o cadena vacía si falla
    """
    return _generar_pdf_base(markdown_content, imagen_portada, output_pdf_path)


# ==================== FUNCIONES DE UTILIDAD ====================

def get_pdf_tool():
    """
    Devuelve la herramienta de generación de PDF para usar en agentes
    """
    return generar_pdf_desde_markdown


def main():
    """
    Función main para probar la generación de PDF
    """
    print("🧪 Probando generación de PDF...")
    
    # Markdown de ejemplo para testing
    markdown_ejemplo = """
# Documento de Prueba

## Introducción

Este es un **documento de prueba** para verificar que la generación de PDF funciona correctamente.

## Características

- Soporte para **texto en negrita** e *cursiva*
- Listas numeradas y con viñetas
- Código inline: `print("Hola mundo")`
- Enlaces y referencias

### Subsección

1. Primer elemento
2. Segundo elemento
3. Tercer elemento

## Código de ejemplo

def hello_world():
print("¡Hola desde Python!")
return True

## Tabla de ejemplo

| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Dato 1    | Dato 2    | Dato 3    |
| Valor A   | Valor B   | Valor C   |

## Conclusión

Este documento demuestra las capacidades de conversión de Markdown a PDF.

> "La simplicidad es la máxima sofisticación." - Leonardo da Vinci
"""
    
    try:
        # Probar generación sin imagen
        print("\n📄 Probando generación de PDF sin imagen...")
        resultado_sin_imagen = _generar_pdf_base(markdown_ejemplo)
        print(f"✅ {resultado_sin_imagen}")
        
        # Verificar si existe alguna imagen de portada del archivo anterior
        imagenes_posibles = [
            "portada_artificial_intelligence_technology.jpg",
            "portada_artificial_intelligence_technology.png",
            "portada_Inteligencia_Artificial.png"
        ]
        
        imagen_encontrada = None
        for img in imagenes_posibles:
            if os.path.exists(img):
                imagen_encontrada = img
                break
        
        if imagen_encontrada:
            print(f"\n🖼️  Probando generación de PDF con imagen: {imagen_encontrada}")
            resultado_con_imagen = _generar_pdf_base(markdown_ejemplo, imagen_encontrada)
            print(f"✅ {resultado_con_imagen}")
        else:
            print("\n⚠️  No se encontró imagen de portada, pero el PDF básico se generó correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
