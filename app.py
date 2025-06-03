import streamlit as st
import os
import random
from flows.documento_flow import DocumentoFlowCompleto, DocumentoState
from utils.llm_selector import obtener_modelos_disponibles_ollama
from utils.llm_provider import crear_llm_crewai
import sys

st.set_page_config(page_title="Generador de PDF CrewAI", layout="centered")
st.title("📄 Generador de PDF CrewAI")

# CSS para aclarar el botón de descarga y el mensaje de éxito
st.markdown("""
<style>
    div[data-testid="stDownloadButton"] > button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 1.5px solid #388e3c !important;
        opacity: 1 !important;
        filter: none !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18) !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #388e3c !important;
        border-color: #2e7031 !important;
        filter: brightness(110%) !important;
    }
    div[data-testid="stDownloadButton"] > button:disabled {
        background-color: #cccccc !important;
        border-color: #cccccc !important;
        color: #ffffff !important;
        filter: none !important;
        opacity: 0.6 !important;
    }
    /* Mensaje de éxito personalizado */
    .stAlert-success {
        background-color: #e6ffe6 !important;
        border: 2px solid #4CAF50 !important;
        color: #256029 !important;
        font-weight: bold !important;
        font-size: 1.08em !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(76, 175, 80, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; font-size:1em; margin-bottom:1em;'>
Trabajo realizado por <b>William Atef Tadrous</b> y <b>Julián Cussianovich</b> para la asignatura <b>AIN</b>. Grupo: <b>3CO11</b>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background-color:#ffe6e6; padding:0.7em; border-radius:8px; text-align:center; font-size:1em; font-weight:bold; color:#b80000; border:2px solid #b80000;'>
⚠️ <u>IMPORTANTE</u>: Este software ha sido desarrollado y optimizado para el modelo <b>gemma3:1b o/y gemma3:4b</b>. Se recomienda usar esos LLM para obtener los mejores resultados.
</div>
""", unsafe_allow_html=True)

# Obtener modelos instalados realmente
modelos = obtener_modelos_disponibles_ollama()
if not modelos:
    st.error("No se encontraron modelos Ollama instalados. ¿Está corriendo el demonio y tienes modelos descargados?")
    st.stop()

if 'generando' not in st.session_state:
    st.session_state['generando'] = False

campos_disabled = st.session_state['generando']

# Formulario SIEMPRE visible, lógica de generación fuera
modelo = st.selectbox("Selecciona el modelo LLM", modelos, key="modelo_llm", disabled=campos_disabled)
topic = st.text_input("Tópico del documento", value="Arquitectura Transformer en los LLM", key="topic_input", disabled=campos_disabled)
submit = st.button("Generar PDF", use_container_width=True, disabled=campos_disabled)

if submit and not st.session_state['generando']:
    st.session_state['generando'] = True
    st.rerun()

