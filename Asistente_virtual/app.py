from streamlit_mic_recorder import speech_to_text
from config import llm
import streamlit as st
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
st.markdown("*Aplicación de chat avanzada con reconocimiento de voz*")

# Inicializar estado de la sesión
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

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

# Función para generar prompt según el tono
def get_tone_prompt(tone, user_input):
    """Genera un prompt específico según el tono seleccionado"""
    tone_prompts = {
        "formal": f"Responde de manera formal y profesional a la siguiente consulta: {user_input}",
        "casual": f"Responde de manera casual, amigable y relajada a: {user_input}",
        "divertido": f"Responde de manera creativa, divertida y con humor (pero manteniendo la información útil) a: {user_input}"
    }
    return tone_prompts.get(tone, user_input)

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
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7F8C8D; font-size: 14px;'>"
    "🚀 Asistente de Voz Inteligente - Potenciado por IA"
    "</div>", 
    unsafe_allow_html=True
)