import streamlit as st
import os
from google import genai
import PyPDF2

# 1. Configuracion de pagina
st.set_page_config(page_title="Asistente RH", page_icon="💼")

# 2. Barra lateral
st.sidebar.title("Configuracion")
api_key_usuario = st.sidebar.text_input("Introduce tu Gemini API Key:", type="password")

st.title("Tu Asistente Virtual de Recursos Humanos")
st.write("Hola! Cargare el manual interno para responder tus dudas.")

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
        return f"Error al leer el PDF: {str(e)}"

texto_manual = leer_pdf("manual.pdf")

# 4. Historial del chat
if "historial" not in st.session_state:
    st.session_state.historial = []

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Entrada del usuario
pregunta = st.chat_input("Escribe tu duda sobre el manual aqui...")

if pregunta:
    st.chat_message("user").markdown(pregunta)
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    
    if not api_key_usuario:
        error_msg = "Por favor, introduce tu Gemini API Key en la barra lateral izquierda."
        st.chat_message("assistant").markdown(error_msg)
        st.session_state.historial.append({"rol": "assistant", "texto": error_msg})
    else:
        try:
            os.environ["GEMINI_API_KEY"] = api_key_usuario.strip()
            cliente_ia = genai.Client()
            
            contexto = f"""
            Eres un asistente experto de Recursos Humanos. Responde de forma muy amable.
            Usa UNICAMENTE esta informacion del manual de la empresa para responder. Si no viene en el texto, di que no cuentas con la informacion.
            
            MANUAL:
            {texto_manual}
            
            PREGUNTA:
            {pregunta}
            """
            # El modelo oficial y vigente para la API actaul
            respuesta = cliente_ia.models.generate_content(
                model='gemini-2.0-flash',
                contents=contexto
            )
            
            st.chat_message("assistant").markdown(respuesta.text)
            st.session_state.historial.append({"rol": "assistant", "texto": respuesta.text})
            
        except Exception as error_general:
            # Eliminamos la cruz roja de aqui para evitar el error ASCII
            msg_fallo = f"Error de comunicacion: {str(error_general)}."
            st.chat_message("assistant").markdown(msg_fallo)
            st.session_state.historial.append({"rol": "assistant", "texto": msg_fallo})
