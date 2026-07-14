import streamlit as st
import os
from google import genai
import PyPDF2

# 1. Configuración de página
st.set_page_config(page_title="Asistente RH", page_icon="💼")

st.sidebar.title("🔑 Configuración")
api_key_usuario = st.sidebar.text_input("Introduce tu Gemini API Key (Empieza con AQ.):", type="password")
st.sidebar.markdown("[¿No tienes una clave? Consíguela gratis aquí](https://aistudio.google.com/)")

st.title("💼 Tu Asistente Virtual de Recursos Humanos")
st.write("¡Hola! Cargaré el manual interno para responder tus dudas.")

# 2. Leer el PDF
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

# 3. Historial
if "historial" not in st.session_state:
    st.session_state.historial = []

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 4. Entrada del usuario
pregunta = st.chat_input("Escribe tu duda sobre el manual aquí...")

if pregunta:
    st.chat_message("user").markdown(pregunta)
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    
    if not api_key_usuario:
        error_msg = "⚠️ Por favor, introduce tu Gemini API Key en la barra lateral izquierda."
        st.chat_message("assistant").markdown(error_msg)
        st.session_state.historial.append({"rol": "assistant", "texto": error_msg})
    else:
        try:
            # TRUCO MAESTRO: Forzamos al sistema a registrar la clave en el entorno global de Python
            # Esto soluciona el error 401 del formato AQ. en servidores en la nube
            os.environ["GEMINI_API_KEY"] = api_key_usuario.strip()
            
            # Inicializamos el cliente sin pasarle parámetros para que tome la variable global limpia
            cliente_ia = genai.Client()
            
            contexto = f"""
            Eres un asistente experto de Recursos Humanos. Responde de forma muy amable.
            Usa ÚNICAMENTE esta información del manual de la empresa para responder. Si no viene en el texto, di que no cuentas con la información.
            
            MANUAL:
            {texto_manual}
            
            PREGUNTA:
            {pregunta}
            """
            
            # Usamos el modelo estable actual
            respuesta = cliente_ia.models.generate_content(
                model='gemini-2.5-flash',
                contents=contexto
            )
            
            st.chat_message("assistant").markdown(respuesta.text)
            st.session_state.historial.append({"rol": "assistant", "texto": respuesta.text})
            
        except Exception as error_general:
            msg_fallo = f"❌ Error de comunicación: {str(error_general)}. Asegúrate de copiar la clave completa."
            st.chat_message("assistant").markdown(msg_fallo)
            st.session_state.historial.append({"rol": "assistant", "texto": msg_fallo})
