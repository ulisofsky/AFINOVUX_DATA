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
    page_title="AFINOVUX",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': "La deidad mayor de la tierra del plenilunio..."}
)

# CSS CORREGIDO - TEMA FANTASÍA PARA AFINOVUX
css_juventud = """
<style>
    /* Importamos Montserrat, Inter y la fuente de fantasía Cinzel Decorative */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Montserrat:wght@400;600;800;900&family=Inter:wght@300;400;500;600&display=swap');

    /* --- 1. FORZAR FONDO GLOBAL Y TEXTO --- */
    html, body, .stApp {
        background-color: #0f0c29 !important;
        color: #e0e0ff !important;
    }

    /* Selectores específicos de Streamlit */
    [data-testid="stAppViewContainer"], 
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        background-color: #0f0c29 !important;
        color: #e0e0ff !important;
    }
    
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

    :root {
        --cyber-dark: #0a0a1a;
        --deep-blue: #1a1a40;
        --neon-purple: #bc13fe;
        --neon-blue: #00d4ff;
        --soft-lavender: #a29bfe;
        --gold-glow: #ffd700;
    }

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

    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        position: relative;
        z-index: 10;
        animation: fadeInDown 0.8s ease-out;
    }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
    
    /* ESTILO DEL TÍTULO PRINCIPAL (AFINOVUX) - FANTASÍA */
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

    /* ANIMACIÓN PARA LA LUNA */
    .moon-container {
        animation: float 6s ease-in-out infinite;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a40 0%, #0f0c29 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    [data-testid="stSidebar"] * { color: #e0e0ff !important; }
    [data-testid="stSidebar"] h2 { color: #00d4ff !important; font-family: 'Montserrat', sans-serif !important; font-weight: 800; }
    [data-testid="stSidebar"] h3 { color: #a29bfe !important; }

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

    [data-testid="stFileUploader"] {
        background: rgba(26, 26, 64, 0.5) !important;
        border: 2px dashed rgba(0, 212, 255, 0.3) !important;
        border-radius: 16px;
        padding: 1rem;
    }
    [data-testid="stFileUploader"] section { color: #a29bfe !important; }
    
    .stCheckbox {
        background: rgba(26, 26, 64, 0.4) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        border: 1px solid rgba(0, 212, 255, 0.1);
    }

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

    .stSpinner > div { border-color: #bc13fe transparent transparent transparent !important; }
    
    [data-testid="stToast"] {
        background: #1a1a40 !important;
        border: 1px solid #00d4ff !important;
        color: #e0e0ff !important;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f0c29; }
    ::-webkit
