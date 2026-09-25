import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import joblib
import base64
import requests
import time
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

from feature_extraction import extract_features, FEATURE_COLUMNS
from whitelist import est_domaine_fiable
from icons import icon

# ======================
# CONFIGURATION
# ======================
st.set_page_config(
    page_title="LoupeURL - Detection d'URLs Malveillantes",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAIL_API_URL = "https://urlapit.netlify.app/.netlify/functions/server"
ASSETS_DIR = Path(__file__).parent / "assets"


@st.cache_data
def get_logo_base64():
    logo_path = ASSETS_DIR / "logo_small.png"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return None

LOGO_B64 = get_logo_base64()

# ======================
# ÉTAT DE SESSION — MODE CLAIR PAR DÉFAUT
# ======================
if "page" not in st.session_state:
    st.session_state.page = "Accueil"
if "historique" not in st.session_state:
    st.session_state.historique = []
if "theme" not in st.session_state:
    st.session_state.theme = "light"   # ← MODE CLAIR PAR DÉFAUT

# ======================
# CSS
# ======================
def get_css(theme):
    if theme == "dark":
        v = {
            "bg": "radial-gradient(ellipse at top left, #101a35 0%, #0a0e1a 55%, #060911 100%)",
            "sidebar_bg": "linear-gradient(180deg, #0c1226 0%, #0a0e1a 100%)",
            "sidebar_border": "rgba(99,102,241,0.15)",
            "text_main": "#f1f5f9",
            "text_muted": "#94a3b8",
            "text_faint": "#94a3b8",
            "border": "rgba(255,255,255,0.1)",
            "surface": "rgba(255,255,255,0.03)",
            "surface2": "rgba(255,255,255,0.06)",
            "input_bg": "#1e293b",
            "input_border": "rgba(99,102,241,0.35)",
            "input_text": "#ffffff",
            "input_placeholder": "#94a3b8",
            "step_text": "#cbd5e1",
            "title_color": "#ffffff",
            "label_color": "#cbd5e1",
        }
    else:
        v = {
            "bg": "radial-gradient(ellipse at top left, #eef1fb 0%, #f6f8fc 55%, #ffffff 100%)",
            "sidebar_bg": "linear-gradient(180deg, #ffffff 0%, #f4f6fb 100%)",
            "sidebar_border": "rgba(99,102,241,0.15)",
            "text_main": "#0f172a",
            "text_muted": "#475569",
            "text_faint": "#64748b",
            "border": "rgba(15,23,42,0.09)",
            "surface": "#ffffff",
            "surface2": "rgba(15,23,42,0.04)",
            "input_bg": "#ffffff",
            "input_border": "rgba(99,102,241,0.3)",
            "input_text": "#0f172a",
            "input_placeholder": "#94a3b8",
            "step_text": "#334155",
            "title_color": "#0f172a",
            "label_color": "#334155",
        }

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ===== MASQUER UNIQUEMENT LES BOUTONS CLOUD ===== */
[data-testid="stAppDeployButton"],
[data-testid="stManageAppButton"],
.stAppDeployButton,
.stDeployButton,
[data-testid="stToolbarActions"] {{
    display: none !important;
}}

/* ===== HEADER TRANSPARENT MAIS AVEC HAUTEUR ===== */
header[data-testid="stHeader"] {{
    background: transparent !important;
    background-color: transparent !important;
    height: 3.5rem !important;
    min-height: 3.5rem !important;
    box-shadow: none !important;
}}

/* ===== BOUTON TOGGLE SIDEBAR (BLANC + FLÈCHE BLEU MARINE) ===== */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"],
button[kind="header"],
button[kind="headerNoPadding"],
button[data-testid="stBaseButton-header"],
button[data-testid="stBaseButton-headerNoPadding"],
header[data-testid="stHeader"] button {{
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #1e2a5e !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(30,42,94,0.2) !important;
    z-index: 999999 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    padding: 8px 10px !important;
    margin: 6px !important;
    min-width: 40px !important;
    min-height: 40px !important;
}}

[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="collapsedControl"]:hover,
button[kind="header"]:hover,
button[kind="headerNoPadding"]:hover {{
    background: #f1f5f9 !important;
    transform: scale(1.05) !important;
    box-shadow: 0 6px 18px rgba(30,42,94,0.4) !important;
}}

[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stExpandSidebarButton"] svg,
button[kind="header"] svg,
button[kind="headerNoPadding"] svg,
header[data-testid="stHeader"] button svg {{
    fill: #1e2a5e !important;
    color: #1e2a5e !important;
    stroke: #1e2a5e !important;
    width: 20px !important;
    height: 20px !important;
}}

/* ===== SELECTBOX ===== */
.stSelectbox > div > div,
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {{
    background-color: {v['input_bg']} !important;
    background: {v['input_bg']} !important;
    border: 2px solid #8b5cf6 !important;
    border-radius: 10px !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
}}

.stSelectbox > div > div > div,
.stSelectbox > div > div > div > div,
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div,
div[data-baseweb="select"] > div > div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] p {{
    color: {v['input_text']} !important;
    -webkit-text-fill-color: {v['input_text']} !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    opacity: 1 !important;
}}

div[data-baseweb="select"] svg,
div[data-baseweb="select"] [data-baseweb="icon"] svg {{
    fill: #8b5cf6 !important;
    color: #8b5cf6 !important;
    stroke: #8b5cf6 !important;
    width: 20px !important;
    height: 20px !important;
}}

/* Menu ouvert */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div {{
    background-color: {v['surface']} !important;
    border: 2px solid #8b5cf6 !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
}}

ul[data-baseweb="menu"],
div[data-baseweb="popover"] ul,
[role="listbox"] {{
    background-color: {v['surface']} !important;
    border-radius: 8px !important;
    padding: 6px !important;
}}

li[role="option"],
[role="option"] {{
    background-color: {v['surface']} !important;
    color: {v['text_main']} !important;
    font-weight: 500 !important;
    padding: 14px 18px !important;
    font-size: 0.95rem !important;
    border-radius: 6px !important;
    margin: 2px 0 !important;
    border-left: 4px solid transparent !important;
    transition: all 0.15s ease !important;
}}

li[role="option"]:hover,
[role="option"]:hover {{
    background-color: rgba(99, 102, 241, 0.15) !important;
    color: {v['text_main']} !important;
    border-left: 4px solid #8b5cf6 !important;
    padding-left: 22px !important;
}}

li[aria-selected="true"],
[role="option"][aria-selected="true"] {{
    background: linear-gradient(90deg, rgba(139, 92, 246, 0.25), rgba(99, 102, 241, 0.12)) !important;
    color: {v['text_main']} !important;
    border-left: 4px solid #8b5cf6 !important;
    font-weight: 700 !important;
    padding-left: 22px !important;
}}

div[data-baseweb="popover"] div,
ul[data-baseweb="menu"] div,
[role="listbox"] div,
[role="option"] span,
[role="option"] div {{
    color: {v['text_main']} !important;
    background-color: transparent !important;
}}

/* ===== MASQUER LA BANDE STREAMLIT CLOUD ===== */
[data-testid="stManageAppButton"],
iframe[title="streamlit_app_manage_button"],
.viewerBadge_container__1QSob,
.viewerBadge_link__1S137,
[class*="viewerBadge"] {{
    display: none !important;
}}

[data-testid="stBottom"] > div:last-child,
footer[data-testid="stBottom"] {{
    display: none !important;
}}

[data-testid="stUserMenu"],
[data-testid="stProfileButton"],
.stUserAvatar {{
    display: none !important;
}}

/* ===== CONTENU PRINCIPAL ===== */
.main .block-container {{
    padding-top: 1rem !important;
}}
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.stApp {{ background: {v['bg']}; }}

h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
    color: {v['title_color']} !important;
}}
div[data-testid="stMarkdownContainer"] h1,
div[data-testid="stMarkdownContainer"] h2,
div[data-testid="stMarkdownContainer"] h3,
div[data-testid="stMarkdownContainer"] h4,
div[data-testid="stMarkdownContainer"] h5 {{
    color: {v['title_color']} !important;
}}