if st.session_state['generando']:
    st.markdown("""
        <div style='background-color:#ffe066; padding:1em; border-radius:8px; text-align:center; font-size:1.15em; font-weight:bold; color:#b8860b;'>
        🚦 No toques nada, la IA está concentrada 🚦
        </div>
    """, unsafe_allow_html=True)
    frases = [
        "Puede tardar hasta 10 minutos...",
        "Ten paciencia, se está cocinando la magia...",
        "¡No cierres la ventana! El conocimiento está en el horno...",
        "Generando tu PDF, esto puede demorar un poco...",
        "La inteligencia artificial está trabajando para ti...",
        "¡Momento de un café! Pronto tendrás tu documento...",
        "Preparando resultados increíbles, espera un momento..."
    ]
    mensaje = random.choice(frases)
    with st.spinner(mensaje):
        st.info(f"Modelo seleccionado: {st.session_state['modelo_llm']}")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        topic_actual = st.session_state["topic_input"]
        flow_executed = False
        execution_error = None
        
        try:
            llm = crear_llm_crewai(st.session_state['modelo_llm'])
        except Exception as e:
            execution_error = f"Error inicializando LLM: {e}"
        
        if not execution_error:
            try:
                flow = DocumentoFlowCompleto(state=DocumentoState(topic=topic_actual))
                flow.kickoff(inputs={"topic": topic_actual})
                flow_executed = True
            except Exception as e:
                execution_error = f"Error ejecutando el flujo: {e}"
    
    # IMPORTANTE: Resetear el estado FUERA del spinner para permitir que la UI se actualice
    st.session_state['generando'] = False
    
    # Manejar errores después del spinner
    if execution_error:
        st.error(execution_error)
        st.rerun()
    
    topic_clean = topic_actual.replace(' ', '_').replace('/', '_').replace('\\', '_')
    pdf_path = os.path.join(output_dir, f"{topic_clean}.pdf")
    
    if os.path.exists(pdf_path):
        st.success(f"✅ PDF generado exitosamente: {pdf_path}")
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Descargar PDF", 
                f, 
                file_name=f"{topic_clean}.pdf", 
                use_container_width=True,
                type="primary"
            )
        
        # Mostrar el diagrama del flujo CrewAI como enlace de descarga HTML
        try:
            st.markdown("### 🔄 Diagrama del Flujo CrewAI Ejecutado")
            
            # Buscar archivo HTML del diagrama
            html_flow_path = "crewai_flow.html"
            if os.path.exists(html_flow_path):
                # Leer el contenido del archivo HTML
                with open(html_flow_path, "rb") as html_file:
                    html_content = html_file.read()
                
                st.markdown("📊 El diagrama interactivo del flujo CrewAI ha sido generado:")
                st.download_button(
                    "📱 Descargar Diagrama HTML Interactivo",
                    html_content,
                    file_name=f"diagrama_crewai_{topic_clean}.html",
                    mime="text/html",
                    use_container_width=True,
                    help="Descarga y abre este archivo HTML en tu navegador para ver el diagrama interactivo del flujo CrewAI"
                )
                st.info("💡 **Tip:** Abre el archivo HTML descargado en tu navegador para ver el diagrama interactivo completo del flujo de CrewAI.")
            else:
                # Intentar generar el diagrama si no existe
                if flow_executed and 'flow' in locals():
                    try:
                        flow_diagram_path = flow.plot(filename="crewai_flow")
                        if flow_diagram_path and os.path.exists("crewai_flow.html"):
                            with open("crewai_flow.html", "rb") as html_file:
                                html_content = html_file.read()
                            st.download_button(
                                "📱 Descargar Diagrama HTML Interactivo",
                                html_content,
                                file_name=f"diagrama_crewai_{topic_clean}.html",
                                mime="text/html",
                                use_container_width=True
                            )
                        else:
                            st.info("ℹ️ No se pudo generar el diagrama del flujo. Puede requerir instalar graphviz: `pip install graphviz`")
                    except Exception as e:
                        st.warning(f"⚠️ No se pudo generar el diagrama del flujo: {e}")
                else:
                    st.info("ℹ️ El diagrama del flujo se generará automáticamente en la próxima ejecución.")
        except Exception as e:
            st.warning(f"⚠️ Error al procesar el diagrama del flujo: {e}")
    else:
        st.error("❌ No se encontró el PDF generado.")

# Mostrar información del modelo (checkbox bloqueado si se está generando)
st.checkbox("Mostrar información del modelo LLM", disabled=campos_disabled, key="mostrar_info_modelo")

if st.session_state.get("mostrar_info_modelo", False):
    st.write(f"Modelo actual: {st.session_state.get('modelo_llm', 'Ninguno')}")
    st.write("Puedes cambiar los modelos disponibles descargando más modelos con Ollama.")

if __name__ == "__main__":
    # Detectar si se está ejecutando bajo Streamlit
    import os
    import sys
    is_streamlit = any(
        "streamlit" in arg for arg in sys.argv
    ) or "STREAMLIT_RUN" in os.environ
    if not is_streamlit:
        print("\033[91m[WARNING]\033[0m Este script debe ejecutarse con: \033[1mstreamlit run app.py\033[0m\nNo lo ejecutes con 'python app.py'. ")
        sys.exit(1)
