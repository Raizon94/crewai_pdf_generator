#!/usr/bin/env python3
# proyecto_crewai/flows/documento_flow.py (FLUJO CORREGIDO)

import os
import sys
import shutil
import re
from crewai.flow.flow import Flow, start, listen, router
from crewai import Crew, Process, Agent, Task
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.estructurador import crear_agente_estructurador, crear_tarea_estructurar
    from agents.buscador import crear_agente_buscador_automatico, crear_tarea_investigacion_automatica
    from agents.escritor import crear_agente_escritor, crear_tarea_redaccion_archivo
    from tools.search_tools import _buscar_imagen_base
    from tools.pdf_tool import _generar_pdf_base
except ImportError as e:
    print(f"[ERROR] No se pudieron importar las dependencias: {e}")
    sys.exit(1)

# ==================== ESTADO DEL FLUJO ====================

class DocumentoState(BaseModel):
    topic: str = ""
    estructura_completa: str = ""
    secciones_lista: list = []
    seccion_actual: int = 0
    archivo_markdown: str = "temp/temp_markdown.md"
    imagen_portada: str = "temp/temp_image.jpg"
    pdf_final: str = ""
    total_secciones: int = 0
    contenido_antes_seccion: str = ""


# ==================== FLOW CORREGIDO ====================

