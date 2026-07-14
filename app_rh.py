import streamlit as st
from google import genai
from google.genai import types
import PyPDF2
import os

# 1. Configuración visual de la página
st.set_page_config(page_title="Asistente RH", page_icon="💼")
st.title("💼 Tu Asistente Virtual de Recursos Humanos")
st.write("¡Hola! Hazme cualquier pregunta sobre el manual de colaboradores.")

# 2. Configurar la API Key de forma interna para el servidor
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# Inicializa el cliente moderno de Google con llave directapara la nube
if "cliente_ia" not in st.session_state:
    st.session_state.cliente_ia = genai.Client(api_key="AQ.Ab8RN6JxFdySkzHoGvU34rhMI_i7TTHpOEctZR0glz5AioRAuQ")

# 3. Función para leer el archivo PDF
@st.cache_data
def leer_pdf(ruta):
    texto = ""
    with open(ruta, 'rb') as archivo:
        lector = PyPDF2.PdfReader(archivo)
        for pagina in lector.pages:
            texto += pagina.extract_text()
    return texto

# Leemos el manual
texto_manual = leer_pdf("manual.pdf")

# 4. Configurar el historial visual en la página web
if "historial_pantalla" not in st.session_state:
    st.session_state.historial_pantalla = []

# Dibujamos los mensajes anteriores si existen
for mensaje in st.session_state.historial_pantalla:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# 5. Caja de texto para que el usuario escriba
pregunta = st.chat_input("Escribe tu duda sobre el manual aquí...")

if pregunta:
    st.chat_message("user").markdown(pregunta)
    st.session_state.historial_pantalla.append({"rol": "user", "texto": pregunta})
    
    configuracion = types.GenerateContentConfig(
        system_instruction=f"Eres un asistente experto de Recursos Humanos. Responde de manera amable usando ÚNICAMENTE esta información del manual de la empresa: {texto_manual}. Si no está en el manual, di que no tienes la información."
    )
    
    # Usamos la variable correcta y el modelo oficial de producción
    respuesta = st.session_state.cliente_ia.models.generate_content(
        model='gemini-2.5-flash',
        contents=pregunta,
        config=configuracion
    )
    
    st.chat_message("assistant").markdown(respuesta.text)
    st.session_state.historial_pantalla.append({"rol": "assistant", "texto": respuesta.text})
