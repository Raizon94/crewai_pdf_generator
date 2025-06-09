import streamlit as st
import os
import random
from flows.documento_flow import DocumentoFlowCompleto, DocumentoState

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
⚠️ <u>IMPORTANTE</u>: Este software ha sido desarrollado y optimizado específicamente para la <b>API de Gemini</b>. El máximo recomendado para la API gratuita de Gemini es de <b>10 a 13 max_rpm</b>.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# Paso 1: Inicializar flags en session_state
# --------------------------------------------------------
#   - 'generando' indica si ya lanzamos el flujo de generación
#   - 'pdf_ok' para saber si existe PDF listo para descarga
#   - 'error_generacion' para guardar cualquier mensaje de error
if "generando" not in st.session_state:
    st.session_state["generando"] = False
if "pdf_ok" not in st.session_state:
    st.session_state["pdf_ok"] = False
if "error_generacion" not in st.session_state:
    st.session_state["error_generacion"] = ""

# --------------------------------------------------------
# Paso 2: Mostrar formulario para configuración y tópico
# --------------------------------------------------------
with st.form(key="form_pdf"):
    # Campo para la API key de Gemini
    gemini_api_key = st.text_input(
        "Gemini API Key (opcional - usa .env si está vacío)",
        value=st.session_state.get("gemini_api_key", ""),
        key="gemini_api_key",
        type="password",
        help="Introduce tu API key de Gemini. Si está vacío, se usará la del archivo .env"
    )
    
    # Campo para max_rpm
    max_rpm = st.number_input(
        "Max RPM (Requests per Minute)",
        min_value=1,
        max_value=60,
        value=st.session_state.get("max_rpm", 10),
        key="max_rpm",
        help="Máximo de requests por minuto. Para API gratuita de Gemini se recomienda máximo 10."
    )
    
    topic = st.text_input(
        "Tópico del documento",
        value=st.session_state.get("topic_input", "Arquitectura Transformer en los LLM"),
        key="topic_input"
    )
    submit = st.form_submit_button("Generar PDF", use_container_width=True)

# --------------------------------------------------------
# Paso 4: Cuando se envía el formulario, lanzamos la generación
# --------------------------------------------------------
if submit and not st.session_state["generando"]:
    # Bloqueamos nuevos envíos
    st.session_state["generando"] = True
    # Reseteamos indicadores
    st.session_state["pdf_ok"] = False
    st.session_state["error_generacion"] = ""
    # A continuación, la recarga natural del formulario trae los valores
    # con session_state["modelo_llm"] y session_state["topic_input"] actualizados.

# --------------------------------------------------------
# Paso 5: Si estamos en modo “generando”, mostramos spinner + info
# --------------------------------------------------------
if st.session_state["generando"]:
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
        # ----------------------------------------------------------------------------------
        # - Obtenemos los parámetros finales desde session_state (ya actualizados)
        # - Ejecutamos el flujo de generación de PDF
        # ----------------------------------------------------------------------------------
        gemini_api_key_actual = st.session_state["gemini_api_key"]
        max_rpm_actual = st.session_state["max_rpm"]
        topic_actual = st.session_state["topic_input"]
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        try:
            flow = DocumentoFlowCompleto(
                state=DocumentoState(topic=topic_actual, gemini_api_key=gemini_api_key_actual, max_rpm=max_rpm_actual)
            )
            flow.kickoff(inputs={"topic": topic_actual, "gemini_api_key": gemini_api_key_actual, "max_rpm": max_rpm_actual})
            # Si no arroja excepción, asumimos que el PDF se creó
            st.session_state["pdf_ok"] = True
        except Exception as e:
            st.session_state["error_generacion"] = f"Error ejecutando el flujo: {e}"
            st.session_state["pdf_ok"] = False

    # Terminó el “spinner”: desbloqueamos la UI
    st.session_state["generando"] = False

    # Si hubo error, lo mostramos y detenemos
    if st.session_state["error_generacion"]:
        st.error(st.session_state["error_generacion"])
    # Si todo fue bien, indicamos que el PDF está listo
    elif st.session_state["pdf_ok"]:
        topic_clean = topic_actual.replace(" ", "_").replace("/", "_").replace("\\", "_")
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
        else:
            st.error("❌ No se encontró el PDF generado después de la ejecución.")
    else:
        # Si no hay PDF y tampoco error explícito, mensaje genérico
        st.error("❌ Ocurrió un problema desconocido al generar el PDF.")


# --------------------------------------------------------
# Aviso si se ejecuta con python en lugar de streamlit
# --------------------------------------------------------
if __name__ == "__main__":
    import os
    import sys
    is_streamlit = any("streamlit" in arg for arg in sys.argv) or "STREAMLIT_RUN" in os.environ
    if not is_streamlit:
        print("\033[91m[WARNING]\033[0m Este script debe ejecutarse con: \033[1mstreamlit run app.py\033[0m\nNo lo ejecutes con 'python app.py'. ")
        sys.exit(1)