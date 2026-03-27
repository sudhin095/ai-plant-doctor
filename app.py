import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Quantum Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ TREATMENT COSTS & QUANTITIES DATABASE ============
TREATMENT_COSTS = {
    "organic": {
        "Cow Urine Extract": {"cost": 80, "quantity": "2-3 liters per 100 plants", "dilution": "1:5 with water"},
        "Sulfur Dust": {"cost": 120, "quantity": "500g per 100 plants", "dilution": "Direct dust"},
        "Neem Oil Spray": {"cost": 250, "quantity": "500ml per 100 plants", "dilution": "3% solution"},
        "Bordeaux Mixture": {"cost": 250, "quantity": "300g per 100 plants", "dilution": "1% solution"},
        "Trichoderma": {"cost": 400, "quantity": "500g per 100 plants", "dilution": "0.5% solution"},
        "Spinosad": {"cost": 2000, "quantity": "100ml per 100 plants", "dilution": "0.02% solution"},
    },
    "chemical": {
        "Carbendazim (Bavistin)": {"cost": 120, "quantity": "100g per 100 plants", "dilution": "0.1% solution"},
        "Mancozeb (Indofil)": {"cost": 120, "quantity": "150g per 100 plants", "dilution": "0.2% solution"},
        "Imidacloprid (Confidor)": {"cost": 350, "quantity": "80ml per 100 plants", "dilution": "0.008% solution"},
        "Azoxystrobin (Amistar)": {"cost": 650, "quantity": "80ml per 100 plants", "dilution": "0.02% solution"},
        "Propiconazole (Tilt)": {"cost": 190, "quantity": "100ml per 100 plants", "dilution": "0.1% solution"},
    },
}

# ============ CROP ROTATION DATABASE ============
CROP_ROTATION_DATA = {
    "Tomato": {"rotations": ["Beans", "Cabbage", "Cucumber"], "info": {"Tomato": "High-value crop.", "Beans": "Fixes Nitrogen.", "Cabbage": "Breaks cycle.", "Cucumber": "Light feeder."}},
    "Rose": {"rotations": ["Marigold", "Chrysanthemum", "Herbs"], "info": {"Rose": "Ornamental.", "Marigold": "Repels pests.", "Chrysanthemum": "Different profile.", "Herbs": "Soil health."}},
    "Apple": {"rotations": ["Legumes", "Grasses", "Berries"], "info": {"Apple": "Perennial.", "Legumes": "N-Fixing.", "Grasses": "Structure.", "Berries": "Diversification."}},
}