class DocumentoFlowCompleto(Flow[DocumentoState]):
    
    @start()
    def limpiar_y_crear_estructura_documento(self):
        """Paso 1: Limpiar temp y crear estructura del documento"""
        print(f"🚀 INICIANDO FLUJO DE DOCUMENTACIÓN COMPLETO")
        print(f"📋 Tema: {self.state.topic}")
        
        # LIMPIAR CARPETA TEMP
        print(f"\n🧹 LIMPIEZA INICIAL - Eliminando contenido de carpeta temp")
        if os.path.exists("temp"):
            try:
                shutil.rmtree("temp")
                print(f"🗑️ Carpeta temp eliminada completamente")
            except Exception as e:
                print(f"⚠️ Error eliminando carpeta temp: {e}")
        
        # Crear carpeta temp limpia
        os.makedirs("temp", exist_ok=True)
        print(f"📁 Carpeta temp creada limpia")
        
        print(f"\n📋 PASO 1: ESTRUCTURADOR - Creando estructura del documento")
        
        # Usar agente estructurador
        agente = crear_agente_estructurador()
        tarea = crear_tarea_estructurar(self.state.topic)
        
        crew = Crew(
            agents=[agente],
            tasks=[tarea],
            process=Process.sequential,
            verbose=True
        )
        
        resultado = crew.kickoff(inputs={"topic": self.state.topic})
        self.state.estructura_completa = resultado.raw if hasattr(resultado, 'raw') else str(resultado)
        
        # Extraer lista de secciones para iterar
        secciones = []
        for line in self.state.estructura_completa.split('\n'):
            if line.strip().startswith('## ') and not line.strip().startswith('### '):
                seccion = line.strip()[3:].strip()
                # Filtrar secciones numéricas y referencias
                if seccion and not seccion.lower().startswith('referencias') and not seccion.lower().startswith('conclusiones'):
                    # Limpiar numeración si existe
                    if seccion.split('.')[0].strip().isdigit():
                        seccion = '.'.join(seccion.split('.')[1:]).strip()
                    if seccion:
                        secciones.append(seccion)
        
        self.state.secciones_lista = secciones
        self.state.total_secciones = len(secciones)
        self.state.seccion_actual = 0
        
        # Inicializar archivo temporal con título
        titulo_documento = f"# {self.state.topic}\n\n"
        try:
            with open(self.state.archivo_markdown, 'w', encoding='utf-8') as f:
                f.write(titulo_documento)
            print(f" Archivo temporal iniciado con título: {self.state.archivo_markdown}")
        except Exception as e:
            print(f"Error escribiendo título en archivo temporal: {e}")
        
        print(f"✅ Estructura creada con {self.state.total_secciones} secciones:")
        for i, seccion in enumerate(secciones, 1):
            print(f"   {i}. {seccion}")
        
        # CORRECCIÓN: Cambiar el return para evitar conflictos de nombres
        return "continuar_siguiente_seccion"
    
    @listen(limpiar_y_crear_estructura_documento)
    def procesar_seccion_individual(self, _):
        """Paso 2: Procesar una sección individual"""
        print(f"\nPASO 2: PROCESAMIENTO DE SECCIONES INDIVIDUALES")
        
        # Verificar si hemos terminado todas las secciones
        if self.state.seccion_actual >= len(self.state.secciones_lista):
            print(f"\n✅ TODAS LAS SECCIONES HAN SIDO COMPLETADAS")
            return "todas_secciones_completadas"
        
        seccion_actual = self.state.secciones_lista[self.state.seccion_actual]
        print(f"\nPROCESANDO SECCIÓN {self.state.seccion_actual + 1}/{self.state.total_secciones}: {seccion_actual}")
        
        
        # Guardar contenido antes de procesar
        if os.path.exists(self.state.archivo_markdown):
            with open(self.state.archivo_markdown, 'r', encoding='utf-8') as f:
                self.state.contenido_antes_seccion = f.read()
        
        # Crear y ejecutar crew para esta sección
        agente_buscador = crear_agente_buscador_automatico()
        agente_escritor = crear_agente_escritor()
        tasks = []
        for i, section in enumerate(self.state.secciones_lista):

            tarea_investigacion = crear_tarea_investigacion_automatica(
                section, 
                self.state.topic,
                agente_buscador
            )
            
            tarea_redaccion = crear_tarea_redaccion_archivo(
                agente_escritor,
                section,
                self.state.topic
            )
            tarea_redaccion.context = [tarea_investigacion]
            tasks.append(tarea_investigacion)
            tasks.append(tarea_redaccion)
        
        crew_seccion = Crew(
            agents=[agente_buscador, agente_escritor],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        crew_seccion.kickoff(inputs={
            "topic": self.state.topic,
            "seccion": seccion_actual
        })
        

        return "seccion_procesada"
    
    

    @listen(procesar_seccion_individual)
    def buscar_imagen_portada(self, _):
        """Paso 3: Buscar imagen de portada"""
        print(f"\nPASO 3: BÚSQUEDA DE IMAGEN - Buscando imagen de portada")
        print(f"Secciones procesadas: {self.state.seccion_actual}/{self.state.total_secciones}")
        
        try:
            imagen_path = _buscar_imagen_base(self.state.topic)
            if imagen_path and "descargada:" in imagen_path:
                filename = imagen_path.split(":")[-1].strip()
                if os.path.exists(filename):
                    self.state.imagen_portada = filename
                    print(f"🖼️ Imagen de portada descargada: {filename}")
                else:
                    print(f"⚠️ No se pudo encontrar imagen descargada: {filename}")
                    self.state.imagen_portada = ""
            else:
                print(f"⚠️ No se pudo descargar imagen para: {self.state.topic}")
                self.state.imagen_portada = ""
        except Exception as e:
            print(f"Error buscando imagen: {e}")
            self.state.imagen_portada = ""
        
        return "imagen_buscada"
    
    @listen(buscar_imagen_portada)
    def compilar_documento_final(self, _):
        """Paso 4: COMPILACIÓN FINAL - Crear PDF con imagen de portada"""
        print(f"\nPASO 4: COMPILACIÓN FINAL - Creando PDF")
        
        if not os.path.exists(self.state.archivo_markdown):
            print(f" Error: Archivo markdown no existe: {self.state.archivo_markdown}")
            return "error_compilacion"
        
        try:
            with open(self.state.archivo_markdown, 'r', encoding='utf-8') as f:
                contenido_markdown = f.read()
            
            print(f"📄 Generando PDF directamente...")
            pdf_path = _generar_pdf_base(
                contenido_markdown, 
                self.state.imagen_portada, 
                "temp/final_documento.pdf"
            )
            
            if pdf_path and os.path.exists(pdf_path):
                self.state.pdf_final = pdf_path
                print(f"PDF final generado: {self.state.pdf_final}")
            else:
                print(f"Error generando PDF")
            
        except Exception as e:
            print(f" Error en compilación final: {e}")
            return "error_compilacion"
        
        return "documento_completado"
    
    @listen(compilar_documento_final)
    def mover_pdf_y_mostrar_estadisticas_finales(self, _):
        """Paso 5: Mover PDF a carpeta output y mostrar estadísticas finales"""
        print(f"\nPASO 5: ORGANIZACIÓN FINAL - Moviendo PDF a carpeta output")
        
        os.makedirs("output", exist_ok=True)
        
        topic_clean = self.state.topic.replace(' ', '_').replace('/', '_').replace('\\', '_')
        pdf_final_name = f"{topic_clean}.pdf"
        pdf_output_path = f"output/{pdf_final_name}"
        
        if self.state.pdf_final and os.path.exists(self.state.pdf_final):
            try:
                shutil.move(self.state.pdf_final, pdf_output_path)
                self.state.pdf_final = pdf_output_path
                print(f"PDF movido a: {pdf_output_path}")
            except Exception as e:
                print(f"Error moviendo PDF: {e}")
        
        # Mostrar estadísticas finales
        print(f"\n" + "="*80)
        print(f"FLUJO COMPLETO FINALIZADO")
        print(f"="*80)
        print(f"Tema del documento: {self.state.topic}")
        print(f"Total de secciones procesadas: {self.state.total_secciones}")
        
        if os.path.exists(self.state.archivo_markdown):
            with open(self.state.archivo_markdown, 'r', encoding='utf-8') as f:
                contenido = f.read()
                palabras = len(contenido.split())
                lineas = len(contenido.split('\n'))
            print(f"📊 Estadísticas del documento:")
            print(f"   • Palabras: {palabras}")
            print(f"   • Líneas: {lineas}")
        
        if self.state.pdf_final and os.path.exists(self.state.pdf_final):
            print(f"📄 PDF final: {self.state.pdf_final}")
            size_bytes = os.path.getsize(self.state.pdf_final)
            size_mb = size_bytes / (1024 * 1024)
            print(f"   • Tamaño: {size_bytes} bytes ({size_mb:.2f} MB)")
        
        print(f"Flujo completo finalizado exitosamente")
        print(f"="*80)

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para ejecutar el flujo completo corregido"""
    topic = "Inteligencia Artificial en la Medicina"
    
    flow = DocumentoFlowCompleto()
    flow.state.topic = topic
    
    print(f"INICIANDO FLUJO DE DOCUMENTACIÓN CORREGIDO")
    print(f"Tema: {topic}")
    
    flow.kickoff()
    
    print("FLOW COMPLETADO CORRECTAMENTE")

if __name__ == "__main__":
    main()
