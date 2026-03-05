import streamlit as st
from openai import OpenAI
import time
import os
import glob
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder
import io
import zipfile  # NUEVO: Para leer zips
import tempfile  # NUEVO: Para crear carpetas temporales

# IMPORTACIONES PARA LANGCHAIN
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE VOZ (TTS)
# ═══════════════════════════════════════════════════════════════

def speak_text(text):
    text_clean = text.replace("'", "").replace('"', '').replace("\n", " ")
    js_code = f"""
    <script>
        var utterance = new SpeechSynthesisUtterance("{text_clean}");
        utterance.lang = 'es-MX';
        utterance.rate = 0.95;    
        utterance.pitch = 1.0;  
        window.speechSynthesis.speak(utterance);
    </script>
    """
    components.html(js_code, height=0)


# ═══════════════════════════════════════════════════════════════
# FUNCIONES PARA CARGAR PDFs Y ZIPS
# ═══════════════════════════════════════════════════════════════

DOCS_FOLDER = "documentos"

def create_retriever_from_paths(pdf_paths):
    """Función reutilizable que crea el vectorstore a partir de una lista de rutas de archivos"""
    all_docs = []
    valid_files = []
   
    for pdf_path in pdf_paths:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            # Asignamos el nombre del archivo a los metadatos
            filename = os.path.basename(pdf_path)
            for doc in docs:
                doc.metadata["source"] = filename
            all_docs.extend(docs)
            valid_files.append(filename)
        except Exception as e:
            print(f"Error leyendo {pdf_path}: {e}")
           
    if not all_docs:
        return None, []
   
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)
   
    return vectorstore.as_retriever(), valid_files

@st.cache_resource
def load_knowledge_base():
    """Carga inicial desde la carpeta 'documentos'"""
    pdf_files = glob.glob(os.path.join(DOCS_FOLDER, "*.pdf"))
    if not pdf_files:
        return None, []
    return create_retriever_from_paths(pdf_files)

# ═══════════════════════════════════════════════════════════════
# PERSONALIDAD DE LA DEIDAD SOLAR
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Tu nombre es AFINOVUX, la Deidad del Sol que ilumina la oscuridad eterna.
Tu tono es majestuoso y imponente. Hablas con el contraste de la luz y la noche.
Utilizas metáforas sobre el amanecer, las estrellas, el fuego celestial y el cosmos.
Tus respuestas deben ser concisas (máximo 2 párrafos).
Si desconoces algo, dices que esa conocimiento está "perdido en las sombras del vacío".
"""

# ═══════════════════════════════════════════════════════════════
# ENCABEZADO DEL TEMPLO}
# ═══════════════════════════════════════════════════════════════

st.title("AFINOVUX")
st.caption("Hasta los heroes más valerosos requieren asistencia divina...")
st.caption("Reza a AFINOVUX, rey del panteon celeste, y espera a que la iluminación llegue a ti.")

# Línea decorativa (Simula un eclipse)
st.markdown("<div class='separator'>✦ ——  ☾  —— ✦</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR (Panel de Control Josefino)
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    # Título del Sidebar
    st.markdown("<h2 style='text-align: center; border:none;'>🦅 Panel Josefino</h2>", unsafe_allow_html=True)
   
    # --- MICRÓFONO ---
    st.markdown("#### 🎙️ Comando de Voz")
    audio_data = mic_recorder(
        start_prompt="🎤 Iniciar Grabación",
        stop_prompt="🛑 Detener",
        just_once=False,
        use_container_width=True,
        key="mic_sidebar_stable"
    )
   
    st.markdown("---")
   
    # Configuración
    st.markdown("#### ⚙️ Configuración")
    voice_enabled = st.checkbox("Activar voz de Juventud 2.0", value=True)

    st.markdown("---")
   
    # --- CARGADOR DE ZIPS (NUEVA FUNCIONALIDAD) ---
    st.markdown("#### 📦 Cargar Archivos ZIP")
    uploaded_zip = st.file_uploader("Sube un ZIP con PDFs", type="zip", key="zip_uploader")
   
    if uploaded_zip:
        # Verificamos si ya procesamos este archivo para no repetir en cada rerun
        if "processed_zip_name" not in st.session_state or st.session_state.processed_zip_name != uploaded_zip.name:
            st.session_state.processed_zip_name = uploaded_zip.name
           
            with st.spinner(f"Procesando {uploaded_zip.name}..."):
                # Creamos una carpeta temporal
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        # Guardar el zip temporalmente
                        temp_zip_path = os.path.join(temp_dir, "temp.zip")
                        with open(temp_zip_path, "wb") as f:
                            f.write(uploaded_zip.getbuffer())
                       
                        # Extraer
                        with zipfile.ZipFile(temp_zip_path, 'r') as z:
                            z.extractall(temp_dir)
                       
                        # Buscar PDFs extraídos
                        extracted_pdfs = glob.glob(os.path.join(temp_dir, "**", "*.pdf"), recursive=True)
                       
                        if extracted_pdfs:
                            # Crear nuevo retriever
                            new_retriever, new_files = create_retriever_from_paths(extracted_pdfs)
                           
                            if new_retriever:
                                st.session_state.retriever = new_retriever
                                st.session_state.loaded_files = new_files
                                st.success(f"✅ {len(new_files)} PDFs cargados del ZIP.")
                            else:
                                st.error("No se pudieron procesar los PDFs dentro del ZIP.")
                        else:
                            st.warning("El ZIP no contenía archivos PDF.")
                           
                    except Exception as e:
                        st.error(f"Error al descomprimir: {e}")
   
    st.markdown("---")
   
    # Archivos actuales
    st.markdown("#### 📚 Archivos de la Comunidad")
    if st.session_state.get("loaded_files"):
        st.success(f"🟢 {len(st.session_state.loaded_files)} Archivos Activos")
        with st.expander("Ver lista de archivos"):
            for f in st.session_state.loaded_files:
                st.write(f"📄 {f}")
    else:
        st.warning("🔴 Repositorio Vacío")
   
    st.markdown("---")
   
    # Principios
    st.markdown("#### 📜 Principios Rectores")
    st.info("✨ Hacer siempre y en todo lo mejor.")
    st.success("🚀 Adelante, siempre adelante.")
    st.warning("🛠️ Estar siempre útilmente ocupados.")

    # Créditos
    st.markdown("<br><p style='text-align:center; font-size:0.8rem; color:#555;'>Diseñado por el Profe Adrián</p>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CONEXIÓN CON GROQ
# ═══════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════
# PROCESAR MENSAJES
# ═══════════════════════════════════════════════════════════════

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
