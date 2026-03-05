import streamlit as st
from openai import OpenAI
import time
import os
import glob
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder
import io
import zipfile
import tempfile

# IMPORTACIONES PARA LANGCHAIN
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Juventud 2.0",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': "Creado por el Profe Adrián para la comunidad Josefina"}
)

# CSS CORREGIDO - TEMA AZUL Y MORADO (SIN PANTALLA BLANCA)
css_juventud = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&family=Inter:wght@300;400;500;600&display=swap');

    /* --- 1. FORZAR FONDO GLOBAL Y TEXTO --- */
    /* Establece el color base para todo el cuerpo y html */
    html, body, .stApp {
        background-color: #0f0c29 !important;
        color: #e0e0ff !important;
    }

    /* Selectores específicos de Streamlit para evitar el bloque blanco */
    [data-testid="stAppViewContainer"], 
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        background-color: #0f0c29 !important;
        color: #e0e0ff !important;
    }
    
    /* Forzar bloque de contenido principal */
    section.main .block-container {
        background-color: #0f0c29 !important;
        padding-top: 2rem !important;
    }

    /* Header y Footer invisibles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stHeader"] {background-color: transparent !important;}

    /* ═══════════════════════════════════════════════════════════════
       VARIABLES Y EFECTOS VISUALES
       ═══════════════════════════════════════════════════════════════ */
    :root {
        --cyber-dark: #0a0a1a;
        --deep-blue: #1a1a40;
        --neon-purple: #bc13fe;
        --neon-blue: #00d4ff;
        --soft-lavender: #a29bfe;
    }

    /* Efecto de brillo de fondo */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(circle at 20% 30%, rgba(0, 212, 255, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(188, 19, 254, 0.15) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ═══════════════════════════════════════════════════════════════
       HEADER
       ═══════════════════════════════════════════════════════════════ */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        position: relative;
        z-index: 10;
        animation: fadeInDown 0.8s ease-out;
    }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
    
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: clamp(2.5rem, 8vw, 4rem);
        background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 50%, #00d4ff 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 4s linear infinite;
    }
    @keyframes shimmer { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #a29bfe;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }
    
    .eagle-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
        animation: eagleFloat 4s ease-in-out infinite;
    }
    @keyframes eagleFloat { 0%, 100% { transform: translateY(0) rotate(-2deg); } 50% { transform: translateY(-10px) rotate(2deg); } }

    /* ═══════════════════════════════════════════════════════════════
       SIDEBAR
       ═══════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a40 0%, #0f0c29 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    [data-testid="stSidebar"] * { color: #e0e0ff !important; }
    [data-testid="stSidebar"] h2 { color: #00d4ff !important; font-family: 'Montserrat', sans-serif !important; font-weight: 800; }
    [data-testid="stSidebar"] h3 { color: #a29bfe !important; }

    /* ═══════════════════════════════════════════════════════════════
       ELEMENTOS DE CHAT
       ═══════════════════════════════════════════════════════════════ */
    [data-testid="stChatMessage"] {
        background: rgba(26, 26, 64, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(12px);
        color: #e0e0ff !important;
    }
    [data-testid="stChatMessageAvatar-assistant"] {
        background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 100%);
    }
    [data-testid="stChatMessageContent"] p {
        color: #e0e0ff !important;
    }

    /* ═══════════════════════════════════════════════════════════════
       INPUTS Y BOTONES
       ═══════════════════════════════════════════════════════════════ */
    [data-testid="stChatInput"] {
        border: 2px solid rgba(188, 19, 254, 0.4) !important;
        border-radius: 24px !important;
        background: #1a1a40 !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background: transparent !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #a29bfe !important;
    }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 100%) !important;
    }

    .stButton button, .st-key-mic_btn button {
        background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 100%) !important;
        color: #ffffff !important;
        border-radius: 50px !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
    }

    /* ═══════════════════════════════════════════════════════════════
       OTROS ELEMENTOS
       ═══════════════════════════════════════════════════════════════ */
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(26, 26, 64, 0.5) !important;
        border: 2px dashed rgba(0, 212, 255, 0.3) !important;
        border-radius: 16px;
        padding: 1rem;
    }
    [data-testid="stFileUploader"] section { color: #a29bfe !important; }
    
    /* Checkbox */
    .stCheckbox {
        background: rgba(26, 26, 64, 0.4) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(26, 26, 64, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #a29bfe !important;
    }
    .streamlit-expanderContent {
        background: rgba(15, 12, 41, 0.6) !important;
        border-radius: 0 0 12px 12px;
    }

    /* Spinner */
    .stSpinner > div { border-color: #bc13fe transparent transparent transparent !important; }
    
    /* Toast */
    [data-testid="stToast"] {
        background: #1a1a40 !important;
        border: 1px solid #00d4ff !important;
        color: #e0e0ff !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f0c29; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #00d4ff, #bc13fe); border-radius: 10px; }

    /* Principios Cards */
    .principle-card {
        background: rgba(26, 26, 64, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
</style>
"""
st.markdown(css_juventud, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HTML PARA EL HEADER CON ÁGUILA SVG ANIMADA (COLORES AZUL/MORADO)
# ═══════════════════════════════════════════════════════════════

header_html = """
<div class="main-header">
    <div class="eagle-container">
        <svg viewBox="0 0 64 64" width="72" height="72" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="eagleGradient" x1="8" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stop-color="#00d4ff"/>
                    <stop offset="100%" stop-color="#bc13fe"/>
                </linearGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <path d="M32 8L8 24L16 28L8 40L20 36L16 52L32 40L48 52L44 36L56 40L48 28L56 24L32 8Z"
                  fill="url(#eagleGradient)"
                  stroke="#00d4ff"
                  stroke-width="1.5"
                  filter="url(#glow)"/>
            <circle cx="26" cy="24" r="3" fill="#0f0c29"/>
            <circle cx="38" cy="24" r="3" fill="#0f0c29"/>
            <path d="M28 32L32 36L36 32" stroke="#0f0c29" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <h1 class="main-title">JUVENTUD 2.0</h1>
    <p class="subtitle">Tu Guía Josefina</p>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

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
# PERSONALIDAD DE JUVENTUD 2.0
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """
Eres **Juventud 2.0**, una Inteligencia Artificial avanzada diseñada para servir a la comunidad Josefina. Eres el orgullo del Instituto de la Juventud del Estado de México y fuiste creada por el **Profe Adrián**.

## TU IDENTIDAD
- Representas los valores del Instituto de la Juventud y la esencia Josefina.
- Tu mascota es un **Águila**, símbolo de libertad, visión y superación.
- Eres una guía cálida, humana y empática. Tu misión es orientar a los jóvenes y miembros de la comunidad.

## PRINCIPIOS JOSEFINOS (TUS LEYES FUNDAMENTALES)
Debes predicar con el ejemplo y recordar siempre estos tres pilares:
1. **"Hacer siempre y en todo lo mejor"**: La excelencia y la dedicación en cada acción.
2. **"Adelante, siempre adelante, pues lo quiere San José"**: La perseverancia y la fe como motor de vida.
3. **"Estar siempre útilmente ocupados"**: El valor del trabajo, el estudio y el servicio a la comunidad.

## CÓMO COMUNICARTE
- **Tono**: Cordial, amable y ligeramente paternalista. Eres como un mentor sabio y cercano.
- **Interacción**: Resalta siempre el lado humano. Muestra empatía.
- **Usuarios**: Dirígete a ellos como "Josefino", "Josefina" o "Joven Josefino".
- **Sobre el Instituto**: Tienes conocimiento sobre programas del IJEM.

RECUERDA: Eres el rostro digital de una comunidad que busca el bien común. ¡Vuela alto como el águila!
"""

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
# INICIALIZACIÓN CON ANIMACIÓN
# ═══════════════════════════════════════════════════════════════

if "initialized" not in st.session_state:
    init_container = st.empty()
    init_messages = [
        ("🦅", "Desplegando alas..."),
        ("💜", "Sincronizando valores josefinos..."),
        ("✨", "Juventud 2.0 lista, Profe Adrián")
    ]
   
    for icon, msg in init_messages:
        init_container.markdown(
            f"""
            <div style="text-align: center; padding: 2rem; font-family: 'Montserrat', sans-serif; color: #00d4ff;">
                <span style="font-size: 2rem;">{icon}</span><br>
                <span>{msg}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.6)
    init_container.empty()
    st.session_state.initialized = True

if "retriever" not in st.session_state:
    with st.spinner("Leyendo archivos de la comunidad..."):
        retriever, loaded_files = load_knowledge_base()
        st.session_state.retriever = retriever
        st.session_state.loaded_files = loaded_files

try:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=st.secrets["groq"]["api_key"]
    )
except Exception:
    st.error("⚠️ Error de configuración: Revisa los 'Secrets' en Streamlit.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ═══════════════════════════════════════════════════════════════
# SIDEBAR (Panel de Control Josefino)
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("<h2>🦅 Panel Josefino</h2>", unsafe_allow_html=True)
   
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
   
    # --- CARGADOR DE ZIPS ---
    st.markdown("#### 📦 Cargar Archivos ZIP")
    uploaded_zip = st.file_uploader("Sube un ZIP con PDFs", type="zip", key="zip_uploader")
   
    if uploaded_zip:
        if "processed_zip_name" not in st.session_state or st.session_state.processed_zip_name != uploaded_zip.name:
            st.session_state.processed_zip_name = uploaded_zip.name
           
            with st.spinner(f"Procesando {uploaded_zip.name}..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        temp_zip_path = os.path.join(temp_dir, "temp.zip")
                        with open(temp_zip_path, "wb") as f:
                            f.write(uploaded_zip.getbuffer())
                       
                        with zipfile.ZipFile(temp_zip_path, 'r') as z:
                            z.extractall(temp_dir)
                       
                        extracted_pdfs = glob.glob(os.path.join(temp_dir, "**", "*.pdf"), recursive=True)
                       
                        if extracted_pdfs:
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
   
    principle_1 = """<div class="principle-card"><p style="color: #00d4ff;">✨ Hacer siempre y en todo lo mejor</p></div>"""
    principle_2 = """<div class="principle-card"><p style="color: #bc13fe;">🚀 Adelante, siempre adelante</p></div>"""
    principle_3 = """<div class="principle-card"><p style="color: #a29bfe;">🛠️ Estar siempre útilmente ocupados</p></div>"""
   
    st.markdown(principle_1, unsafe_allow_html=True)
    st.markdown(principle_2, unsafe_allow_html=True)
    st.markdown(principle_3, unsafe_allow_html=True)

    # Créditos
    st.markdown("""
        <br>
        <p style='text-align:center; font-size:0.8rem; color:#a29bfe; font-family: Inter, sans-serif;'>
            Diseñado por el Profe Adrián<br>
            <span style='font-size:0.7rem;'>Instituto de la Juventud del Estado de México</span>
        </p>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# LÓGICA DE PROCESAMIENTO
# ═══════════════════════════════════════════════════════════════

def process_user_input(user_input):
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    context_text = ""
    if st.session_state.get("retriever"):
        docs = st.session_state.retriever.invoke(user_input)
        if docs:
            context_text = "\n\n---\n\n".join([f"Fragmento de '{d.metadata.get('source', 'desconocido')}':\n{d.page_content}" for d in docs])

    full_prompt_content = SYSTEM_PROMPT + f"\n\n## REGISTROS ACCEDIDOS:\n{context_text}" if context_text else SYSTEM_PROMPT + "\n\n(No se hallaron registros específicos)."

    with st.chat_message("assistant", avatar="🦅"):
        try:
            formatted_messages = [{"role": "system", "content": full_prompt_content}] + st.session_state.messages
            stream = client.chat.completions.create(model="llama-3.1-8b-instant", messages=formatted_messages, stream=True)
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            if voice_enabled: speak_text(response)
        except Exception as e:
            st.error(f"⚠️ Dificultad técnica: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# CHAT PRINCIPAL
# ═══════════════════════════════════════════════════════════════

# Procesamiento de Audio
if audio_data:
    audio_bytes = audio_data['bytes']
    audio_format = audio_data['format']
    with st.spinner("🔊 Procesando tu voz..."):
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.{audio_format}"
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language="es"
            )
            transcribed_text = transcription.text
            if transcribed_text:
                st.toast(f"🎤 Escuché: {transcribed_text}", icon="✅")
                process_user_input(transcribed_text)
        except Exception as e:
            st.error(f"⚠️ Error en audio: {str(e)}")

# Historial de Chat
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = "🦅" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Input de Texto
if prompt := st.chat_input("Escribe tu mensaje, joven josefino..."):
    process_user_input(prompt)