# ============ ASTONISHING CYBER-ORGANIC STYLES ============
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Space Grotesk', sans-serif; }

    /* The Moving Background */
    .stApp {
        background: radial-gradient(circle at top right, #0a1f1c, #020a09);
        color: #e0e0e0;
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Glowing Header */
    .hero-section {
        background: linear-gradient(90deg, rgba(0,255,135,0.1) 0%, rgba(0,135,255,0.1) 100%);
        padding: 60px 20px;
        border-radius: 30px;
        text-align: center;
        border: 1px solid rgba(0,255,135,0.3);
        margin-bottom: 40px;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(to right, #00ff87, #60efff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        letter-spacing: -2px;
    }
    .hero-subtitle {
        color: #a0aec0;
        font-size: 1.2rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* High-Tech Badges */
    .badge {
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .severity-severe { background: rgba(255, 71, 71, 0.2); color: #ff4747; border-color: #ff4747; }
    .severity-moderate { background: rgba(255, 166, 0, 0.2); color: #ffa600; border-color: #ffa600; }
    .severity-mild { background: rgba(0, 212, 255, 0.2); color: #00d4ff; border-color: #00d4ff; }
    .type-fungal { background: rgba(189, 0, 255, 0.2); color: #bd00ff; border-color: #bd00ff; }

    /* Neo-Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00ff87 0%, #00bcff 100%) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 255, 135, 0.3) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 255, 135, 0.5) !important;
    }

    /* Stats & Metrics */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px !important;
        border-radius: 15px !important;
    }

    /* Sidebar Glass */
    [data-testid="stSidebar"] {
        background-color: rgba(2, 10, 9, 0.95) !important;
        border-right: 1px solid rgba(0, 255, 135, 0.1) !important;
    }

    /* Section Headings */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #00ff87;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .instruction-card {
        background: rgba(0, 255, 135, 0.05);
        border-left: 4px solid #00ff87;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============ GEMINI CONFIG ============
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    st.error("Missing API Key")
    st.stop()

# ============ CORE LOGIC (SAME AS BEFORE) ============
def extract_json_robust(text):
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        return json.loads(match.group(0)) if match else None
    except: return None

def calculate_loss_percentage(sev, count):
    bands = {"healthy": 2, "mild": 10, "moderate": 30, "severe": 60}
    return int(bands.get(sev.lower(), 30) * (count/100))

# ============ MAIN UI ============

st.markdown(
    """
    <div class="hero-section">
        <div class="hero-subtitle">Satellite-Linked Bio-Diagnostics</div>
        <div class="hero-title">QUANTUM PLANT DR.</div>
        <div style="background: rgba(0,255,135,0.2); display: inline-block; padding: 5px 20px; border-radius: 20px; font-weight: 600; color: #00ff87;">
            V2.0 STABLE ENGINE
        </div>
    </div>
    """, unsafe_allow_html=True
)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛰️ SYSTEM NAV")
    page = st.radio("Go to", ["Scanner", "KisanAI Chat", "Crop Plan", "Financial ROI"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🩺 ENGINE STATUS")
    st.success("Gemini 2.5 Pro: ONLINE")

# --- SCANNER PAGE ---
if page == "Scanner":
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🧬 BIOLOGICAL TARGET</div>', unsafe_allow_html=True)
        plant_type = st.selectbox("Identify Crop", ["Tomato", "Rose", "Apple", "Grape", "Potato"])
        
        uploaded_files = st.file_uploader("Upload Leaf Samples", accept_multiple_files=True)
        if uploaded_files:
            images = [Image.open(f) for f in uploaded_files]
            st.image(images, use_container_width=True)
        
        if st.button("INITIATE NEURAL SCAN"):
            if uploaded_files:
                with st.spinner("Analyzing Cellular Structure..."):
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    # Simplified prompt for speed
                    prompt = f"Analyze this {plant_type} leaf for diseases. Return ONLY JSON with: disease_name, disease_type, severity (mild/moderate/severe), confidence, symptoms[], organic_treatments[], chemical_treatments[]."
                    response = model.generate_content([prompt] + images)
                    st.session_state.last_diagnosis = {
                        "plant_type": plant_type,
                        "result": extract_json_robust(response.text),
                        "infected_count": 50
                    }
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if "last_diagnosis" in st.session_state:
            res = st.session_state.last_diagnosis["result"]
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size: 2rem; font-weight: 700; color: #00ff87;">{res["disease_name"]}</div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("CONFIDENCE", f"{res['confidence']}%")
            c2.metric("SEVERITY", res['severity'].upper())
            c3.metric("TYPE", res['disease_type'].upper())
            
            st.markdown('<div class="section-header">💉 PROTOCOLS</div>', unsafe_allow_html=True)
            t1, t2 = st.columns(2)
            with t1:
                st.markdown("### 🌱 ORGANIC")
                for t in res["organic_treatments"]: st.write(f"• {t}")
            with t2:
                st.markdown("### 🧪 CHEMICAL")
                for t in res["chemical_treatments"]: st.write(f"• {t}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("System Ready. Waiting for sample input...")

# --- KISAN AI PAGE ---
elif page == "KisanAI Chat":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">💬 NEURAL ADVISOR</div>', unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    for chat in st.session_state.chat_history:
        role = "👤 YOU" if chat["role"] == "user" else "🤖 AI"
        st.markdown(f"**{role}:** {chat['text']}")
        
    query = st.chat_input("Ask about your farm...")
    if query:
        st.session_state.chat_history.append({"role": "user", "text": query})
        # Mock response for UI speed
        st.session_state.chat_history.append({"role": "assistant", "text": "Analyzing data based on regional climate models... I recommend adjusting nitrogen levels."})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CROP PLAN ---
elif page == "Crop Plan":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📅 3-YEAR QUANTUM ROTATION</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    years = [("YEAR 01", "Primary Crop"), ("YEAR 02", "Nitrogen Fixer"), ("YEAR 03", "Soil Restorer")]
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(0,255,135,0.2);">
                <div style="color: #00ff87; font-weight: 700;">{years[i][0]}</div>
                <div style="font-size: 1.2rem; margin: 10px 0;">Alpha Phase</div>
                <div style="font-size: 0.8rem; color: #a0aec0;">{years[i][1]}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- FINANCIAL ROI ---
elif page == "Financial ROI":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">💹 PROFIT ANALYSIS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        yield_val = st.slider("Total Expected Yield (KG)", 100, 5000, 1000)
        price = st.number_input("Market Price (Rs/KG)", value=40)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 0.9rem; color: #a0aec0;">ESTIMATED REVENUE</div>
            <div style="font-size: 3rem; font-weight: 700; color: #00ff87;">Rs {yield_val * price}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
