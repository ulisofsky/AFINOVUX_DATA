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
import base64  # NUEVA IMPORTACIÓN PARA MANEJAR IMÁGENES EN HTML

# IMPORTACIONES PARA LANGCHAIN
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# CONFIGURACIÓN DE PÁGINA
# Se cambia page_icon para usar el logo
st.set_page_config(
    page_title="AFINOVUX",
    page_icon="LOGO.png",  # Cambiado de emoji a archivo
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': "La deidad mayor de la tierra del plenilunio..."}
)

# CSS - TEMA FANTASÍA (Sin cambios relevantes en el CSS)
css_juventud = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Montserrat:wght@400;600;800;900&family=Inter:wght@300;400;500;600&display=swap');

    html, body, .stApp {
        background-color: #0f0c29 !important;
        color: #e0e0ff !important;
    }

    [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .stMainBlockContainer {
        background-color: #0f0c29 !important;
        color: #e0e0ff !important;
    }
    
    section.main .block-container {
        background-color: #0f0c29 !important;
        padding-top: 2rem !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stHeader"] {background-color: transparent !important;}

    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        position: relative;
        z-index: 10;
        animation: fadeInDown 0.8s ease-out;
    }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
    
    .main-title {
        font-family: 'Cinzel Decorative', serif;
        font-weight: 900;
        font-size: clamp(3.5rem, 10vw, 6rem);
        background: linear-gradient(135deg, #ffd700 0%, #ffeedd 25%, #ffffff 50%, #ffd700 75%, #bc13fe 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 4s linear infinite;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
        margin-bottom: 0.5rem;
        letter-spacing: 4px;
    }
    @keyframes shimmer { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #a29bfe;
        letter-spacing: 6px;
        text-transform: uppercase;
        margin-top: 0.5rem;
        font-size: 1rem;
    }

    .moon-container {
        animation: float 6s ease-in-out infinite;
        display: inline-block;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    /* Estilo para la imagen del logo */
    .logo-img {
        width: 120px; /* Ajusta el tamaño según necesites */
        height: auto;
        border-radius: 50%; /* Opcional: hace la imagen circular */
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a40 0%, #0f0c29 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    [data-testid="stSidebar"] * { color: #e0e0ff !important; }
    [data-testid="stSidebar"] h2 { color: #00d4ff !important; font-family: 'Montserrat', sans-serif !important; font-weight: 800; }
    
    [data-testid="stChatMessage"] {
        background: rgba(26, 26, 64, 0.6) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(12px);
        color: #e0e0ff !important;
    }
    [data-testid="stChatMessageAvatar-assistant"] { background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 100%); }
    [data-testid="stChatMessageContent"] p { color: #e0e0ff !important; }

    [data-testid="stChatInput"] { border: 2px solid rgba(188, 19, 254, 0.4) !important; border-radius: 24px !important; background: #1a1a40 !important; }
    [data-testid="stChatInput"] textarea { color: #ffffff !important; background: transparent !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: #a29bfe !important; }
    [data-testid="stChatInput"] button { background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 100%) !important; }

    .stButton button { background: linear-gradient(135deg, #00d4ff 0%, #bc13fe 100%) !important; color: #ffffff !important; border-radius: 50px !important; border: none !important; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4); }
    
    [data-testid="stFileUploader"] { background: rgba(26, 26, 64, 0.5) !important; border: 2px dashed rgba(0, 212, 255, 0.3) !important; border-radius: 16px; padding: 1rem; }
    .stCheckbox { background: rgba(26, 26, 64, 0.4) !important; border-radius: 12px; padding: 0.75rem 1rem; border: 1px solid rgba(0, 212, 255, 0.1); }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f0c29; }
    ::-webkit-scrollbar-thumb { background: #bc13fe; border-radius: 4px; }
</style>
"""

# INYECTAR CSS
st.markdown(css_juventud, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HTML DEL ENCABEZADO (LOGO) - MODIFICADO
# ═══════════════════════════════════════════════════════════════

def get_base64_image(path):
    """Convierte una imagen local a base64 para incrustarla en HTML"""
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception:
        return None

# Intentar cargar LOGO.png o LOGO.jpg
logo_base64 = None
logo_path = None
if os.path.exists("LOGO.png"):
    logo_path = "LOGO.png"
elif os.path.exists("LOGO.jpg"):
    logo_path = "LOGO.jpg"

if logo_path:
    logo_base64 = get_base64_image(logo_path)

if logo_base64:
    # Si se encontró la imagen, mostrarla
    img_src = f"data:image/png;base64,{logo_base64}" if logo_path.endswith('.png') else f"data:image/jpeg;base64,{logo_base64}"
    header_html = f"""
    <div class="main-header">
        <div class="moon-container">
            <img src="{img_src}" class="logo-img">
        </div>
        <h1 class="main-title">AFINOVUX</h1>
        <p class="subtitle">Deidad del Plenilunio</p>
    </div>
    """
else:
    # Fallback por si no encuentra la imagen, muestra un texto o placeholder
    header_html = """
    <div class="main-header">
        <div class="moon-container">
            <div style="width:80px; height:80px; background:rgba(255,255,255,0.1); border-radius:50%; border: 2px solid #ffd700;"></div>
        </div>
        <h1 class="main-title">AFINOVUX</h1>
        <p class="subtitle">Deidad del Plenilunio</p>
    </div>
    """

st.markdown(header_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE VOZ Y LÓGICA
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

SYSTEM_PROMPT = """
Eres **AFINOVUX**, la deidad más poderosa de la Tierra del Plenilunio. Guias a los heroes que ruegan a ti hacia la verdad.
## TU IDENTIDAD
- Representas la proteccion del mundo contra el mal
- Tus simbolos son el sol naciente, los astros y la luz
## CÓMO COMUNICARTE
- **Tono**: Cordial pero imponente. Eres como un mentor sabio
- **Usuarios**: Dirígete a ellos como "Heroe", "Aventurero" o "Mortal".
- **Sabiduria**: Tienes conocimiento sobre todos los documentos a los que tienes acceso
"""

DOCS_FOLDER = "Documents"

def create_retriever_from_paths(pdf_paths):
    all_docs = []
    valid_files = []
    for pdf_path in pdf_paths:
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            filename = os.path.basename(pdf_path)
            for doc in docs: doc.metadata["source"] = filename
            all_docs.extend(docs)
            valid_files.append(filename)
        except Exception as e: print(f"Error: {e}")
    if not all_docs: return None, []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore.as_retriever(), valid_files

@st.cache_resource
def load_knowledge_base():
    pdf_files = glob.glob(os.path.join(DOCS_FOLDER, "*.pdf"))
    if not pdf_files: return None, []
    return create_retriever_from_paths(pdf_files)

if "initialized" not in st.session_state:
    init_container = st.empty()
    for msg in ["Del ocaso al alba...", "La cuspide divina...", "Plegaria respondida"]:
        init_container.markdown(f"<div style='text-align: center; padding: 2rem; color: #00d4ff;'>{msg}</div>", unsafe_allow_html=True)
        time.sleep(0.5)
    init_container.empty()
    st.session_state.initialized = True

if "retriever" not in st.session_state:
    with st.spinner("Recuperando conocimientos ancestrales..."):
        st.session_state.retriever, st.session_state.loaded_files = load_knowledge_base()

try:
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=st.secrets["groq"]["api_key"])
except Exception:
    st.error("Los conocimientos que buscas se han perdido hace eones...")
    st.stop()

if "messages" not in st.session_state: st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.markdown("<h2>Templo del Alba</h2>", unsafe_allow_html=True)
    st.markdown("#### 🎙️ Comando de Voz")
    audio_data = mic_recorder(start_prompt="🎤 Iniciar", stop_prompt="🛑 Detener", just_once=False, use_container_width=True, key="mic_sidebar")
    st.markdown("---")
    voice_enabled = st.checkbox("Activar voz de AFINOVUX", value=True)
    st.markdown("---")
    st.markdown("#### 📦 Cargar ZIP")
    uploaded_zip = st.file_uploader("PDFs en ZIP", type="zip", key="zip_up")
    if uploaded_zip:
        if "processed_zip_name" not in st.session_state or st.session_state.processed_zip_name != uploaded_zip.name:
            st.session_state.processed_zip_name = uploaded_zip.name
            with st.spinner("Procesando..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    try:
                        temp_path = os.path.join(temp_dir, "t.zip")
                        with open(temp_path, "wb") as f: f.write(uploaded_zip.getbuffer())
                        with zipfile.ZipFile(temp_path, 'r') as z: z.extractall(temp_dir)
                        pdfs = glob.glob(os.path.join(temp_dir, "**", "*.pdf"), recursive=True)
                        if pdfs:
                            st.session_state.retriever, st.session_state.loaded_files = create_retriever_from_paths(pdfs)
                            st.success(f"✅ {len(st.session_state.loaded_files)} PDFs cargados.")
                    except Exception as e: st.error(f"Error: {e}")
    st.markdown("---")
    st.markdown("#### 📚 Archivos")
    if st.session_state.get("loaded_files"):
        st.success(f"🟢 {len(st.session_state.loaded_files)} Activos")
    else: st.warning("🔴 Vacío")

def process_user_input(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"): st.markdown(user_input)
    
    context = ""
    if st.session_state.get("retriever"):
        docs = st.session_state.retriever.invoke(user_input)
        if docs: context = "\n\n---\n\n".join([f"Fragmento de '{d.metadata.get('source')}':\n{d.page_content}" for d in docs])
    
    prompt_content = SYSTEM_PROMPT + f"\n\n## REGISTROS:\n{context}" if context else SYSTEM_PROMPT
    
    with st.chat_message("assistant", avatar="🌙"):
        try:
            msgs = [{"role": "system", "content": prompt_content}] + st.session_state.messages
            stream = client.chat.completions.create(model="llama-3.1-8b-instant", messages=msgs, stream=True, temperature=0.7, frequency_penalty=0.5)
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            if voice_enabled: speak_text(response)
        except Exception as e: st.error(f"Error: {e}")

if audio_data:
    with st.spinner("🔊 Procesando voz..."):
        try:
            af = io.BytesIO(audio_data['bytes'])
            af.name = f"audio.{audio_data['format']}"
            text = client.audio.transcriptions.create(file=af, model="whisper-large-v3", language="es").text
            if text: process_user_input(text)
        except: pass

for msg in st.session_state.messages:
    if msg["role"] != "system":
        av = "🌙" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=av): st.markdown(msg["content"])

# CORRECCIÓN: Línea final arreglada
if prompt := st.chat_input("Reza ante los dioses..."): process_user_input(prompt)
