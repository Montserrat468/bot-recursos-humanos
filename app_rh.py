import streamlit as st
import os
from google import genai
import PyPDF2

# 1. Configuración de página de Streamlit
st.set_page_config(page_title="Asistente RH", page_icon="💼")

# 2. Configuración de la barra lateral (Se declara la variable api_key_usuario)
st.sidebar.title("🔑 Configuración")
api_key_usuario = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")
st.sidebar.markdown("[¿No tienes una clave? Consíguela gratis aquí](https://aistudio.google.com/)")

st.title("💼 Tu Asistente Virtual de Recursos Humanos")
st.write("¡Hola! Cargaré el manual interno para responder tus dudas.")

# 3. Leer el PDF de forma segura
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

# 4. Inicializar e imprimir el historial del chat
if "historial" not in st.session_state:
    st.session_state.historial = []

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Declaración de la variable 'pregunta' (Debe ir ANTES de evaluarse)
pregunta = st.chat_input("Escribe tu duda sobre el manual aquí...")

# 6. Evaluación de la variable 'pregunta' (Ahora la variable ya existe en memoria)
if pregunta:
    # Mostramos la pregunta del usuario en la interfaz
    st.chat_message("user").markdown(pregunta)
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    
    if not api_key_usuario:
        error_msg = "⚠️ Por favor, introduce tu Gemini API Key en la barra lateral izquierda."
        st.chat_message("assistant").markdown(error_msg)
        st.session_state.historial.append({"rol": "assistant", "texto": error_msg})
    else:
        try:
            # Configuración de la clave e inicialización del cliente de IA
            os.environ["GEMINI_API_KEY"] = api_key_usuario.strip()
            cliente_ia = genai.Client()
            
            contexto = f"""
            Eres un asistente experto de Recursos Humanos. Responde de forma muy amable.
            Usa ÚNICAMENTE esta información del manual de la empresa para responder. Si no viene en el texto, di que no cuentas con la información.
            
            MANUAL:
            {texto_manual}
            
            PREGUNTA:
            {pregunta}
            """
            
            # Petición al modelo oficial estable
            respuesta = cliente_ia.models.generate_content(
                model='gemini-2.0-flash',
                contents=contexto
            )
            
            # Mostramos la respuesta del asistente en pantalla
            st.chat_message("assistant").markdown(respuesta.text)
            st.session_state.historial.append({"rol": "assistant", "texto": respuesta.text})
            
        except Exception as error_general:
            msg_fallo = f"❌ Error de comunicación: {str(error_general)}."
            st.chat_message("assistant").markdown(msg_fallo)
            st.session_state.historial.append({"rol": "assistant", "texto": msg_fallo})