p, span, div, label {{ color: {v['text_main']}; }}
.stMarkdown p {{ color: {v['text_main']} !important; }}

.stTextInput input,
.stTextInput input:hover,
.stTextInput input:focus,
.stTextInput input:active {{
    background-color: {v['input_bg']} !important;
    border: 1.5px solid {v['input_border']} !important;
    color: {v['input_text']} !important;
    -webkit-text-fill-color: {v['input_text']} !important;
    caret-color: #6366f1 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}}
.stTextInput input::placeholder {{
    color: {v['input_placeholder']} !important;
    -webkit-text-fill-color: {v['input_placeholder']} !important;
    opacity: 0.8 !important;
}}

.stTextArea textarea,
.stTextArea textarea:hover,
.stTextArea textarea:focus,
.stTextArea textarea:active {{
    background-color: {v['input_bg']} !important;
    border: 1.5px solid {v['input_border']} !important;
    color: {v['input_text']} !important;
    -webkit-text-fill-color: {v['input_text']} !important;
    caret-color: #6366f1 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}}
.stTextArea textarea::placeholder {{
    color: {v['input_placeholder']} !important;
    -webkit-text-fill-color: {v['input_placeholder']} !important;
    opacity: 0.8 !important;
}}

div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"],
div[data-baseweb="textarea"] > div,
div[data-baseweb="base-input"] {{
    background-color: {v['input_bg']} !important;
    border-color: {v['input_border']} !important;
}}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] input {{
    background-color: {v['input_bg']} !important;
    color: {v['input_text']} !important;
    -webkit-text-fill-color: {v['input_text']} !important;
}}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stRadio label,
.stCheckbox label {{
    color: {v['label_color']} !important;
}}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {{
    background: {v['sidebar_bg']} !important;
    border-right: 1px solid {v['sidebar_border']} !important;
}}
section[data-testid="stSidebar"] > div {{ padding-top: 0 !important; }}

.brand-block {{
    display: flex; align-items: center; gap: 12px;
    padding: 1.6rem 1.2rem 1.2rem 1.2rem;
    border-bottom: 1px solid {v['border']};
    margin-bottom: 0.8rem;
}}
.brand-logo-img {{ width: 42px; height: auto; border-radius: 10px; }}
.brand-name {{ font-size: 1.15rem; font-weight: 800; color: {v['text_main']}; line-height: 1.15; }}
.brand-tagline {{ font-size: 0.62rem; color: {v['text_faint']}; letter-spacing: 1.2px; text-transform: uppercase; }}

.nav-btn-wrapper .stButton > button {{
    background: transparent !important;
    border: 1px solid transparent !important;
    color: {v['text_muted']} !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 500 !important;
    padding: 0.55rem 0.9rem !important;
    border-radius: 10px !important;
    transition: all 0.15s ease;
}}
.nav-btn-wrapper .stButton > button:hover {{
    background: rgba(99,102,241,0.12) !important;
    color: {v['text_main']} !important;
}}
.nav-btn-active .stButton > button {{
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.2)) !important;
    color: {v['text_main']} !important;
    border: 1px solid rgba(129,140,248,0.35) !important;
}}

.sidebar-metric-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 1.2rem; font-size: 0.8rem; color: {v['text_muted']};
}}
.sidebar-metric-row .val {{ color: {v['text_main']}; font-weight: 700; }}
.sidebar-metric-row .val.danger {{ color: #ef4444; }}

.hero {{
    background: linear-gradient(135deg, #1e2a5e 0%, #4338ca 55%, #6d28d9 100%);
    border-radius: 20px;
    padding: 2.8rem 2.6rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.8rem;
}}
.hero::after {{
    content: "";
    position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.10), transparent 70%);
}}
.hero-title {{ display:flex; align-items:center; gap: 14px; }}
.hero-title img {{ width: 50px; height: auto; border-radius: 12px; }}
.hero-title h1 {{ font-size: 2rem; font-weight: 800; color: white !important; margin: 0; }}
.hero p {{ color: #e0e7ff !important; font-size: 1rem; max-width: 620px; margin-top: 0.9rem; line-height: 1.6; }}

.service-card {{
    background: {v['surface']};
    border: 1px solid {v['border']};
    border-radius: 16px;
    padding: 1.3rem 1.4rem;
    height: 100%;
}}
.service-card .svc-icon {{
    width: 38px; height: 38px; border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 0.7rem;
    color: white;
}}
.service-card .svc-title {{ font-weight: 700; color: {v['text_main']}; font-size: 0.95rem; margin-bottom: 0.25rem; }}
.service-card .svc-desc {{ color: {v['text_muted']}; font-size: 0.82rem; line-height: 1.5; }}

.step-row {{ display: flex; gap: 14px; align-items: flex-start; margin-bottom: 0.9rem; }}
.step-num {{
    width: 26px; height: 26px; min-width: 26px; border-radius: 8px;
    background: rgba(99,102,241,0.18); color: #6366f1;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.8rem;
}}
.step-text {{ color: {v['step_text']}; font-size: 0.9rem; padding-top: 2px; }}
.step-text b {{ color: {v['text_main']}; }}

.result-card {{
    border-radius: 16px; padding: 1.5rem 1.8rem; margin: 1rem 0 1.3rem 0;
    display: flex; align-items: flex-start; gap: 16px;
}}
.result-card.safe {{ background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25); }}
.result-card.danger {{ background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25); }}
.result-icon-wrap {{
    width: 44px; height: 44px; min-width: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
}}
.result-icon-wrap.safe {{ background: rgba(34,197,94,0.18); color: #16a34a; }}
.result-icon-wrap.danger {{ background: rgba(239,68,68,0.18); color: #dc2626; }}
.result-title {{ font-size: 1.05rem; font-weight: 700; color: {v['text_main']}; margin-bottom: 3px; }}
.result-desc {{ color: {v['step_text']}; font-size: 0.88rem; }}
.result-url {{ color: {v['text_faint']}; font-size: 0.75rem; margin-top: 6px; word-break: break-all; }}

.article-card {{
    border-radius: 14px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
    background: {v['surface']}; border: 1px solid {v['border']};
    display: flex; gap: 12px; align-items: flex-start;
}}
.article-card .art-icon {{ color: #6366f1; margin-top: 2px; }}
.article-card .art-title {{ font-weight: 700; color: {v['text_main']}; font-size: 0.9rem; }}
.article-card .art-desc {{ color: {v['text_muted']}; font-size: 0.8rem; margin-top: 2px; }}

.feat-tag {{
    display: inline-flex; align-items: center; gap: 6px;
    background: {v['surface2']}; border: 1px solid {v['border']};
    padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; color: {v['step_text']};
    margin: 3px 4px 3px 0;
}}
.feat-tag svg {{ flex-shrink: 0; }}

.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important; font-weight: 600 !important; color: white !important;
}}
.stButton > button[kind="secondary"] {{
    background: {v['surface2']} !important;
    color: {v['text_main']} !important;
    border: 1px solid {v['border']} !important;
}}

.stRadio label,
.stRadio > div > label > div,
.stCheckbox label {{ color: {v['text_main']} !important; }}

.stFileUploader, .stFileUploader * {{ color: {v['text_main']} !important; }}
section[data-testid="stFileUploadDropzone"] {{
    background-color: {v['input_bg']} !important;
    border: 1px dashed {v['input_border']} !important;
    border-radius: 10px !important;
}}
section[data-testid="stFileUploadDropzone"] svg {{ fill: {v['text_muted']} !important; }}

.stDataFrame {{ border-radius: 12px !important; overflow: hidden; }}
.stDataFrame, .stDataFrame * {{ color: {v['text_main']} !important; }}

::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-thumb {{ background: #6366f1; border-radius: 4px; }}

@keyframes slideInUp {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes pulseGlow {{
    0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5); }}
    70% {{ box-shadow: 0 0 0 22px rgba(34, 197, 94, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
}}
@keyframes checkmark {{
    0% {{ transform: scale(0) rotate(-45deg); }}
    50% {{ transform: scale(1.25) rotate(10deg); }}
    100% {{ transform: scale(1) rotate(0deg); }}
}}
@keyframes barGrow {{
    from {{ width: 0; opacity: 0; }}
    to {{ opacity: 1; }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}
.email-success-animation {{ animation: slideInUp 0.6s ease-out, pulseGlow 1.5s ease-in-out; }}
.checkmark-animation {{ animation: checkmark 0.6s ease-out; }}
.fade-in {{ animation: fadeIn 0.5s ease-out; }}

.grafana-panel {{
    background: {'rgba(20, 22, 30, 0.95)' if theme == 'dark' else '#ffffff'};
    border: 1px solid {'rgba(255,255,255,0.08)' if theme == 'dark' else '#e2e8f0'};
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    {'box-shadow: 0 1px 3px rgba(0,0,0,0.06);' if theme == 'light' else ''}
}}
.grafana-title {{
    font-size: 0.72rem;
    color: {v['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 700;
    margin-bottom: 0.9rem;
    border-bottom: 1px solid {v['border']};
    padding-bottom: 0.55rem;
}}
.grafana-row {{
    display: grid;
    grid-template-columns: 190px 1fr 100px 110px;
    align-items: center;
    gap: 1rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid {v['border']};
}}
.grafana-row:last-child {{ border-bottom: none; }}
.grafana-label {{ font-size: 0.85rem; font-weight: 500; color: {v['text_main']}; }}
.grafana-bar-container {{
    background: {'rgba(255,255,255,0.05)' if theme == 'dark' else '#f1f5f9'};
    border-radius: 4px;
    height: 9px;
    overflow: hidden;
}}
.grafana-bar {{
    height: 100%;
    border-radius: 4px;
    animation: barGrow 0.9s ease-out;
}}
.grafana-value {{
    font-size: 0.95rem;
    font-weight: 700;
    font-family: 'Courier New', monospace;
    text-align: right;
}}
.grafana-status {{
    font-size: 0.65rem;
    font-weight: 700;
    text-align: center;
    padding: 4px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
</style>
"""

st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ======================
# JS : Force le texte des selectbox + masque l'UI Cloud
# ======================
st.markdown("""
<script>
function forceSelectboxText() {
    const isLight = document.querySelector('.stApp') && 
                    getComputedStyle(document.body).backgroundColor.includes('255');
    const textColor = isLight ? '#0f172a' : '#ffffff';
    
    document.querySelectorAll('.stSelectbox [data-baseweb="select"] *').forEach(el => {
        if (el.children.length === 0 && el.textContent.trim().length > 0) {
            el.style.setProperty('color', textColor, 'important');
            el.style.setProperty('-webkit-text-fill-color', textColor, 'important');
            el.style.setProperty('opacity', '1', 'important');
            el.style.setProperty('font-weight', '600', 'important');
        }
    });
    document.querySelectorAll('.stSelectbox [data-baseweb="select"] svg').forEach(el => {
        el.style.setProperty('fill', '#8b5cf6', 'important');
        el.style.setProperty('stroke', '#8b5cf6', 'important');
    });
}
forceSelectboxText();
setInterval(forceSelectboxText, 300);

function killStreamlitCloudUI() {
    const selectors = [
        '[data-testid="stAppDeployButton"]',
        '[data-testid="stManageAppButton"]',
        '[data-testid="stToolbar"]',
        '[data-testid="stToolbarActions"]',
        '.stAppDeployButton',
        '.stDeployButton',
        '.viewerBadge_container__1QSob',
        '.viewerBadge_link__1S137',
        'iframe[title="streamlit_app_manage_button"]'
    ];
    selectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            el.style.display = 'none';
        });
    });
}
killStreamlitCloudUI();
setInterval(killStreamlitCloudUI, 500);
</script>
""", unsafe_allow_html=True)


def svg_tag(name, size=18, color="currentColor"):
    return icon(name, size=size, color=color)


def page_title(icon_name, texte, size=22):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:0.2rem 0 1rem 0;">'
        f'<span style="color:#a5b4fc;display:flex;">{svg_tag(icon_name, size=size)}</span>'
        f'<h3 style="margin:0;">{texte}</h3>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ======================
# CHARGEMENT DU MODÈLE
# ======================
@st.cache_resource
def charger_modele():
    try:
        model = joblib.load("modeles/best_model.pkl")
        scaler = joblib.load("modeles/scaler.pkl")
        return model, scaler
    except Exception:
        return None, None

model, scaler = charger_modele()


def analyser_url(url):
    if model is None or scaler is None:
        return None
    features = extract_features(url)
    if features is None:
        return None
    try:
        if est_domaine_fiable(url):
            return {"prediction": 0, "score": 0.0, "probabilite": 0.0,
                    "features": features, "whitelist": True}
        df_feat = pd.DataFrame([features])[FEATURE_COLUMNS]
        X_scaled = scaler.transform(df_feat)
        proba = model.predict_proba(X_scaled)[0]
        prediction = int(model.predict(X_scaled)[0])
        probabilite = float(proba[1] * 100)
        return {"prediction": prediction, "score": round(probabilite / 20, 1),
                "probabilite": probabilite, "features": features, "whitelist": False}
    except Exception:
        return None


# ============================================================
# GÉNÉRATION PDF PROFESSIONNEL
# ============================================================
def generer_pdf_rapport(url, est_mal, proba, date_str, features=None, niveau=""):
    class PDF(FPDF):
        def header(self):
            self.set_fill_color(30, 42, 94)
            self.rect(0, 0, 210, 25, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 16)
            self.set_xy(10, 6)
            self.cell(0, 8, "LoupeURL - Rapport d'analyse", ln=True)
            self.set_font("Helvetica", "", 9)
            self.set_xy(10, 15)
            self.set_text_color(200, 210, 240)
            self.cell(0, 5, "Detection intelligente des URL malveillantes", ln=True)
            self.ln(12)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"LoupeURL 2026 - Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 42, 94)
    pdf.cell(0, 8, "1. INFORMATIONS GENERALES", ln=True)
    pdf.set_draw_color(30, 42, 94)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(40, 7, "Date d'analyse :")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, date_str, ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 7, "URL analysee :", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 42, 94)
    url_courte = url if len(url) <= 90 else url[:87] + "..."
    pdf.set_x(10)
    pdf.multi_cell(190, 6, url_courte)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 42, 94)
    pdf.cell(0, 8, "2. VERDICT", ln=True)
    pdf.set_draw_color(30, 42, 94)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    if est_mal:
        bg = (254, 226, 226)
        border = (220, 38, 38)
        text_color = (153, 27, 27)
        verdict_txt = "URL MALVEILLANTE"
        sous_titre = "Cette URL presente des caracteristiques de phishing / malware."
    else:
        bg = (220, 252, 231)
        border = (22, 163, 74)
        text_color = (20, 83, 45)
        verdict_txt = "URL LEGITIME"
        sous_titre = "Aucune menace detectee. L'URL semble sure."

    y_start = pdf.get_y()
    pdf.set_fill_color(*bg)
    pdf.set_draw_color(*border)
    pdf.set_line_width(0.8)
    pdf.rect(10, y_start, 190, 22, 'DF')
    pdf.set_line_width(0.2)

    pdf.set_xy(14, y_start + 3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*text_color)
    pdf.cell(0, 8, verdict_txt, ln=True)
    pdf.set_xy(14, y_start + 11)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, sous_titre, ln=True)

    pdf.set_y(y_start + 26)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(60, 7, "Probabilite malveillante :")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*text_color)
    pdf.cell(0, 7, f"{proba:.1f}%", ln=True)

    if niveau:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(60, 7, "Niveau de risque :")
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*text_color)
        pdf.cell(0, 7, niveau, ln=True)

    pdf.ln(6)

    if features:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 42, 94)
        pdf.cell(0, 8, "3. INDICATEURS DETAILLES", ln=True)
        pdf.set_draw_color(30, 42, 94)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(30, 42, 94)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(70, 8, "Indicateur", border=1, align="C", fill=True)
        pdf.cell(40, 8, "Valeur", border=1, align="C", fill=True)
        pdf.cell(40, 8, "Seuil", border=1, align="C", fill=True)
        pdf.cell(40, 8, "Statut", border=1, align="C", fill=True, ln=True)

        indicateurs = [
            ("Adresse IP", features.get('has_ip', 0), 1,
             "Detectee" if features.get('has_ip', 0) == 1 else "Aucune",
             features.get('has_ip', 0) == 1),
            ("Sous-domaines", features.get('num_subdomains', 0), 2,
             str(features.get('num_subdomains', 0)),
             features.get('num_subdomains', 0) >= 2),
            ("Longueur URL", features.get('url_length', 0), 60,
             f"{features.get('url_length', 0)} car.",
             features.get('url_length', 0) >= 60),
            ("Mots suspects", features.get('suspicious_words', 0), 1,
             str(features.get('suspicious_words', 0)),
             features.get('suspicious_words', 0) >= 1),
            ("Port non standard", features.get('has_port', 0), 1,
             "Oui" if features.get('has_port', 0) == 1 else "Non",
             features.get('has_port', 0) == 1),
            ("Caracteres speciaux", features.get('num_special_chars', 0), 3,
             str(features.get('num_special_chars', 0)),
             features.get('num_special_chars', 0) >= 3),
        ]

        for nom, valeur, seuil, valeur_affichee, est_mauvais in indicateurs:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(50, 50, 50)
            pdf.set_fill_color(248, 250, 252)
            pdf.cell(70, 7, f"  {nom}", border=1, fill=True)
            pdf.cell(40, 7, valeur_affichee, border=1, align="C")
            pdf.cell(40, 7, str(seuil), border=1, align="C")

            if est_mauvais:
                pdf.set_text_color(220, 38, 38)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(254, 226, 226)
                pdf.cell(40, 7, "MALVEILLANT", border=1, align="C", fill=True)
            else:
                pdf.set_text_color(22, 163, 74)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_fill_color(220, 252, 231)
                pdf.cell(40, 7, "LEGITIME", border=1, align="C", fill=True)
            pdf.ln()

        pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 42, 94)
    pdf.cell(0, 8, "4. RECOMMANDATIONS", ln=True)
    pdf.set_draw_color(30, 42, 94)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)

    if est_mal:
        recs = [
            "Ne cliquez PAS sur cette URL.",
            "Ne saisissez aucune information personnelle.",
            "Ne transferez pas ce lien a vos contacts.",
            "Signalez cette URL aux autorites competentes.",
            "En cas de doute, contactez l'organisme via son site officiel.",
        ]
    else:
        recs = [
            "Cette URL semble sure, mais restez vigilant.",
            "Verifiez toujours le nom de domaine.",
            "Utilisez un gestionnaire de mots de passe.",
        ]

    for i, rec in enumerate(recs, 1):
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(99, 102, 241)
        pdf.cell(6, 6, f"{i}.")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(184, 6, rec)
        pdf.ln(1)

    pdf.ln(6)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.set_x(10)
    pdf.multi_cell(190, 5,
        "Ce rapport a ete genere automatiquement par LoupeURL. "
        "Les resultats sont indicatifs et ne remplacent pas une analyse approfondie.")

    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin-1', errors='ignore')
    return bytes(output)


def appeler_api_articles():
    try:
        r = requests.get(f"{MAIL_API_URL}/api/articles", timeout=60)
        if r.status_code == 200:
            return r.json().get("articles", [])
    except requests.exceptions.RequestException:
        pass
    return None


def envoyer_sensibilisation(destinataires, article_id):
    try:
        r = requests.post(
            f"{MAIL_API_URL}/api/send-sensibilisation",
            json={"recipients": destinataires, "articleId": article_id},
            timeout=60
        )
        return r.status_code, r.json()
    except requests.exceptions.RequestException as e:
        return None, {"error": str(e)}


def envoyer_alerte(destinataires, url, probabilite, niveau):
    try:
        r = requests.post(
            f"{MAIL_API_URL}/api/send-alert",
            json={"recipients": destinataires, "url": url,
                  "probabilite": round(probabilite), "niveau": niveau},
            timeout=60
        )
        return r.status_code, r.json()
    except requests.exceptions.RequestException as e:
        return None, {"error": str(e)}


# ======================
# TABLEAU GRAFANA
# ======================
def afficher_tableau_grafana(features, est_mal):
    st.markdown("##### Tableau de bord - Analyse detaillee")

    caracteristiques = [
        {"nom": "Adresse IP", "valeur": features.get('has_ip', 0), "seuil": 1,
         "format": lambda v: "Detectee" if v == 1 else "Aucune",
         "malveillant_si": lambda v: v == 1},
        {"nom": "Sous-domaines", "valeur": features.get('num_subdomains', 0), "seuil": 2,
         "format": lambda v: str(v), "malveillant_si": lambda v: v >= 2},
        {"nom": "Longueur URL", "valeur": features.get('url_length', 0), "seuil": 60,
         "format": lambda v: f"{v} car.", "malveillant_si": lambda v: v >= 60},
        {"nom": "Mots suspects", "valeur": features.get('suspicious_words', 0), "seuil": 1,
         "format": lambda v: str(v), "malveillant_si": lambda v: v >= 1},
        {"nom": "Port non standard", "valeur": features.get('has_port', 0), "seuil": 1,
         "format": lambda v: "Oui" if v == 1 else "Non", "malveillant_si": lambda v: v == 1},
        {"nom": "Caracteres speciaux", "valeur": features.get('num_special_chars', 0), "seuil": 3,
         "format": lambda v: str(v), "malveillant_si": lambda v: v >= 3},
    ]

    lignes = ""
    for c in caracteristiques:
        est_mauvais = c["malveillant_si"](c["valeur"])
        if est_mauvais:
            pct = min(100, int((c["valeur"] / c["seuil"]) * 50 + 50)) if c["seuil"] > 0 else 100
            couleur, statut, bg = "#ef4444", "MALVEILLANT", "rgba(239, 68, 68, 0.18)"
        else:
            pct = max(0, int((c["valeur"] / c["seuil"]) * 50)) if c["seuil"] > 0 else 0
            couleur, statut, bg = "#22c55e", "LEGITIME", "rgba(34, 197, 94, 0.18)"

        lignes += (
            f'<div class="grafana-row">'
            f'<div class="grafana-label">{c["nom"]}</div>'
            f'<div class="grafana-bar-container">'
            f'<div class="grafana-bar" style="width: {pct}%; background: linear-gradient(90deg, {couleur}66, {couleur});"></div>'
            f'</div>'
            f'<div class="grafana-value" style="color: {couleur};">{c["format"](c["valeur"])}</div>'
            f'<div class="grafana-status" style="background: {bg}; color: {couleur};">{statut}</div>'
            f'</div>'
        )

    verdict_bg = "rgba(239, 68, 68, 0.15)" if est_mal else "rgba(34, 197, 94, 0.15)"
    verdict_color = "#ef4444" if est_mal else "#22c55e"
    verdict_texte = "URL MALVEILLANTE DETECTEE" if est_mal else "URL LEGITIME"

    html = (
        f'<div class="grafana-panel fade-in">'
        f'<div class="grafana-title">INDICATEURS DE MALVEILLANCE</div>'
        f'{lignes}'
        f'</div>'
        f'<div style="background: {verdict_bg}; border: 1px solid {verdict_color}; border-radius: 8px; padding: 1rem; text-align: center; margin-top: 0.8rem;">'
        f'<div style="color: {verdict_color}; font-weight: 800; font-size: 1.05rem; letter-spacing: 1px;">{verdict_texte}</div>'
        f'</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


# ======================
# SIDEBAR
# ======================
with st.sidebar:
    logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" class="brand-logo-img">' if LOGO_B64 else ""
    st.markdown(f"""
    <div class="brand-block">
        {logo_html}
        <div>
            <div class="brand-name">LoupeURL</div>
            <div class="brand-tagline">Detection intelligente</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("home", "Accueil"),
        ("search", "Analyse"),
        ("folder", "Analyse par lot"),
        ("history", "Historique"),
        ("megaphone", "Sensibilisation"),
    ]
    for icon_name, label in nav_items:
        is_active = st.session_state.page == label
        wrapper_class = "nav-btn-active" if is_active else "nav-btn-wrapper"
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.06);margin:0.8rem 0;"></div>', unsafe_allow_html=True)

    total_analyses = len(st.session_state.historique)
    total_menaces = sum(1 for h in st.session_state.historique if h.get("prediction", 0) == 1)
    st.markdown(f"""
    <div class="sidebar-metric-row"><span>URL analysees</span><span class="val">{total_analyses}</span></div>
    <div class="sidebar-metric-row"><span>Menaces detectees</span><span class="val danger">{total_menaces}</span></div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid rgba(120,120,150,0.15);margin:0.8rem 0;"></div>', unsafe_allow_html=True)

    theme_label = "Theme sombre" if st.session_state.theme == "light" else "Theme clair"
    st.markdown('<div class="nav-btn-wrapper">', unsafe_allow_html=True)
    if st.button(theme_label, key="toggle_theme", use_container_width=True):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="position:fixed;bottom:14px;left:18px;font-size:0.65rem;color:#64748b;">v2.0 - 2026 LoupeURL</div>', unsafe_allow_html=True)

page = st.session_state.page

# ============================================================
# PAGE : ACCUEIL
# ============================================================
if page == "Accueil":
    logo_hero = f'<img src="data:image/png;base64,{LOGO_B64}">' if LOGO_B64 else ""
    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">{logo_hero}<h1>LoupeURL</h1></div>
        <p>LoupeURL est une solution intelligente de detection des URL malveillantes,
        fondee sur le Machine Learning. Elle analyse en temps reel la structure d'une
        adresse web pour identifier les tentatives de phishing, de diffusion de logiciels
        malveillants ou de fraude en ligne - avant meme que vous ne cliquiez.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Nos services")
    services = [
        ("search", "Analyse unitaire", "Verifiez instantanement si une URL est sure ou suspecte."),
        ("folder", "Analyse par lot", "Analysez un fichier entier de liens en une seule operation."),
        ("history", "Historique", "Retrouvez l'ensemble de vos analyses passees et leurs verdicts."),
        ("megaphone", "Sensibilisation", "Formez vos equipes aux risques du phishing et des ransomwares."),
    ]
    cols = st.columns(4)
    for col, (icon_name, titre, desc) in zip(cols, services):
        with col:
            st.markdown(f"""
            <div class="service-card">
                <div class="svc-icon">{svg_tag(icon_name, size=19, color="white")}</div>
                <div class="svc-title">{titre}</div>
                <div class="svc-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Comment ca marche ?")
    etapes = [
        "Vous soumettez une URL (ou un fichier de plusieurs URL)",
        "LoupeURL extrait ses caracteristiques (longueur, sous-domaines, mots suspects, adresse IP...)",
        "Un modele de Machine Learning (Random Forest) evalue la probabilite de malveillance",
        "Vous obtenez un verdict clair, avec le detail des indicateurs ayant motive la decision",
    ]
    for i, texte in enumerate(etapes, 1):
        st.markdown(f"""
        <div class="step-row">
            <div class="step-num">{i}</div>
            <div class="step-text">{texte}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Utilisez le menu a gauche pour commencer une analyse ou lancer une campagne de sensibilisation.")

# ============================================================
# PAGE : ANALYSE
# ============================================================
elif page == "Analyse":
    page_title("search", "Analyse d'une URL")

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        url = st.text_input("URL", placeholder="https://exemple.com", label_visibility="collapsed", key="input_url")
    with col_btn:
        analyser = st.button("Analyser", use_container_width=True, type="primary")

    if analyser and url:
        with st.spinner("Analyse en cours..."):
            resultat = analyser_url(url)

        if resultat is None:
            st.error("URL invalide ou modele non charge")
            st.session_state.pop("dernier_resultat", None)
        else:
            st.session_state.dernier_resultat = resultat
            st.session_state.derniere_url = url
            st.session_state.historique.insert(0, {
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "url": url,
                "prediction": resultat["prediction"],
                "probabilite": resultat["probabilite"],
                "score": resultat["score"],
            })

    if "dernier_resultat" in st.session_state:
        resultat = st.session_state.dernier_resultat
        url_affichee = st.session_state.derniere_url

        est_malveillant = resultat["prediction"] == 1
        proba = resultat["probabilite"]

        if resultat.get("whitelist") or not est_malveillant:
            desc = "Domaine reconnu (whitelist)" if resultat.get("whitelist") else f"Probabilite malveillante : {proba:.0f}%"
            st.markdown(f"""
            <div class="result-card safe">
                <div class="result-icon-wrap safe">{svg_tag('check-circle', 22)}</div>
                <div>
                    <div class="result-title">URL sure</div>
                    <div class="result-desc">{desc}</div>
                    <div class="result-url">{url_affichee}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            niveau = "ELEVE" if proba > 80 else "MOYEN"
            st.markdown(f"""
            <div class="result-card danger">
                <div class="result-icon-wrap danger">{svg_tag('alert-triangle', 22)}</div>
                <div>
                    <div class="result-title">URL suspecte detectee</div>
                    <div class="result-desc">Probabilite malveillante : <b>{proba:.0f}%</b> - Niveau : <b>{niveau}</b></div>
                    <div class="result-url">{url_affichee}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        afficher_tableau_grafana(resultat.get("features", {}), est_malveillant)

        if est_malveillant:
            st.markdown("---")
            st.markdown("##### Actions d'urgence")
            st.warning("NE CLIQUEZ PAS sur ce lien. Envoyez une alerte a vos proches ou telechargez le rapport.")

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("**Envoyer une alerte**")
                emails_alerte_raw = st.text_area(
                    "Destinataires (un email par ligne)",
                    height=110,
                    placeholder="ami@email.com\nfamille@email.com",
                    key="emails_alerte_urgence",
                    label_visibility="collapsed"
                )

                if st.button("Envoyer l'alerte maintenant", type="primary", use_container_width=True, key="btn_alerte"):
                    if not emails_alerte_raw.strip():
                        st.warning("Ajoutez au moins une adresse email.")
                    else:
                        destinataires = [e.strip() for e in emails_alerte_raw.split("\n") if e.strip()]
                        emails_invalides = [e for e in destinataires if "@" not in e]
                        if emails_invalides:
                            st.error(f"Adresses invalides : {', '.join(emails_invalides)}")
                        else:
                            with st.spinner("Envoi en cours..."):
                                total_envoyes = 0
                                total_echecs = 0
                                erreurs = []

                                for i in range(0, len(destinataires), 3):
                                    lot = destinataires[i:i + 3]
                                    statut_code, reponse = envoyer_alerte(lot, url_affichee, proba, niveau)
                                    if statut_code == 200:
                                        details = reponse.get("details", [])
                                        envoyes = sum(1 for d in details if d.get("statut") == "envoye")
                                        echecs = sum(1 for d in details if d.get("statut") == "echec")
                                        total_envoyes += envoyes
                                        total_echecs += echecs
                                    else:
                                        total_echecs += len(lot)
                                        erreurs.append(reponse.get("error", "inconnue"))

                            if total_echecs == 0:
                                st.markdown(f"""
                                <div class="email-success-animation" style="background: rgba(34, 197, 94, 0.12); border: 2px solid #22c55e; border-radius: 16px; padding: 2.5rem; text-align: center; margin: 1.5rem 0;">
                                    <div class="checkmark-animation" style="font-size: 4.5rem; margin-bottom: 1rem; color: #22c55e;">&#10003;</div>
                                    <h2 style="color: #22c55e; margin: 0 0 0.5rem 0; font-size: 1.6rem; font-weight: 800;">Alerte envoyee avec succes</h2>
                                    <p style="color: #94a3b8; margin: 0;">Le message a ete delivre a <strong style="color:#22c55e;">{total_envoyes}</strong> destinataire(s).</p>
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                            else:
                                st.warning(f"Envoi partiel : {total_envoyes} succes, {total_echecs} echec(s). Erreur : {erreurs[0] if erreurs else 'inconnue'}")

            with col_b:
                st.markdown("**Rapport d'analyse**")
                pdf_bytes = generer_pdf_rapport(
                    url_affichee,
                    est_malveillant,
                    proba,
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    features=resultat.get("features", {}),
                    niveau=niveau if est_malveillant else ""
                )
                st.download_button(
                    "Telecharger le rapport PDF",
                    data=pdf_bytes,
                    file_name=f"rapport_LoupeURL_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        features = resultat.get("features", {})
        st.markdown("##### Caracteristiques detectees")
        tags = [
            ("target", "Mots suspects", features.get("suspicious_words", 0)),
            ("shield-alert", "Adresse IP", "Oui" if features.get("has_ip", 0) == 1 else "Non"),
            ("layers", "Sous-domaines", features.get("num_subdomains", 0)),
            ("link", "Longueur", f"{features.get('url_length', 0)} car."),
        ]
        tags_html = "".join(
            f'<span class="feat-tag">{svg_tag(n, 14)} {l} : {v}</span>' for n, l, v in tags
        )
        st.markdown(tags_html, unsafe_allow_html=True)

# ============================================================
# PAGE : ANALYSE PAR LOT
# ============================================================
elif page == "Analyse par lot":
    page_title("folder", "Analyse par lot")
    st.info("Televersez un fichier CSV contenant une colonne **url**")
    fichier = st.file_uploader("Fichier CSV", type=["csv"], label_visibility="collapsed")
    if fichier:
        df = pd.read_csv(fichier)
        if "url" not in df.columns:
            st.error("Colonne 'url' manquante")
        else:
            st.write(f"**{len(df)}** URLs detectees")
            if st.button("Lancer l'analyse", type="primary"):
                resultats = []
                progress = st.progress(0)
                for i, row in df.iterrows():
                    res = analyser_url(str(row["url"]))
                    if res:
                        resultats.append({
                            "url": row["url"],
                            "verdict": "Suspecte" if res["prediction"] == 1 else "Sure",
                            "probabilite": f"{res['probabilite']:.0f}%",
                        })
                        st.session_state.historique.insert(0, {
                            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "url": row["url"], "prediction": res["prediction"],
                            "probabilite": res["probabilite"], "score": res["score"],
                        })
                    progress.progress((i + 1) / len(df))
                progress.empty()
                df_res = pd.DataFrame(resultats)
                st.success(f"{len(df_res)} URLs traitees")
                st.dataframe(df_res, use_container_width=True)

# ============================================================
# PAGE : HISTORIQUE
# ============================================================
elif page == "Historique":
    page_title("history", "Historique des analyses")
    if not st.session_state.historique:
        st.info("Aucune analyse enregistree")
    else:
        df_hist = pd.DataFrame(st.session_state.historique)
        df_hist["Resultat"] = df_hist["prediction"].apply(lambda x: "Suspecte" if x == 1 else "Sure")
        st.dataframe(df_hist[["date", "url", "Resultat", "probabilite", "score"]], use_container_width=True)
        if st.button("Vider l'historique"):
            st.session_state.historique = []
            st.rerun()

# ============================================================
# PAGE : SENSIBILISATION
# ============================================================
elif page == "Sensibilisation":
    page_title("megaphone", "Campagne de sensibilisation")
    st.markdown(
        "Envoyez un article educatif sur la cybersecurite a un ou plusieurs destinataires. "
        "L'email est envoye **au nom de LoupeURL**, jamais en votre nom personnel."
    )

    articles = appeler_api_articles()

    if articles is None:
        st.error("Impossible de contacter l'API d'envoi d'emails.")
    else:
        st.markdown("##### 1. Choisissez un article")
        for art in articles:
            st.markdown(f"""
            <div class="article-card">
                <div class="art-icon">{svg_tag('mail', 18)}</div>
                <div>
                    <div class="art-title">{art['titre']}</div>
                    <div class="art-desc">{art['resume']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        options = {a["titre"]: a["id"] for a in articles}
        choix_titre = st.selectbox("Article a envoyer", list(options.keys()))
        article_id = options[choix_titre]

        st.markdown("##### 2. Destinataires")
        mode = st.radio("Mode de saisie", ["Saisie manuelle", "Fichier CSV"], horizontal=True)
        destinataires = []
        if mode == "Saisie manuelle":
            emails_raw = st.text_area("Emails (un par ligne)", height=110)
            if emails_raw:
                destinataires = [e.strip() for e in emails_raw.split("\n") if e.strip()]
        else:
            f = st.file_uploader("CSV avec colonne 'email'", type=["csv"])
            if f:
                df = pd.read_csv(f)
                if "email" in df.columns:
                    destinataires = df["email"].dropna().tolist()

        if destinataires:
            st.info(f"{len(destinataires)} destinataire(s) pret(s)")

        st.markdown("##### 3. Envoi")
        if st.button("Envoyer la campagne", type="primary", disabled=not destinataires):
            with st.spinner("Envoi en cours..."):
                total_envoyes = 0
                total_echecs = 0
                erreurs = []

                for i in range(0, len(destinataires), 3):
                    lot = destinataires[i:i + 3]
                    statut_code, reponse = envoyer_sensibilisation(lot, article_id)
                    if statut_code == 200:
                        total_envoyes += reponse.get('envoyes', 0)
                        total_echecs += reponse.get('echecs', 0)
                    else:
                        total_echecs += len(lot)
                        erreurs.append(reponse.get('error', 'inconnue'))

                if total_echecs == 0:
                    st.markdown(f"""
                    <div class="email-success-animation" style="background: rgba(34, 197, 94, 0.12); border: 2px solid #22c55e; border-radius: 16px; padding: 2.5rem; text-align: center; margin: 1.5rem 0;">
                        <div class="checkmark-animation" style="font-size: 4.5rem; margin-bottom: 1rem; color: #22c55e;">&#10003;</div>
                        <h2 style="color: #22c55e; margin: 0 0 0.5rem 0; font-size: 1.6rem; font-weight: 800;">Campagne envoyee avec succes</h2>
                        <p style="color: #94a3b8; margin: 0;">Message delivre a <strong style="color:#22c55e;">{total_envoyes}</strong> destinataire(s).</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.warning(f"Campagne partielle : {total_envoyes} succes, {total_echecs} echec(s). Erreur : {erreurs[0] if erreurs else 'inconnue'}")
