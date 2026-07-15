import streamlit as st
import os
from google import genai
import PyPDF2

# [Se mantiene igual la sección de configuración de página y lectura del PDF...]

# Modificación en la entrada de clave de la barra lateral para permitir múltiples claves
st.sidebar.title("🔑 Configuración")
api_input = st.sidebar.text_input(
    "Introduce tus Gemini API Keys (separadas por comas si tienes más de una):", 
    type="password"
)
st.sidebar.markdown("[Consigue tus claves gratis aquí](https://aistudio.google.com/)")

# ... [Se mantiene igual la lógica de lectura de PDF e historial de chat] ...

if pregunta:
    st.chat_message("user").markdown(pregunta)
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    
    if not api_input:
        error_msg = "⚠️ Por favor, introduce al menos una Gemini API Key en la barra lateral."
        st.chat_message("assistant").markdown(error_msg)
        st.session_state.historial.append({"rol": "assistant", "texto": error_msg})
    else:
        # Procesamos la entrada: separamos las claves por comas y limpiamos espacios
        lista_claves = [clave.strip() for clave in api_input.split(",") if clave.strip()]
        
        respuesta_exitosa = False
        ultimo_error = ""
        
        # Iteramos sobre cada clave disponible hasta que una funcione
        for i, clave_actual in enumerate(lista_claves):
            try:
                # Registramos la clave actual en el entorno del sistema
                os.environ["GEMINI_API_KEY"] = clave_actual
                
                # Inicializamos el cliente oficial de Google GenAI
                cliente_ia = genai.Client()
                
                contexto = f"""
                Eres un asistente experto de Recursos Humanos. Responde de forma muy amable.
                Usa ÚNICAMENTE esta información del manual de la empresa para responder. Si no viene en el texto, di que no cuentas con la información.
                
                MANUAL:
                {texto_manual}
                
                PREGUNTA:
                {pregunta}
                """
                
                # Intentamos la generación de contenido con el modelo estándar
                respuesta = cliente_ia.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=contexto
                )
                
                # Si llegamos aquí, la petición fue exitosa
                st.chat_message("assistant").markdown(respuesta.text)
                st.session_state.historial.append({"rol": "assistant", "texto": respuesta.text})
                respuesta_exitosa = True
                break  # Salimos del bucle de claves al tener éxito
                
            except Exception as e:
                # Guardamos el error y continuamos con la siguiente clave de la lista
                ultimo_error = str(e)
                continue
        
        # Si recorrimos todas las claves y ninguna funcionó
        if not respuesta_exitosa:
            if "429" in ultimo_error or "RESOURCE_EXHAUSTED" in ultimo_error:
                msg_fallo = "❌ Todas las claves introducidas han agotado su límite de cuota diario. Por favor, introduce una clave nueva o espera a que se reinicie el servicio."
            else:
                msg_fallo = f"❌ Error de comunicación: {ultimo_error}."
                
            st.chat_message("assistant").markdown(msg_fallo)
            st.session_state.historial.append({"rol": "assistant", "texto": msg_fallo})
