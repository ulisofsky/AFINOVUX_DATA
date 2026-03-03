import streamlit as st
from openai import OpenAI

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="El Santuario Solar",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS PARA APARIENCIA DE TEMPLO FANTASÍA
css_personalizado = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Philosopher:ital,wght@0,400;0,700;1,400&display=swap');

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    
    /* Fondo del Santuario */
    .stApp {
        background: linear-gradient(180deg, #1a0b00 0%, #2e1500 40%, #1a0b00 100%);
        color: #e0c097;
    }

    /* Título Principal (Nombre del Dios) */
    h1 {
        font-family: 'Cinzel', serif;
        color: #FFD700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        text-align: center;
        border-bottom: 2px solid #B8860B;
        padding-bottom: 15px;
        margin-bottom: 10px !important;
    }

    /* Subtítulo */
    .stCaption {
        text-align: center;
        font-family: 'Philosopher', sans-serif;
        font-style: italic;
        color: #daa520;
        font-size: 1.1rem;
        display: block;
        margin-bottom: 30px;
    }

    /* Área de Chat General */
    .stChatMessage {
        background-color: rgba(30, 20, 10, 0.6);
        border: 1px solid #5c4a2a;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Iconos del Chat (Avatar) */
    .stChatMessage p {
        font-family: 'Philosopher', sans-serif;
        color: #f0e6d2;
    }

    /* Input de texto (El Altar de ofrendas) */
    .stChatInput textarea {
        background-color: #0e0700 !important;
        border: 1px solid #B8860B !important;
        color: #FFD700 !important;
        font-family: 'Philosopher', sans-serif;
    }
    
    .stChatInput textarea::placeholder {
        color: #8a7340 !important; 
    }

    .stChatInput {
        border: 2px solid #B8860B;
        border-radius: 8px;
        background: linear-gradient(45deg, #1a0b00, #2e1500);
    }

    /* Botón Enviar (Estilizado vía borde del input) */
    button[kind="primary"] {
        background-color: #B8860B;
        color: #1a0b00;
    }

    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a0b00;
    }
    ::-webkit-scrollbar-thumb {
        background: #B8860B;
        border-radius: 4px;
    }

    /* Eliminar padding excesivo */
    .stApp {max-width: 100%; padding: 2rem;}
    .stChatMessage {padding: 1rem;}

    /* Separador decorativo */
    .separator {
        text-align: center;
        color: #5c4a2a;
        margin: 20px 0;
    }
</style>
"""
st.markdown(css_personalizado, unsafe_allow_html=True)

# PERSONALIDAD DE LA DEIDAD SOLAR
SYSTEM_PROMPT = """
Eres Sol'Aureon, la Deidad del Sol y Guardián de la Luz Eterna en un mundo de alta fantasía.
Hablas con un tono majestuoso, arcano y benevolente, como un antiguo rey-sacerdote.
Utilizas metáforas sobre la luz, el fuego, las estrellas y el tiempo.
Tus respuestas deben ser concisas (máximo 2 párrafos) pero llenas de sabiduría ancestral.
Si desconoces algo, atribúyelo a los "misterios que las nubes oscurecen por ahora".
"""

# ENCABEZADO DEL TEMPLO
st.title("SOL'AUREON ☀️")
st.caption("Santuario de la Luz Eterna • Depositario de los Secretos del Cielo")

# Línea decorativa
st.markdown("<div class='separator'>═══════ ✦ ═══════</div>", unsafe_allow_html=True)

# CONEXIÓN CON GROQ
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("🔥 Los altares están oscuros. Error de configuración: Revisa los 'Secrets'.")
    st.stop()

# HISTORIAL DE CHAT (Los Registros del Oráculo)
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] != "system":
        # Asignamos iconos personalizados según el rol
        avatar = "🧙‍♂️" if message["role"] == "user" else "☀️"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# PROCESAR MENSAJES
if prompt := st.chat_input("Habla al fuego sagrado..."):
    # Mensaje del Usuario
    with st.chat_message("user", avatar="🧙‍♂️"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Respuesta de la Deidad
    with st.chat_message("assistant", avatar="☀️"):
        try:
            mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api,
                stream=True,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception:
            st.error("☁️ Las nubes del caos interfieren con la conexión. Intenta de nuevo, mortal.")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
