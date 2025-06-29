from streamlit_mic_recorder import speech_to_text
from config import llm
import streamlit as st

st.set_page_config(page_title="Asistente de Voz", layout="centered")

st.title("🗣️ Tu asistente de Voz Todo en Uno")
st.write("Aplicación de chat habilitada por voz (GPT-4o + Micrófono)")

# Inicializar historial
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Configuraciones simples en sidebar
with st.sidebar:
    st.header("Configuraciones")
    
    # Selección de idioma
    language = st.selectbox(
        "Idioma:",
        ["es", "en", "fr", "it", "de"],
        format_func=lambda x: {"es": "Español", "en": "Inglés", "fr": "Francés", "it": "Italiano", "de": "Alemán"}[x]
    )
    
    # Selección de tono
    tone = st.selectbox(
        "Tono de respuesta:",
        ["casual", "formal", "divertido"]
    )
    
    # Botón limpiar
    if st.button("Limpiar Chat"):
        st.session_state.conversation_history = []
        st.rerun()

# Función para generar prompt con tono
def get_prompt_with_tone(text, tone):
    if tone == "formal":
        return f"Responde de manera formal y profesional: {text}"
    elif tone == "divertido":
        return f"Responde de manera divertida y creativa: {text}"
    else:  # casual
        return f"Responde de manera casual y amigable: {text}"

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
    
    # Generar respuesta con tono
    prompt = get_prompt_with_tone(text, tone)
    response = llm.invoke(prompt)
    
    # Agregar respuesta al historial
    st.session_state.conversation_history.append({"role": "assistant", "content": response.content})
    
    st.write("🤖 Respuesta del modelo: ", response.content)

# Mostrar historial si existe
if st.session_state.conversation_history:
    st.subheader("Historial")
    
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.write(f"🧑 **Tú:** {message['content']}")
        else:
            st.write(f"🤖 **Asistente:** {message['content']}")
        st.write("---")