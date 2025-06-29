from streamlit_mic_recorder import speech_to_text
from config import llm
import streamlit as st
import pyttsx3 
import threading
import time

# Configuración de página
st.set_page_config(
    page_title="Asistente de Voz Avanzado", 
    layout="centered",
    page_icon="🗣️"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86C1;
        margin-bottom: 30px;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #E8F6F3;
        border-left: 4px solid #58D68D;
    }
    .assistant-message {
        background-color: #EBF5FB;
        border-left: 4px solid #3498DB;
    }
    .tone-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        margin-left: 10px;
    }
    .formal { background-color: #5D6D7E; }
    .casual { background-color: #F39C12; }
    .divertido { background-color: #E74C3C; }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🗣️ Tu Asistente de Voz Inteligente</h1>', unsafe_allow_html=True)
st.markdown("*Aplicación de chat avanzada con reconocimiento de voz y síntesis de habla*")

# Inicializar estado de la sesión
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False

# Configuraciones en la barra lateral
st.sidebar.header("⚙️ Configuraciones")

# Selección de idioma
language = st.sidebar.selectbox(
    "🌍 Idioma de reconocimiento:",
    ["es", "en", "fr", "it", "de"],
    format_func=lambda x: {
        "es": "🇪🇸 Español", 
        "en": "🇺🇸 Inglés", 
        "fr": "🇫🇷 Francés", 
        "it": "🇮🇹 Italiano", 
        "de": "🇩🇪 Alemán"
    }[x]
)

# Selección de tono
tone = st.sidebar.selectbox(
    "🎭 Tono de respuesta:",
    ["formal", "casual", "divertido"],
    format_func=lambda x: {
        "formal": "🎩 Formal y profesional",
        "casual": "😊 Casual y amigable", 
        "divertido": "🎉 Divertido y creativo"
    }[x]
)

# Configuración de voz (Text-to-Speech)
st.sidebar.subheader("🔊 Configuración de Voz")
voice_enabled = st.sidebar.checkbox("Activar respuesta por voz", value=st.session_state.voice_enabled)
st.session_state.voice_enabled = voice_enabled

if voice_enabled:
    # Configuraciones de voz
    voice_rate = st.sidebar.slider("Velocidad de habla", 100, 300, 200)
    voice_volume = st.sidebar.slider("Volumen", 0.0, 1.0, 0.9)
    
    # Selección de voz (esto dependerá del sistema)
    voice_gender = st.sidebar.selectbox(
        "Tipo de voz:",
        ["femenina", "masculina"],
        format_func=lambda x: f"👩 Voz {x}" if x == "femenina" else f"👨 Voz {x}"
    )

# Función para configurar el motor de voz
def setup_tts_engine():
    """Configura el motor de text-to-speech"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Configurar propiedades básicas
        engine.setProperty('rate', voice_rate if voice_enabled else 200)
        engine.setProperty('volume', voice_volume if voice_enabled else 0.9)
        
        # Intentar seleccionar voz por género (funcionalidad limitada según el sistema)
        if voices and voice_enabled:
            # Buscar voz femenina o masculina (esto es aproximado)
            for voice in voices:
                if voice_gender == "femenina" and ("female" in voice.name.lower() or "zira" in voice.name.lower()):
                    engine.setProperty('voice', voice.id)
                    break
                elif voice_gender == "masculina" and ("male" in voice.name.lower() or "david" in voice.name.lower()):
                    engine.setProperty('voice', voice.id)
                    break
        
        return engine
    except:
        return None

# Función para generar prompt según el tono
def get_tone_prompt(tone, user_input):
    """Genera un prompt específico según el tono seleccionado"""
    tone_prompts = {
        "formal": f"Responde de manera formal y profesional a la siguiente consulta: {user_input}",
        "casual": f"Responde de manera casual, amigable y relajada a: {user_input}",
        "divertido": f"Responde de manera creativa, divertida y con humor (pero manteniendo la información útil) a: {user_input}"
    }
    return tone_prompts.get(tone, user_input)

# Función para reproducir texto como voz
def speak_text(text, engine):
    """Reproduce el texto usando el motor TTS"""
    try:
        if engine:
            engine.say(text)
            engine.runAndWait()
    except Exception as e:
        st.error(f"Error en la síntesis de voz: {e}")

# Sección principal - Captura de voz
st.subheader("🎤 Habla con tu asistente")

col1, col2 = st.columns([3, 1])

with col1:
    # Capturar voz y convertirla a texto
    text = speech_to_text(
        language=language,
        use_container_width=True,
        just_once=True,
        key="STT"
    )

with col2:
    # Botón para limpiar historial
    if st.button("🗑️ Limpiar Chat", type="secondary"):
        st.session_state.conversation_history = []
        st.rerun()

# Procesar el texto capturado
if text:
    # Agregar mensaje del usuario al historial
    st.session_state.conversation_history.append({
        "role": "user", 
        "content": text, 
        "tone": tone,
        "timestamp": time.strftime("%H:%M:%S")
    })
    
    # Generar respuesta con el tono apropiado
    tone_prompt = get_tone_prompt(tone, text)
    
    try:
        with st.spinner("🤔 Pensando..."):
            response = llm.invoke(tone_prompt)
            
        # Agregar respuesta al historial
        st.session_state.conversation_history.append({
            "role": "assistant", 
            "content": response.content, 
            "tone": tone,
            "timestamp": time.strftime("%H:%M:%S")
        })
        
        # Reproducir respuesta por voz si está habilitado
        if voice_enabled:
            with st.spinner("🔊 Reproduciendo respuesta..."):
                tts_engine = setup_tts_engine()
                if tts_engine:
                    # Ejecutar TTS en un hilo separado para no bloquear la UI
                    thread = threading.Thread(target=speak_text, args=(response.content, tts_engine))
                    thread.daemon = True
                    thread.start()
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error al procesar la solicitud: {e}")

# Mostrar historial de conversación
if st.session_state.conversation_history:
    st.subheader("💬 Historial de Conversación")
    
    for i, message in enumerate(st.session_state.conversation_history):
        if message["role"] == "user":
            tone_class = message.get("tone", "casual")
            tone_badge = f'<span class="tone-badge {tone_class}">{tone_class.upper()}</span>'
            
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 Tú</strong> <small>({message.get("timestamp", "")})</small>{tone_badge}
                <br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Asistente</strong> <small>({message.get("timestamp", "")})</small>
                <br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Información")
st.sidebar.info(
    "**Características:**\n"
    "• 🎤 Reconocimiento de voz multiidioma\n"
    "• 🗣️ Síntesis de voz configurable\n"
    "• 🎭 Múltiples tonos de respuesta\n"
    "• 💾 Historial de conversación\n"
    "• ⚙️ Configuraciones personalizables"
)

# Tips de uso
with st.sidebar.expander("💡 Tips de Uso"):
    st.markdown("""
    **Para mejores resultados:**
    - Habla claramente y a velocidad normal
    - Usa el micrófono en un ambiente silencioso
    - Experimenta con diferentes tonos según el contexto
    - Ajusta la velocidad de voz según tu preferencia
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7F8C8D; font-size: 14px;'>"
    "🚀 Asistente de Voz Inteligente - Potenciado por IA"
    "</div>", 
    unsafe_allow_html=True
)