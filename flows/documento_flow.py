#!/usr/bin/env python3
# proyecto_crewai/flows/documento_flow.py

import os
import sys
import shutil
from crewai.flow.flow import Flow, start, listen
from crewai import Crew, Process
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.estructurador import crear_agente_estructurador, crear_tarea_estructurar
    from agents.buscador import crear_agente_buscador_automatico, crear_tarea_investigacion_automatica
    from agents.escritor import crear_agente_escritor, crear_tarea_redaccion_archivo
    from tools.search_tools import _buscar_imagen_base
    from tools.pdf_tool import _generar_pdf_base
    from utils.llm_provider import crear_llm_crewai
except ImportError as e:
    print(f"[ERROR] No se pudieron importar las dependencias: {e}")
    sys.exit(1)


# ==================== ESTADO DEL FLUJO ====================

class DocumentoState(BaseModel):
    topic: str = ""
    modelo: str | None = None
    llm_global: object = Field(default=None, exclude=True)  # Excluir de serialización
    estructura_completa: str = ""
    secciones_lista: list[str] = []
    total_secciones: int = 0
    archivo_markdown: str = "temp/temp_markdown.md"
    imagen_portada: str = ""
    pdf_final: str = ""


# ==================== FLOW COMPLETO ====================

class DocumentoFlowCompleto(Flow[DocumentoState]):

    @start()
    def limpiar_y_crear_estructura_documento(self):
        """Paso 1: Limpiar carpeta temp, generar estructura y extraer lista de secciones."""
        print(f"INICIANDO FLUJO DE DOCUMENTACIÓN COMPLETO")
        print(f"Tema: {self.state.topic}")

        # 0. Crear instancia LLM global una sola vez
        print("Creando instancia LLM global...")
        self.state.llm_global = crear_llm_crewai(modelo_seleccionado=self.state.modelo)
        print("LLM global creado correctamente.")

        # 1. Limpiar carpeta temp
        if os.path.exists("temp"):
            try:
                shutil.rmtree("temp")
                print("Carpeta 'temp' eliminada completamente.")
            except Exception as e:
                print(f"Error eliminando carpeta 'temp': {e}")

        # 2. Crear carpeta temp vacía
        os.makedirs("temp", exist_ok=True)
        print("Carpeta 'temp' creada limpia.")

        # 3. Invocar agente estructurador para obtener la estructura completa
        print("\nPASO 1: ESTRUCTURADOR - Generando esquema del documento")
        agente_estructurador = crear_agente_estructurador(self.state.modelo, llm_instance=self.state.llm_global)
        tarea_estructurar = crear_tarea_estructurar(self.state.topic, agente_estructurador)

        crew_estruct = Crew(
            agents=[agente_estructurador],
            tasks=[tarea_estructurar],
            process=Process.sequential,
            verbose=True
        )
        resultado = crew_estruct.kickoff(inputs={"topic": self.state.topic})
        self.state.estructura_completa = resultado.raw if hasattr(resultado, "raw") else str(resultado)

        # 4. Extraer todas las cabeceras '## ' (nivel 2) excepto 'Referencias' y 'Conclusiones'
        secciones: list[str] = []
        for line in self.state.estructura_completa.split("\n"):
            text = line.strip()
            if text.startswith("## ") and not text.startswith("### "):
                título = text[3:].strip()
                título_min = título.lower()
                if título and not (título_min.startswith("referencias") or título_min.startswith("conclusiones")):
                    # Filtrar numeración del tipo "1. Introducción"
                    partes = título.split(".", 1)
                    if partes[0].strip().isdigit() and len(partes) > 1:
                        título = partes[1].strip()
                    secciones.append(título)
        self.state.secciones_lista = secciones
        self.state.total_secciones = len(secciones)

        print(f"\nEstructura detectada con {self.state.total_secciones} secciones:")
        for i, s in enumerate(self.state.secciones_lista, start=1):
            print(f"   {i}. {s}")

        # 5. Inicializar archivo Markdown con el título principal
        try:
            os.makedirs(os.path.dirname(self.state.archivo_markdown), exist_ok=True)
            with open(self.state.archivo_markdown, "w", encoding="utf-8") as f:
                f.write(f"# {self.state.topic}\n\n")
            print(f"Archivo Markdown iniciado en: {self.state.archivo_markdown}")
        except Exception as e:
            print(f"Error escribiendo el archivo Markdown: {e}")

        # Pasar al procesamiento de todas las secciones
        return "procesar_seccion"

    @listen(limpiar_y_crear_estructura_documento)
    def procesar_seccion(self, _):
        """
        Paso 2 (CORREGIDO): Crear agentes una vez, generar todas las tareas y ejecutarlas en un solo Crew.
        """
        print(f"\nPASO 2: Preparando el Crew para procesar todas las secciones")

        # 1. CREAR AGENTES UNA SOLA VEZ (FUERA DEL BUCLE)
        # Estos agentes se reutilizarán para todas las tareas y usarán la misma instancia LLM.
        agente_buscador = crear_agente_buscador_automatico(modelo=self.state.modelo, llm_instance=self.state.llm_global)
        agente_escritor = crear_agente_escritor(modelo=self.state.modelo, llm_instance=self.state.llm_global)

        # 2. GENERAR TODAS LAS TAREAS DINÁMICAMENTE
        # Creamos una lista para almacenar todas las tareas que se generarán.
        all_tasks = []
        
        # Se usará para encadenar la redacción con la investigación de la misma sección
        # y potencialmente con la redacción de la sección anterior para dar contexto.
        last_task = None 

        for idx, seccion in enumerate(self.state.secciones_lista):
            print(f"   Generando tareas para la sección {idx + 1}/{self.state.total_secciones}: '{seccion}'")

            # Tarea de investigación para la sección actual
            tarea_investigacion = crear_tarea_investigacion_automatica(
                seccion,
                self.state.topic,
                agente_buscador
            )

            # Tarea de redacción para la sección actual
            # Depende de la tarea de investigación de ESTA sección.
            tarea_redaccion = crear_tarea_redaccion_archivo(
                agente_escritor,
                seccion,
                self.state.topic
            )
            tarea_redaccion.context = [tarea_investigacion]

            # Opcional: Para mejorar la coherencia, puedes hacer que la redacción
            # de una sección dependa de la redacción de la anterior.
            # if last_task:
            #    tarea_redaccion.context.append(last_task)

            # Añadimos ambas tareas a nuestra lista global
            all_tasks.append(tarea_investigacion)
            all_tasks.append(tarea_redaccion)
            
            # Actualizamos la última tarea para la siguiente iteración
            last_task = tarea_redaccion

        # 3. CREAR Y EJECUTAR UN ÚNICO CREW CON TODAS LAS TAREAS
        # Este Crew contiene todos los agentes y la lista completa de tareas.
        # CrewAI gestionará el orden de ejecución basado en las dependencias (context).
        print("\nIniciando el Crew principal con todas las tareas generadas...")
        full_crew = Crew(
            agents=[agente_buscador, agente_escritor],
            tasks=all_tasks,
            process=Process.sequential,
            verbose=True,
            max_execution_time=1800,  # 30 minutos máximo para todo el crew
            step_callback=lambda step: print(f"[CREW STEP] {step.tool_name if hasattr(step, 'tool_name') else 'Procesando...'}")
        )

        # Ejecutamos el Crew una sola vez.
        resultado_final = full_crew.kickoff()
        
        print("\nTodas las secciones han sido procesadas por el Crew.")
        print("Resultado final del Crew:", resultado_final)

        # Avanzamos al siguiente paso del flujo
        return "todas_secciones_completadas"

    @listen(procesar_seccion)
    def buscar_imagen_portada(self, _):
        """Paso 3: Buscar imagen de portada para el documento completo."""
        print(f"\nPASO 3: BÚSQUEDA DE IMAGEN - Buscando imagen de portada para '{self.state.topic}'")
        print(f"Secciones procesadas: {self.state.total_secciones}/{self.state.total_secciones}")

        try:
            imagen_path = _buscar_imagen_base(self.state.topic)
            if imagen_path and "descargada:" in imagen_path:
                filename = imagen_path.split(":", 1)[-1].strip()
                if os.path.exists(filename):
                    self.state.imagen_portada = filename
                    print(f"Imagen de portada descargada: {filename}")
                else:
                    print(f"No se encontró la imagen descargada: {filename}")
                    self.state.imagen_portada = ""
            else:
                print(f"No fue posible descargar imagen para: {self.state.topic}")
                self.state.imagen_portada = ""
        except Exception as e:
            print(f"Error buscando imagen de portada: {e}")
            self.state.imagen_portada = ""

        return "imagen_buscada"

    @listen(buscar_imagen_portada)
    def compilar_documento_final(self, _):
        """Paso 4: Compilar el Markdown completo en un PDF, incluyendo la portada."""
        print(f"\nPASO 4: COMPILACIÓN FINAL - Generando PDF")

        if not os.path.exists(self.state.archivo_markdown):
            print(f"Error: El archivo Markdown no existe: {self.state.archivo_markdown}")
            return "error_compilacion"

        try:
            with open(self.state.archivo_markdown, "r", encoding="utf-8") as f:
                contenido_markdown = f.read()

            print("Generando PDF a partir del Markdown...")
            pdf_path = _generar_pdf_base(
                contenido_markdown,
                self.state.imagen_portada,
                "temp/final_documento.pdf"
            )

            if pdf_path and os.path.exists(pdf_path):
                self.state.pdf_final = pdf_path
                print(f"PDF generado: {self.state.pdf_final}")
            else:
                print("Error al generar el PDF.")
                return "error_compilacion"

        except Exception as e:
            print(f"Excepción al compilar el PDF: {e}")
            return "error_compilacion"

        return "documento_completado"

    @listen(compilar_documento_final)
    def mover_pdf_y_mostrar_estadisticas_finales(self, _):
        """Paso 5: Mover el PDF a 'output/' y mostrar estadísticas del flujo."""
        print(f"\nPASO 5: ORGANIZACIÓN FINAL - Moviendo PDF a carpeta 'output'")

        os.makedirs("output", exist_ok=True)
        topic_clean = self.state.topic.replace(" ", "_").replace("/", "_").replace("\\", "_")
        destino = f"output/{topic_clean}.pdf"

        if self.state.pdf_final and os.path.exists(self.state.pdf_final):
            try:
                shutil.move(self.state.pdf_final, destino)
                self.state.pdf_final = destino
                print(f"PDF movido a: {destino}")
            except Exception as e:
                print(f"Error moviendo PDF: {e}")

        print("\n" + "=" * 60)
        print("FLUJO COMPLETO FINALIZADO")
        print("=" * 60)
        print(f"Tema del documento: {self.state.topic}")
        print(f"Total de secciones procesadas: {self.state.total_secciones}")

        if os.path.exists(self.state.archivo_markdown):
            with open(self.state.archivo_markdown, "r", encoding="utf-8") as f:
                contenido = f.read()
            palabras = len(contenido.split())
            lineas = len(contenido.split("\n"))
            print("Estadísticas del documento:")
            print(f"   • Palabras: {palabras}")
            print(f"   • Líneas: {lineas}")

        if self.state.pdf_final and os.path.exists(self.state.pdf_final):
            size_bytes = os.path.getsize(self.state.pdf_final)
            size_mb = size_bytes / (1024 * 1024)
            print(f"PDF final: {self.state.pdf_final}")
            print(f"   • Tamaño: {size_bytes} bytes ({size_mb:.2f} MB)")

        print("=" * 60)
        return None  # Final del flujo


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para ejecutar el flujo completo."""
    topic = "Inteligencia Artificial en la Medicina"

    flow = DocumentoFlowCompleto()
    flow.state.topic = topic
    flow.state.modelo = None  # Usar modelo por defecto, o especificar uno si se desea

    print("=== INICIANDO FLUJO DE DOCUMENTACIÓN CORREGIDO ===")
    flow.kickoff()
    print("=== FLUJO COMPLETADO CORRECTAMENTE ===")


if __name__ == "__main__":
    main()