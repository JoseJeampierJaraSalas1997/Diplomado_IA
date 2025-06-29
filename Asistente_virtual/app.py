from streamlit_mic_recorder import speech_to_text
from config import llm
import streamlit as st
import pyttsx3
import threading

st.set_page_config(page_title="Asistente de Voz Mejorado", layout="centered")

st.title("🗣️ Tu Asistente de Voz Todo en Uno")
st.write("Aplicación de chat habilitada por voz (GPT-4o + Micrófono + Síntesis de voz)")

# Inicializar estado de la sesión
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Configuraciones en sidebar
st.sidebar.header("Configuraciones")

# Selección de idioma
language = st.sidebar.selectbox(
    "Idioma de reconocimiento:",
    ["es", "en", "fr", "it", "de"],
    format_func=lambda x: {
        "es": "Español", 
        "en": "Inglés", 
        "fr": "Francés", 
        "it": "Italiano", 
        "de": "Alemán"
    }[x]
)

# Selección de tono
tone = st.sidebar.selectbox(
    "Tono de respuesta:",
    ["casual", "formal", "divertido"],
    format_func=lambda x: {
        "formal": "Formal y profesional",
        "casual": "Casual y amigable", 
        "divertido": "Divertido y creativo"
    }[x]
)

# Configuración de voz
st.sidebar.subheader("Configuración de Voz")
speak_response = st.sidebar.checkbox("Activar respuesta por voz", value=True)

if speak_response:
    voice_speed = st.sidebar.slider("Velocidad de voz", 100, 300, 180)
    voice_volume = st.sidebar.slider("Volumen", 0.1, 1.0, 0.8)
    
    voice_type = st.sidebar.selectbox(
        "Tipo de voz:",
        ["femenina", "masculina"]
    )
    
    # Botón para probar voz
    if st.sidebar.button("Probar Voz"):
        def test_voice():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', voice_speed)
                engine.setProperty('volume', voice_volume)
                
                voices = engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if voice_type == "femenina" and any(word in voice.name.lower() for word in ["female", "zira", "helena"]):
                            engine.setProperty('voice', voice.id)
                            break
                        elif voice_type == "masculina" and any(word in voice.name.lower() for word in ["male", "david"]):
                            engine.setProperty('voice', voice.id)
                            break
                
                engine.say("Esta es una prueba de voz")
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                st.error(f"Error en TTS: {e}")
        
        test_voice()

# Función para generar prompt según el tono
def get_prompt_with_tone(user_input, tone):
    if tone == "formal":
        return f"Responde de manera formal y profesional: {user_input}"
    elif tone == "divertido":
        return f"Responde de manera divertida y creativa (manteniendo la información útil): {user_input}"
    else:  # casual
        return f"Responde de manera casual y amigable: {user_input}"

# Función para síntesis de voz
def speak_text(text, speed, volume, voice_type):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', speed)
        engine.setProperty('volume', volume)
        
        voices = engine.getProperty('voices')
        if voices:
            for voice in voices:
                voice_name = voice.name.lower()
                if voice_type == "femenina" and any(word in voice_name for word in ["female", "zira", "helena", "sabina"]):
                    engine.setProperty('voice', voice.id)
                    break
                elif voice_type == "masculina" and any(word in voice_name for word in ["male", "david", "diego"]):
                    engine.setProperty('voice', voice.id)
                    break
        
        # Limpiar texto para mejor síntesis
        clean_text = text.replace('*', '').replace('_', '').replace('#', '')
        
        engine.say(clean_text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error(f"Error TTS: {e}")

# Botón para limpiar historial
if st.button("Limpiar Historial"):
    st.session_state.conversation_history = []
    st.rerun()

# Capturar voz y convertirla a texto
text = speech_to_text(
    language=language,
    use_container_width=True,
    just_once=True,
    key="STT"
)

# Procesar el texto si existe
if text:
    # Agregar al historial
    st.session_state.conversation_history.append({"role": "user", "content": text})
    
    st.write("🧑 Tú: ", text)
    
    # Generar respuesta con el tono seleccionado
    prompt = get_prompt_with_tone(text, tone)
    response = llm.invoke(prompt)
    
    # Agregar respuesta al historial
    st.session_state.conversation_history.append({"role": "assistant", "content": response.content})
    
    st.write("🤖 Respuesta del modelo: ", response.content)
    
    # Reproducir respuesta por voz si está activado
    if speak_response:
        with st.spinner("Reproduciendo respuesta..."):
            # Ejecutar en hilo separado para no bloquear la interfaz
            thread = threading.Thread(
                target=speak_text, 
                args=(response.content, voice_speed, voice_volume, voice_type)
            )
            thread.daemon = True
            thread.start()

# Mostrar historial
if st.session_state.conversation_history:
    st.subheader("Historial de Conversación")
    
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.write(f"🧑 **Tú:** {message['content']}")
        else:
            st.write(f"🤖 **Asistente:** {message['content']}")
        st.write("---")

# Información en sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    "**Características:**\n"
    "• Reconocimiento de voz multiidioma\n"
    "• Síntesis de voz configurable\n"
    "• Múltiples tonos de respuesta\n"
    "• Historial de conversación"
)