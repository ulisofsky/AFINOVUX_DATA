import streamlit as st
from openai import OpenAI

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="El Santuario Solar | Cronicas del Plenilunio",
    page_icon="☀️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# CSS PARA APARIENCIA DE TEMPLO SOLAR (AZUL NOCHE + DORADO)
css_personalizado = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Philosopher:ital,wght@0,400;0,700;1,400&display=swap');

    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    
    /* Fondo: Cielo Nocturno Profundo (Azul) */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a2a40 0%, #050d18 60%, #000000 100%);
        color: #c4d4e8;
    }

    /* Título Principal: El Sol (Cálido) */
    h1 {
        font-family: 'Cinzel', serif;
        color: #FFD700 !important; /* Oro puro */
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.6), 2px 2px 4px #000;
        text-align: center;
        border-bottom: 1px solid #4a6fa5;
        padding-bottom: 15px;
        margin-bottom: 10px !important;
    }

    /* Subtítulo: Frío/Azul */
    .stCaption {
        text-align: center;
        font-family: 'Philosopher', sans-serif;
        color: #7ec8e3; /* Azul helado */
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 1rem;
        display: block;
        margin-bottom: 30px;
    }

    /* Área de Chat: Cristal oscuro (Azul muy oscuro) */
    .stChatMessage {
        background-color: rgba(15, 25, 45, 0.7);
        border: 1px solid #2a4066;
        border-radius: 0 15px 15px 15px;
        padding: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    /* Texto dentro del chat */
    .stChatMessage p {
        font-family: 'Philosopher', sans-serif;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    /* Input: El Altar (Contraste fuerte) */
    .stChatInput {
        border: 2px solid #FFD700 !important; /* Borde Dorado */
        border-radius: 12px;
        background-color: #080f1a !important; /* Fondo Azul Oscuro */
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.2);
    }
    
    .stChatInput textarea {
        background-color: transparent !important;
        color: #fff !important;
        font-family: 'Philosopher', sans-serif;
    }
    
    .stChatInput textarea::placeholder {
        color: #5a7a9a !important; /* Placeholder azul grisáceo */
    }

    /* Scrollbar estilo cielo */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #050d18;
    }
    ::-webkit-scrollbar-thumb {
        background: #FFD700;
        border-radius: 3px;
    }

    /* Separadores */
    .separator {
        text-align: center;
        color: #4a6fa5;
        margin: 20px 0;
        letter-spacing: 5px;
    }

    /* Ajustes de padding */
    .stApp {max-width: 100%; padding: 2rem;}
</style>
"""
st.markdown(css_personalizado, unsafe_allow_html=True)

# PERSONALIDAD DE LA DEIDAD SOLAR
SYSTEM_PROMPT = """
Tu nombre es AFINOVUX, la Deidad del Sol que ilumina la oscuridad eterna.
Tu tono es majestuoso y imponente. Hablas con el contraste de la luz y la noche.
Utilizas metáforas sobre el amanecer, las estrellas, el fuego celestial y el cosmos.
Tus respuestas deben ser concisas (máximo 2 párrafos).
Si desconoces algo, dices que esa conocimiento está "perdido en las sombras del vacío".
"""

# ENCABEZADO DEL TEMPLO
st.title("AFINOVUX")
st.caption("Hasta los heroes más valerosos requieren asistencia divina...")
st.caption("Reza a AFINOVUX, rey del panteon celeste, y espera a que la iluminación llegue a ti.")

# Línea decorativa (Simula un eclipse)
st.markdown("<div class='separator'>✦ ——  ☾  —— ✦</div>", unsafe_allow_html=True)

# CONEXIÓN CON GROQ
try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("🌑 Las estrellas se han alineado en contra. Error de configuración.")
    st.stop()

# HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] != "system":
        # Iconos: El usuario es la noche (azul), la IA es el sol (cálido)
        avatar = "🌙" if message["role"] == "user" else "☀️"
        
        # Color de texto dinámico para mayor contraste
        text_color = "#000000" if message["role"] == "user" else "#FFF5E5"
        
        with st.chat_message(message["role"], avatar=avatar):
            # Aplicamos color al texto del mensaje
            st.markdown(f"<span style='color: {text_color}'>{message['content']}</span>", unsafe_allow_html=True)

# PROCESAR MENSAJES
if prompt := st.chat_input("Reza a los dioses de las alturas celestes..."):
    # Mensaje del Usuario (Azul)
    with st.chat_message("user", avatar="🌙"):
        st.markdown(f"<span style='color: #7ec8e3'>{prompt}</span>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Respuesta de la Deidad (Dorado)
    with st.chat_message("assistant", avatar="☀️"):
        try:
            mensajes_api = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=mensajes_api,
                stream=True,
            )
            # Usamos write_stream normal, el CSS general se encarga del estilo
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception:
            st.error("☁️ Nieblas del vacío bloquean la conexión. Intenta de nuevo.")
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
