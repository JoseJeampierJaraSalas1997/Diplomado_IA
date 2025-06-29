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
        padding: 16px 20px;
        border-radius: 18px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20px;
        border-top-right-radius: 4px;
    }
    .user-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255,255,255,0.1);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .user-message:hover::before {
        opacity: 1;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20px;
        border-top-left-radius: 4px;
    }
    .assistant-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255,255,255,0.1);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .assistant-message:hover::before {
        opacity: 1;
    }
    .tone-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        color: white;
        margin-left: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .formal { 
        background: rgba(93, 109, 126, 0.9);
        box-shadow: 0 2px 8px rgba(93, 109, 126, 0.3);
    }
    .casual { 
        background: rgba(243, 156, 18, 0.9);
        box-shadow: 0 2px 8px rgba(243, 156, 18, 0.3);
    }
    .divertido { 
        background: rgba(231, 76, 60, 0.9);
        box-shadow: 0 2px 8px rgba(231, 76, 60, 0.3);
    }
    .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .message-content {
        font-size: 15px;
        line-height: 1.5;
        position: relative;
        z-index: 1;
    }
    .timestamp {
        font-size: 12px;
        opacity: 0.8;
        margin-left: 8px;
    }
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
                <div class="message-header">
                    <strong>🧑 Tú</strong>
                    <span class="timestamp">({message.get("timestamp", "")})</span>
                    {tone_badge}
                </div>
                <div class="message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-header">
                    <strong>🤖 Asistente</strong>
                    <span class="timestamp">({message.get("timestamp", "")})</span>
                </div>
                <div class="message-content">{message["content"]}</div>
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