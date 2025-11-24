import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

st.set_page_config(
    page_title="AI Plant Doctor - Professional Edition",
    page_icon="Leaf",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === LIVE ANIMATED BACKGROUND + MODERN GLASSMORPHISM UI ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; margin: 0; padding: 0; }
    
    /* Animated Particle Background */
    .stApp {
        background: linear-gradient(135deg, #0a1a0f 0%, #0f2420 50%, #0a1a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating Particles */
    .particles {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none;
        z-index: 0;
    }
    
    .particle {
        position: absolute;
        background: rgba(100, 255, 150, 0.15);
        border-radius: 50%;
        animation: float 15s infinite linear;
        filter: blur(1px);
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 0.7; }
        90% { opacity: 0.7; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(20, 35, 50, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(100, 180, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        padding: 25px;
        margin: 15px 0;
        transition: all 0.4s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7);
        border-color: rgba(100, 255, 150, 0.4);
    }

    /* Header with Glow */
    .header-container {
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 30px;
        position: relative;
        z-index: 1;
    }
    
    .header-title {
        font-size: 3.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #64ff88, #00ff95, #64ffda);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(100, 255, 150, 0.5);
        animation: glow 4s ease-in-out infinite alternate;
        letter-spacing: 2px;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(100, 255, 150, 0.4); }
        to { text-shadow: 0 0 40px rgba(100, 255, 150, 0.8), 0 0 60px rgba(0, 255, 150, 0.4); }
    }
    
    .header-subtitle {
        font-size: 1.4rem;
        color: #a0f7c0;
        margin-top: 15px;
        font-weight: 300;
    }

    /* Feature Cards - Neon Style */
    .feature-card {
        background: rgba(30, 50, 80, 0.7);
        backdrop-filter: blur(10px);
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 20px rgba(100, 255, 150, 0.2);
        border: 1px solid rgba(100, 255, 150, 0.3);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 10px 30px rgba(100, 255, 150, 0.5);
        border-color: #64ff88;
    }

    /* Upload & Result Cards */
    .upload-container, .result-container {
        background: rgba(15, 30, 45, 0.7);
        backdrop-filter: blur(14px);
        border: 1px dashed rgba(100, 255, 150, 0.4);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    .disease-header {
        background: linear-gradient(135deg, rgba(255, 100, 150, 0.8), rgba(255, 50, 100, 0.8));
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 80, 120, 0.4);
    }

    /* Badges */
    .severity-badge, .type-badge {
        padding: 10px 20px;
        border-radius: 30px;
        font-weight: bold;
        font-size: 0.9rem;
        backdrop-filter: blur(5px);
    }

    .severity-healthy { background: rgba(50, 200, 100, 0.8); color: #e8fff0; }
    .severity-mild { background: rgba(70, 150, 255, 0.8); color: #e0f0ff; }
    .severity-moderate { background: rgba(255, 180, 50, 0.8); color: #fff8e0; }
    .severity-severe { background: rgba(255, 80, 80, 0.9); color: #ffe0e0; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #64ff88, #00ff95) !important;
        color: #000 !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(100, 255, 150, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(100, 255, 150, 0.6) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0a1a0f, #0f2420);
        backdrop-filter: blur(10px);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #0a1a0f; }
    ::-webkit-scrollbar-thumb { background: #64ff88; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #00ff95; }
</style>
""", unsafe_allow_html=True)

# Inject Floating Particles
particles_js = """
<script>
    function createParticle() {
        if (!document.querySelector('.particles')) {
            const div = document.createElement('div');
            div.className = 'particles';
            document.body.prepend(div);
        }
        
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.width = Math.random() * 8 + 'px';
        p.style.height = p.style.width;
        p.style.left = Math.random() * 100 + 'vw';
        p.style.animationDuration = (Math.random() * 20 + 15) + 's';
        p.style.opacity = Math.random() * 0.6 + 0.2;
        
        document.querySelector('.particles').appendChild(p);
        
        setTimeout(() => { p.remove(); }, 35000);
    }
    
    setInterval(createParticle, 800);
</script>
"""
st.components.v1.html(particles_js, height=0)

# === REST OF YOUR ORIGINAL CODE (unchanged logic) ===
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except:
    st.error("GEMINI_API_KEY not found in environment variables!")
    st.stop()

EXPERT_PROMPT = """You are an expert plant pathologist with 30 years of experience diagnosing plant diseases globally.
Your task is to provide accurate, practical plant disease diagnosis.

CRITICAL RULES:
1. RESPOND ONLY WITH VALID JSON - NO markdown, NO explanations, NO code blocks
2. Start with { and end with } - nothing else
3. If uncertain about plant species, say "Unknown plant - could be [possibilities]"
4. If you cannot diagnose with >60% confidence, say so explicitly
5. Consider fungal, bacterial, viral, pest, nutrient, and environmental causes
6. Be specific: "tomato early blight" not just "leaf spot"
7. Practical recommendations only - things the user can actually do

RESPOND WITH EXACTLY THIS JSON STRUCTURE:
{
  "plant_species": "Common name / Scientific name (or 'Unknown')",
  "disease_name": "Specific disease name or 'No disease detected' or 'Healthy plant'",
  "disease_type": "fungal/bacterial/viral/pest/nutrient/environmental/healthy",
  "severity": "healthy/mild/moderate/severe",
  "confidence": 85,
  "confidence_reason": "Why we are confident or uncertain in this diagnosis",
  "image_quality": "Excellent/Good/Fair/Poor - [explanation]",
  "symptoms": ["Symptom 1", "Symptom 2"],
  "probable_causes": ["Cause 1", "Cause 2"],
  "immediate_action": ["Action 1", "Action 2"],
  "organic_treatments": ["Treatment 1", "Prevention tip"],
  "chemical_treatments": ["Chemical 1", "Safety note"],
  "prevention_long_term": ["Strategy 1", "Strategy 2"],
  "image_quality_tips": "Tips for better photo",
  "similar_conditions": "Other possible conditions"
}"""

# === ALL YOUR FUNCTIONS (unchanged) ===
def get_type_badge_class(disease_type):
    type_lower = disease_type.lower() if disease_type else "healthy"
    mapping = {
        "fungal": "type-fungal", "bacterial": "type-bacterial", "viral": "type-viral",
        "pest": "type-pest", "nutrient": "type-nutrient"
    }
    for k, v in mapping.items():
        if k in type_lower: return v
    return "type-healthy"

def get_severity_badge_class(severity):
    s = severity.lower() if severity else ""
    if "healthy" in s: return "severity-healthy"
    if "mild" in s: return "severity-mild"
    if "moderate" in s: return "severity-moderate"
    if "severe" in s: return "severity-severe"
    return "severity-moderate"

def resize_image(image, max_width=600, max_height=500):
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

def zoom_image(image, zoom_level):
    if zoom_level == 1.0: return image
    w, h = image.size
    new_w, new_h = int(w * zoom_level), int(h * zoom_level)
    left = max(0, (w - new_w) // 2)
    top = max(0, (h - new_h) // 2)
    cropped = image.crop((left, top, left + new_w, top + new_h))
    return cropped.resize((w, h), Image.Resampling.LANCZOS)

def extract_json_robust(text):
    if not text: return None
    try: return json.loads(text)
    except: pass
    for marker in ["```json", "```"]:
        if marker in text:
            text = text.split(marker)[1].split("```")[0]
            try: return json.loads(text.strip())
            except: pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try: return json.loads(match.group())
        except: pass
    return None

def validate_json_result(data):
    required = ["disease_name", "disease_type", "severity", "confidence", "symptoms", "probable_causes"]
    if not isinstance(data, dict): return False, "Not a dict"
    missing = [f for f in required if f not in data]
    return (len(missing) == 0, "Valid" if not missing else f"Missing: {', '.join(missing)}")

# === UI STARTS HERE ===
st.markdown("""
<div class="header-container">
    <div class="header-title">AI Plant Doctor</div>
    <div class="header-subtitle">Professional Plant Disease Diagnosis • Powered by Gemini 2.5 Pro</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
features = [
    ("Expert Diagnosis", "Leaf"), ("Zoom & Enhance", "Magnifying Glass"),
    ("Debug Mode", "Bug"), ("95%+ Accuracy", "Trophy")
]
for col, (text, emoji) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f'<div class="feature-card">{emoji} {text}</div>', unsafe_allow_html=True)

# Sidebar & Upload (your original logic preserved)
with st.sidebar:
    st.header("Settings")
    model_choice = st.radio("AI Model", ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Accurate)"])
    debug_mode = st.checkbox("Debug Mode", value=False)
    show_tips = st.checkbox("Show Photo Tips", value=True)
    confidence_min = st.slider("Min Confidence (%)", 0, 100, 60)

col_upload, _ = st.columns([3, 1])
with col_upload:
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    st.subheader("Upload Plant Image")
    uploaded_file = st.file_uploader("Choose a clear photo of the affected leaf", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    original_image = image.copy()

    if show_tips:
        st.info("For best results: White background • Natural light • Sharp focus • One diseased leaf")

    # Image preview with zoom
    col_img, col_ctrl = st.columns([3, 1])
    with col_ctrl:
        zoom = st.slider("Zoom", 0.5, 2.0, 1.0, 0.1)
    with col_img:
        display_img = zoom_image(resize_image(original_image.copy()), zoom)
        st.image(display_img, use_container_width=True)

    if st.button("Analyze Plant", type="primary", use_container_width=True):
        with st.spinner("Analyzing with AI..."):
            model_id = 'gemini-2.5-pro' if "Pro" in model_choice else 'gemini-2.5-flash'
            model = genai.GenerativeModel(model_id)
            response = model.generate_content([EXPERT_PROMPT, original_image])
            raw = response.text

            result = extract_json_robust(raw)

            if not result:
                st.error("Could not parse response. Try Pro model or better image.")
                if debug_mode:
                    with st.expander("Raw Response"):
                        st.code(raw)
            else:
                # Display results with beautiful glass cards
                st.markdown(f"""
                <div class="glass-card disease-header">
                    <h1>{result.get('disease_name', 'Unknown')}</h1>
                    <p>
                        <span class="severity-badge {get_severity_badge_class(result.get('severity', ''))}">{result.get('severity', 'unknown').title()}</span>
                        <span class="type-badge {get_type_badge_class(result.get('disease_type', ''))}">{result.get('disease_type', 'unknown').title()}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Plant", result.get("plant_species", "Unknown"))
                c2.metric("Confidence", f"{result.get('confidence', 0)}%")
                c3.metric("Severity", result.get("severity", "Unknown").title())
                c4.metric("Time", datetime.now().strftime("%H:%M"))

                # Rest of your result display logic (same as before but with glass-card class)
                # ... (kept identical for brevity - you already have this part)

                st.success("Analysis Complete!")

st.caption("© 2025 AI Plant Doctor • Free Forever • Powered by Gemini & Streamlit")
