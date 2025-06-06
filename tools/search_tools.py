#!/usr/bin/env python3
# proyecto_crewai/tools/search_tools.py

import os
import sys
from crewai.tools import tool
from dotenv import load_dotenv

# --- Import Streamlit for error reporting if key is missing ---
# This is generally not ideal for a tools module but helps debug in Streamlit context.
# Consider a more robust logging or error propagation for non-Streamlit use.
try:
    import streamlit as st
except ImportError:
    st = None # type: ignore

# Cargar variables de entorno desde .env de forma más robusta
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    # print(f"[DEBUG] Loaded .env file from: {dotenv_path}") # Optional: for confirming .env load
else:
    print(f"[WARNING] .env file not found at: {dotenv_path}")
    if st:
        st.warning(f".env file not found at project root. SERPER_API_KEY might be missing.")

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== FUNCIÓN BASE (para testing) ====================

def _buscar_web_base(query: str) -> str:
    """Función base para buscar en la web (sin decorador @tool)"""
    try:
        # Importar dependencias necesarias
        try:
            import requests
        except ImportError as e:
            print(f"Error: Falta instalar dependencias: {e}")
            print("Instala con: pip install requests")
            return ""
        
        # API Key de Serper (obtenida de variable de entorno)
        SERPER_API_KEY = os.getenv("SERPER_API_KEY")
        
        if not SERPER_API_KEY:
            error_message = "Error: La variable de entorno SERPER_API_KEY no está configurada. Verifica tu archivo .env en la raíz del proyecto."
            print(error_message)
            if st: # Intenta mostrar en Streamlit si está disponible
                st.error("Configuración incompleta: SERPER_API_KEY no encontrada. Revisa tu archivo .env y reinicia la aplicación.")
            return error_message # Devuelve el error para que CrewAI lo maneje
            
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "gl": "es", # Código de país para España (resultados en español)
            "hl": "es"  # Código de idioma para español
        }
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        print(f"Realizando búsqueda web para: {query}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status() # Lanza excepción para errores HTTP
        
        search_results = response.json()
        print(f"Resultados de búsqueda recibidos (estado: {response.status_code})")
        
        # Procesar y formatear resultados
        formatted_results = f"Resultados de la búsqueda para '{query}':\\n\\n"
        
        if 'knowledgeGraph' in search_results:
            kg = search_results['knowledgeGraph']
            formatted_results += f"**Información Destacada ({kg.get('title', '')}):**\\n"
            if 'description' in kg:
                formatted_results += f"{kg['description']}\\n"
            if 'attributes' in kg:
                for attr, value in kg['attributes'].items():
                    formatted_results += f"- {attr.capitalize()}: {value}\\n"
            formatted_results += "\\n"

        if 'organic' in search_results:
            for item in search_results['organic'][:5]: # Limitar a los primeros 5 resultados
                formatted_results += f"**Título:** {item.get('title', 'N/A')}\\n"
                formatted_results += f"**Enlace:** {item.get('link', 'N/A')}\\n"
                formatted_results += f"**Snippet:** {item.get('snippet', 'N/A')}\\n\\n" # Corrected this line
        
        if not formatted_results.strip() or formatted_results == f"Resultados de la búsqueda para '{query}':\\n\\n":
            return "No se encontraron resultados relevantes."
            
        return formatted_results

    except requests.exceptions.HTTPError as http_err:
        # Intentar obtener más detalles del error desde la respuesta
        error_details = http_err.response.text if http_err.response else ''
        print(f"Error HTTP: {http_err} - {error_details}")
        return f"Error HTTP al buscar: {http_err} - {error_details}"
    except requests.exceptions.RequestException as req_err:
        print(f"Error de Red: {req_err}")
        return f"Error de red al buscar: {req_err}"
    except Exception as e:
        print(f"Error inesperado en búsqueda web: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error inesperado al buscar: {str(e)}"

# ==================== HERRAMIENTA PARA AGENTES ====================

@tool("buscar_web")
def buscar_web(query: str) -> str:
    """Realiza una búsqueda web utilizando la API de Google Serper.
    
    Args:
        query: La consulta de búsqueda.
    
    Returns:
        Una cadena formateada con los resultados de la búsqueda o un mensaje de error.
    """
    return _buscar_web_base(query)

# ==================== FUNCIÓN BASE IMAGEN (para testing) ====================

def _buscar_imagen_base(topic: str) -> str:
    """Función base para buscar y descargar imagen (sin decorador @tool)"""
    try:
        # Importar dependencias necesarias
        try:
            import requests
        except ImportError as e:
            print(f"Error: Falta instalar dependencias: {e}")
            print("Instala con: pip install requests")
            return ""
        
        # API Key de Serper (obtenida de variable de entorno)
        SERPER_API_KEY = os.getenv("SERPER_API_KEY")

        if not SERPER_API_KEY:
            error_message = "Error: La variable de entorno SERPER_API_KEY no está configurada para búsqueda de imágenes. Verifica tu archivo .env."
            print(error_message)
            if st: # Intenta mostrar en Streamlit si está disponible
                st.error("Configuración incompleta: SERPER_API_KEY no encontrada para búsqueda de imágenes. Revisa tu archivo .env y reinicia.")
            return error_message # Devuelve el error para que CrewAI lo maneje

        url = "https://google.serper.dev/images"
        payload = {
            "q": f"{topic} high quality",
            "gl": "es",
            "hl": "es"
        }
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        print(f"Buscando imagen para: {topic}")
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        image_results = response.json()
        print(f"Resultados de imágenes recibidos (estado: {response.status_code})")
        
        if 'images' in image_results and image_results['images']:
            # Intentar descargar la primera imagen válida
            for img_data in image_results['images'][:5]: # Intentar con las primeras 5
                image_url = img_data.get('imageUrl')
                if not image_url:
                    continue
                
                try:
                    print(f"Descargando imagen desde: {image_url}")
                    img_response = requests.get(image_url, timeout=10, stream=True)
                    img_response.raise_for_status()
                    
                    # Determinar extensión y nombre de archivo
                    content_type = img_response.headers.get('Content-Type')
                    if content_type and 'image/jpeg' in content_type:
                        ext = '.jpg'
                    elif content_type and 'image/png' in content_type:
                        ext = '.png'
                    elif content_type and 'image/gif' in content_type:
                        ext = '.gif'
                    else:
                        # Si no se puede determinar, intentar por la URL o usar .jpg
                        parsed_url = requests.utils.urlparse(image_url) # type: ignore
                        path_ext = os.path.splitext(parsed_url.path)[1]
                        if path_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                            ext = path_ext
                        else:
                            ext = '.jpg' # Por defecto
                            print(f"No se pudo determinar la extensión de la imagen desde Content-Type o URL, usando {ext}")
                    
                    # Crear directorio temp si no existe
                    if not os.path.exists("temp"):
                        os.makedirs("temp")
                        print("Directorio 'temp' creado.")
                    
                    image_path = os.path.join("temp", f"temp_image{ext}")
                    
                    # Eliminar imagen anterior si existe con otra extensión
                    for old_ext in ['.jpg', '.png', '.jpeg', '.gif']:
                        old_file = os.path.join("temp", f"temp_image{old_ext}")
                        if os.path.exists(old_file) and old_file != image_path:
                            try:
                                os.remove(old_file)
                                print(f"Imagen anterior eliminada: {old_file}")
                            except Exception as e_rem:
                                print(f"Error eliminando imagen anterior {old_file}: {e_rem}")
                                
                    with open(image_path, 'wb') as f:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"Imagen descargada y guardada en: {image_path}")
                    return f"Imagen descargada y guardada en {image_path}"
                
                except requests.exceptions.RequestException as img_req_err:
                    print(f"Error descargando imagen desde {image_url}: {img_req_err}")
                    continue # Intentar con la siguiente imagen
                except Exception as e_img_proc:
                    print(f"Error procesando imagen desde {image_url}: {e_img_proc}")
                    continue
            
            return "No se pudo descargar ninguna imagen válida de los resultados."
        else:
            return "No se encontraron imágenes para el tema."

    except requests.exceptions.HTTPError as http_err:
        # Intentar obtener más detalles del error desde la respuesta
        error_details = http_err.response.text if http_err.response else ''
        print(f"Error HTTP: {http_err} - {error_details}")
        return f"Error HTTP al buscar imagen: {http_err} - {error_details}"
    except requests.exceptions.RequestException as req_err:
        print(f"Error de Red: {req_err}")
        return f"Error de red al buscar imagen: {req_err}"
    except Exception as e:
        print(f"Error inesperado en búsqueda de imagen: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error inesperado al buscar imagen: {str(e)}"

# ==================== HERRAMIENTA IMAGEN PARA AGENTES ====================

@tool("BuscadorDeImagenes")
def buscar_y_descargar_imagen(topic: str) -> str:
    """Busca una imagen relevante para el tema usando Google Serper y la descarga.
    
    Args:
        topic: El tema para el cual buscar una imagen.
    
    Returns:
        Una cadena con la ruta de la imagen descargada o un mensaje de error.
    """
    return _buscar_imagen_base(topic)


# ==================== FUNCIONES DE UTILIDAD ====================

def get_search_tools():
    """
    Devuelve una lista de herramientas de búsqueda para usar en agentes
    """
    return [buscar_web, buscar_y_descargar_imagen]


def _test_search_base(api_key_present: bool):
    print("\\n🧪 Probando búsqueda web...")
    if not api_key_present:
        print("⚠️  Saltando prueba de búsqueda web porque SERPER_API_KEY no está configurada.")
    else:
        resultado_busqueda = _buscar_web_base("inteligencia artificial")
        print(f"Resultado búsqueda: {resultado_busqueda[:200]}...") # Mostrar solo una parte

    print("\\n🖼️ Probando búsqueda de imágenes...")
    if not api_key_present:
        print("⚠️  Saltando prueba de búsqueda de imágenes porque SERPER_API_KEY no está configurada.")
    else:
        resultado_imagen = _buscar_imagen_base("gatos")
        print(f"Resultado imagen: {resultado_imagen}")


def main():
    """
    Función main para probar las herramientas de búsqueda
    """
    print("🔧 Iniciando pruebas de search_tools.py...")
    
    # Verificar si la API key está disponible para las pruebas
    api_key = os.getenv("SERPER_API_KEY")
    if api_key:
        print(f"🔑 SERPER_API_KEY encontrada (primeros 10 chars): {api_key[:10]}...")
        api_key_present = True
    else:
        print("⚠️ SERPER_API_KEY no encontrada en las variables de entorno.")
        print("   Las pruebas que dependen de la API KEY podrían no funcionar completamente o ser omitidas.")
        print("   Asegúrate de tener un archivo .env en la raíz del proyecto con SERPER_API_KEY='tu_clave_aqui'")
        api_key_present = False

    _test_search_base(api_key_present)
    
    print("\\n✅ Pruebas de search_tools.py completadas.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
