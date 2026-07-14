import streamlit as st
from google import genai
import PyPDF2

# 1. Configuración de la página
st.set_page_config(page_title="Asistente RH", page_icon="💼", layout="centered")

# Barra lateral para la API Key (Solución definitiva a bloqueos de servidor)
st.sidebar.title("🔑 Configuración")
api_key_usuario = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")
st.sidebar.markdown("[¿No tienes una clave? Consíguela gratis aquí](https://aistudio.google.com/)")

st.title("💼 Tu Asistente Virtual de Recursos Humanos")
st.write("¡Hola! Cargaré el manual interno para responder tus dudas.")

# 2. Leer el manual PDF de forma segura
@st.cache_data
def leer_pdf(ruta_archivo):
    try:
        texto = ""
        with open(ruta_archivo, 'rb') as archivo:
            lector = PyPDF2.PdfReader(archivo)
            for pagina in lector.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto += texto_pagina
        return texto
    except Exception as e:
        return f"Error al leer el PDF: {e}"

texto_manual = leer_pdf("manual.pdf")

# 3. Inicializar el historial de chat en la memoria del navegador
if "historial" not in st.session_state:
    st.session_state.historial = []

# Mostrar el historial en pantalla
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 4. Caja de entrada para la duda del usuario
pregunta = st.chat_input("Escribe tu duda sobre el manual aquí...")

if pregunta:
    # Mostramos la pregunta de inmediato en la interfaz
    st.chat_message("user").markdown(pregunta)
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    
    # VALIDACIÓN: Si el usuario no ha puesto una clave, detenemos el proceso amablemente
    if not api_key_usuario:
        error_msg = "⚠️ Por favor, introduce tu Gemini API Key en la barra lateral izquierda para poder responderte."
        st.chat_message("assistant").markdown(error_msg)
        st.session_state.historial.append({"rol": "assistant", "texto": error_msg})
    else:
        try:
            # Inicializamos el cliente usando la clave provista de forma segura
            cliente_ia = genai.Client(api_key=api_key_usuario)
            
            # Formateamos el contexto para la Inteligencia Artificial
            contexto = f"""
            Eres un asistente experto de Recursos Humanos. Responde la duda del colaborador de forma muy amable.
            Usa ÚNICAMENTE la siguiente información extraída del manual de la empresa. Si la respuesta no viene en el texto, di textualmente que no cuentas con esa información.
            
            ---
            MANUAL:
            {texto_manual}
            ---
            
            PREGUNTA:
            {pregunta}
            """
            
            # Llamamos al modelo oficial estable
            respuesta = cliente_ia.models.generate_content(
                model='gemini-2.5-flash',
                contents=contexto
            )
            
            # Mostramos la respuesta de la IA
            st.chat_message("assistant").markdown(respuesta.text)
            st.session_state.historial.append({"rol": "assistant", "texto": respuesta.text})
            
        except Exception as error_general:
            msg_fallo = f"❌ Ocurrió un problema con la API de Google: {str(error_general)}. Verifica que tu clave sea correcta."
            st.chat_message("assistant").markdown(msg_fallo)
            st.session_state.historial.append({"rol": "assistant", "texto": msg_fallo})
