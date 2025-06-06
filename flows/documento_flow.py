#!/usr/bin/env python3
# proyecto_crewai/flows/documento_flow.py

import os
import sys
import shutil
from crewai.flow.flow import Flow, start, listen
from crewai import Crew, Process
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
    modelo: str | None = None
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
        print(f"🚀 INICIANDO FLUJO DE DOCUMENTACIÓN COMPLETO")
        print(f"📋 Tema: {self.state.topic}")

        # 1. Limpiar carpeta temp
        if os.path.exists("temp"):
            try:
                shutil.rmtree("temp")
                print("🗑️ Carpeta 'temp' eliminada completamente.")
            except Exception as e:
                print(f"⚠️ Error eliminando carpeta 'temp': {e}")

        # 2. Crear carpeta temp vacía
        os.makedirs("temp", exist_ok=True)
        print("📁 Carpeta 'temp' creada limpia.")

        # 3. Invocar agente estructurador para obtener la estructura completa
        print("\n📋 PASO 1: ESTRUCTURADOR - Generando esquema del documento")
        agente_estructurador = crear_agente_estructurador(self.state.modelo)
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

        print(f"\n✅ Estructura detectada con {self.state.total_secciones} secciones:")
        for i, s in enumerate(self.state.secciones_lista, start=1):
            print(f"   {i}. {s}")

        # 5. Inicializar archivo Markdown con el título principal
        try:
            os.makedirs(os.path.dirname(self.state.archivo_markdown), exist_ok=True)
            with open(self.state.archivo_markdown, "w", encoding="utf-8") as f:
                f.write(f"# {self.state.topic}\n\n")
            print(f"📄 Archivo Markdown iniciado en: {self.state.archivo_markdown}")
        except Exception as e:
            print(f"⚠️ Error escribiendo el archivo Markdown: {e}")

        # Pasar al procesamiento de todas las secciones
        return "procesar_seccion"

    @listen(limpiar_y_crear_estructura_documento)
    def procesar_seccion(self, _):
        """Paso 2: Iterar por cada sección, creando agentes frescos y ejecutando investigación + redacción."""
        print(f"\n📝 PASO 2: Procesando todas las secciones, una por una")

        for idx, seccion in enumerate(self.state.secciones_lista):
            print(f"   ▶️ Procesando sección {idx + 1}/{self.state.total_secciones}: '{seccion}'")

            # 1) Crear un agente de búsqueda y otro de redacción frescos para esta sección
            agente_buscador = crear_agente_buscador_automatico(modelo=self.state.modelo)
            agente_escritor = crear_agente_escritor(modelo=self.state.modelo)

            # 2) Tarea de investigación
            tarea_inv = crear_tarea_investigacion_automatica(
                seccion,
                self.state.topic,
                agente_buscador
            )
            tarea_inv.name = f"investigar_{idx}"

            # 3) Tarea de redacción, que depende de la investigación previa
            tarea_red = crear_tarea_redaccion_archivo(
                agente_escritor,
                seccion,
                self.state.topic
            )
            tarea_red.name = f"redactar_{idx}"
            tarea_red.context = [tarea_inv]

            # 4) Armar un Crew secuencial para esta sección
            crew_seccion = Crew(
                agents=[agente_buscador, agente_escritor],
                tasks=[tarea_inv, tarea_red],
                process=Process.sequential,
                verbose=True
            )

            # 5) Ejecutar investigación + redacción
            resultado = crew_seccion.kickoff()
            # NOTA: Se asume que el agente escritor, usando sus herramientas internas
            #       (por ejemplo append_to_markdown), añade directamente el contenido
            #       al archivo Markdown. No se hace escritura explícita aquí.

        # Una vez procesadas todas las secciones, avanzamos al siguiente paso
        return "todas_secciones_completadas"

    @listen(procesar_seccion)
    def buscar_imagen_portada(self, _):
        """Paso 3: Buscar imagen de portada para el documento completo."""
        print(f"\n🖼️ PASO 3: BÚSQUEDA DE IMAGEN - Buscando imagen de portada para '{self.state.topic}'")
        print(f"Secciones procesadas: {self.state.total_secciones}/{self.state.total_secciones}")

        try:
            imagen_path = _buscar_imagen_base(self.state.topic)
            if imagen_path and "descargada:" in imagen_path:
                filename = imagen_path.split(":", 1)[-1].strip()
                if os.path.exists(filename):
                    self.state.imagen_portada = filename
                    print(f"✅ Imagen de portada descargada: {filename}")
                else:
                    print(f"⚠️ No se encontró la imagen descargada: {filename}")
                    self.state.imagen_portada = ""
            else:
                print(f"⚠️ No fue posible descargar imagen para: {self.state.topic}")
                self.state.imagen_portada = ""
        except Exception as e:
            print(f"⚠️ Error buscando imagen de portada: {e}")
            self.state.imagen_portada = ""

        return "imagen_buscada"

    @listen(buscar_imagen_portada)
    def compilar_documento_final(self, _):
        """Paso 4: Compilar el Markdown completo en un PDF, incluyendo la portada."""
        print(f"\n📄 PASO 4: COMPILACIÓN FINAL - Generando PDF")

        if not os.path.exists(self.state.archivo_markdown):
            print(f"⚠️ Error: El archivo Markdown no existe: {self.state.archivo_markdown}")
            return "error_compilacion"

        try:
            with open(self.state.archivo_markdown, "r", encoding="utf-8") as f:
                contenido_markdown = f.read()

            print("📑 Generando PDF a partir del Markdown...")
            pdf_path = _generar_pdf_base(
                contenido_markdown,
                self.state.imagen_portada,
                "temp/final_documento.pdf"
            )

            if pdf_path and os.path.exists(pdf_path):
                self.state.pdf_final = pdf_path
                print(f"✅ PDF generado: {self.state.pdf_final}")
            else:
                print("⚠️ Error al generar el PDF.")
                return "error_compilacion"

        except Exception as e:
            print(f"⚠️ Excepción al compilar el PDF: {e}")
            return "error_compilacion"

        return "documento_completado"

    @listen(compilar_documento_final)
    def mover_pdf_y_mostrar_estadisticas_finales(self, _):
        """Paso 5: Mover el PDF a 'output/' y mostrar estadísticas del flujo."""
        print(f"\n🚚 PASO 5: ORGANIZACIÓN FINAL - Moviendo PDF a carpeta 'output'")

        os.makedirs("output", exist_ok=True)
        topic_clean = self.state.topic.replace(" ", "_").replace("/", "_").replace("\\", "_")
        destino = f"output/{topic_clean}.pdf"

        if self.state.pdf_final and os.path.exists(self.state.pdf_final):
            try:
                shutil.move(self.state.pdf_final, destino)
                self.state.pdf_final = destino
                print(f"✅ PDF movido a: {destino}")
            except Exception as e:
                print(f"⚠️ Error moviendo PDF: {e}")

        print("\n" + "=" * 60)
        print("🎉 FLUJO COMPLETO FINALIZADO")
        print("=" * 60)
        print(f"Tema del documento: {self.state.topic}")
        print(f"Total de secciones procesadas: {self.state.total_secciones}")

        if os.path.exists(self.state.archivo_markdown):
            with open(self.state.archivo_markdown, "r", encoding="utf-8") as f:
                contenido = f.read()
            palabras = len(contenido.split())
            lineas = len(contenido.split("\n"))
            print("📊 Estadísticas del documento:")
            print(f"   • Palabras: {palabras}")
            print(f"   • Líneas: {lineas}")

        if self.state.pdf_final and os.path.exists(self.state.pdf_final):
            size_bytes = os.path.getsize(self.state.pdf_final)
            size_mb = size_bytes / (1024 * 1024)
            print(f"📄 PDF final: {self.state.pdf_final}")
            print(f"   • Tamaño: {size_bytes} bytes ({size_mb:.2f} MB)")

        print("=" * 60)
        return None  # Final del flujo


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Función principal para ejecutar el flujo completo."""
    topic = "Inteligencia Artificial en la Medicina"

    flow = DocumentoFlowCompleto()
    flow.state.topic = topic

    print("=== INICIANDO FLUJO DE DOCUMENTACIÓN CORREGIDO ===")
    flow.kickoff()
    print("=== FLUJO COMPLETADO CORRECTAMENTE ===")


if __name__ == "__main__":
    main()