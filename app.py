# app.py — Cleaned + Multilingual Option 2 (UI English by default)
import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

# -------------------------
# Page config (MUST be first)
# -------------------------
st.set_page_config(
    page_title="🌿 AI Plant Doctor - Professional Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Minimal multilingual support (Option 2)
# -------------------------
# UI will remain English by default. If the user enters another language name,
# we convert it to an ISO code and use Gemini (fallback) to translate UI strings.

# Small local map for common languages to avoid API calls for common names
LANG_NAME_TO_CODE = {
    "english": "en", "hindi": "hi", "tamil": "ta", "telugu": "te",
    "kannada": "kn", "malayalam": "ml", "bengali": "bn", "marathi": "mr",
    "gujarati": "gu", "punjabi": "pa", "urdu": "ur", "odia": "or",
    "oriya": "or", "spanish": "es", "french": "fr", "german": "de",
    "arabic": "ar", "chinese": "zh", "japanese": "ja", "korean": "ko"
}

def get_lang_code_from_name(language_name):
    """Return ISO code for given language name. Check local map first, else attempt to use Gemini."""
    if not language_name:
        return "en"
    name = language_name.strip().lower()
    if name in LANG_NAME_TO_CODE:
        return LANG_NAME_TO_CODE[name]
    # fallback: call Gemini (if API key is configured), else default to 'en'
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            "Convert the following language name into its ISO 639-1 code. "
            "Only output the code, nothing else.\n\nLanguage: " + language_name
        )
        resp = model.generate_content(prompt)
        code = resp.text.strip().lower()
        # sanitize (keep only first two letters)
        if len(code) >= 2:
            return code[:2]
        return "en"
    except Exception:
        return "en"

def translate_text_via_gemini(text, target_lang_code):
    """Translate UI text using Gemini. Returns translated text or original on failure."""
    if target_lang_code == "en" or not target_lang_code:
        return text
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"Translate the following text to language code '{target_lang_code}'. Keep it short and suitable for UI labels.\n\nText:\n{text}"
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return text

def T(text):
    """Wrapper to translate UI text only when user chooses a non-English UI language."""
    lang = st.session_state.get("ui_lang", "en")
    if not lang or lang == "en":
        return text
    # We can cache translations in session_state to avoid repeated API calls
    translations = st.session_state.setdefault("_cached_translations", {})
    key = f"{lang}::" + text
    if key in translations:
        return translations[key]
    translated = translate_text_via_gemini(text, lang)
    translations[key] = translated
    return translated

# -------------------------
# Configure Gemini API (non-fatal — app can show error)
# -------------------------
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    # We do not stop here; translations will fallback to English and some features that need Gemini may fail later.
    st.warning("⚠️ GEMINI_API_KEY not found in environment variables. Translation via Gemini will be unavailable.")

# -------------------------
# Expert prompt (unchanged)
# -------------------------
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
  "symptoms": [
    "First visible symptom observed",
    "Second visible symptom observed",
    "Third visible symptom if present"
  ],
  "probable_causes": [
    "Primary cause with conditions that led to it",
    "Secondary possible cause",
    "Environmental factor if applicable"
  ],
  "immediate_action": [
    "Action 1: Specific, actionable step",
    "Action 2: Specific, actionable step",
    "Action 3: Specific, actionable step"
  ],
  "organic_treatments": [
    "Treatment 1: Specific product and application method",
    "Treatment 2: Specific product and application method",
    "Prevention: How to avoid this in future"
  ],
  "chemical_treatments": [
    "Chemical 1: Product name and dilution rate",
    "Chemical 2: Alternative if resistance develops",
    "Note: When to use and safety precautions"
  ],
  "prevention_long_term": [
    "Prevention strategy 1: Cultural practice",
    "Prevention strategy 2: Environmental control",
    "Prevention strategy 3: Variety selection or rotation"
  ],
  "image_quality_tips": "What would make diagnosis more certain",
  "similar_conditions": "Other conditions that might look similar"
}"""

# -------------------------
# Helper functions (image, json parsing)
# -------------------------
def get_type_badge_class(disease_type):
    type_lower = disease_type.lower() if disease_type else "healthy"
    if "fungal" in type_lower:
        return "type-fungal"
    elif "bacterial" in type_lower:
        return "type-bacterial"
    elif "viral" in type_lower:
        return "type-viral"
    elif "pest" in type_lower:
        return "type-pest"
    elif "nutrient" in type_lower:
        return "type-nutrient"
    else:
        return "type-healthy"

def get_severity_badge_class(severity):
    severity_lower = (severity.lower() if severity else "moderate")
    if "healthy" in severity_lower or "none" in severity_lower:
        return "severity-healthy"
    elif "mild" in severity_lower:
        return "severity-mild"
    elif "moderate" in severity_lower:
        return "severity-moderate"
    elif "severe" in severity_lower:
        return "severity-severe"
    return "severity-moderate"

def resize_image(image, max_width=600, max_height=500):
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

def zoom_image(image, zoom_level):
    if zoom_level == 1.0:
        return image
    width, height = image.size
    new_width = int(width * zoom_level)
    new_height = int(height * zoom_level)
    left = max(0, (width - new_width) / 2)
    top = max(0, (height - new_height) / 2)
    right = min(width, left + new_width)
    bottom = min(height, top + new_height)
    cropped = image.crop((left, top, right, bottom))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)

def extract_json_robust(response_text):
    if not response_text:
        return None
    # try direct parse
    try:
        return json.loads(response_text)
    except Exception:
        pass
    cleaned = response_text
    # remove triple-backtick wrappers if present
    try:
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]
    except Exception:
        pass
    try:
        return json.loads(cleaned.strip())
    except Exception:
        pass
    # fallback: extract first {...} block
    match = re.search(r'\{[\s\S]*\}', response_text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None

def validate_json_result(data):
    required_fields = [
        "disease_name", "disease_type", "severity",
        "confidence", "symptoms", "probable_causes"
    ]
    if not isinstance(data, dict):
        return False, "Response is not a dictionary"
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, "Valid"

# -------------------------
# Page styling (unchanged look)
# -------------------------
st.markdown("""
<style>
    * { margin: 0; padding: 0; }
    .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); color: #e4e6eb; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
    p, span, div, label { color: #e4e6eb; }
    .header-container { background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%); padding: 40px 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); border: 1px solid rgba(102,126,234,0.3); }
    .header-title { font-size: 2.5rem; font-weight:700; color:#ffffff; text-align:center; margin-bottom:10px; letter-spacing:1px; }
    .header-subtitle { font-size: 1.1rem; color: #b0c4ff; text-align:center; }
    .feature-card { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white; padding:15px 20px; border-radius:10px; text-align:center; font-weight:600; font-size:0.95rem; box-shadow:0 4px 15px rgba(102,126,234,0.5); transition: transform 0.3s ease; border:1px solid rgba(255,255,255,0.1); }
    .feature-card:hover { transform:translateY(-5px); box-shadow:0 6px 20px rgba(102,126,234,0.7); }
    .upload-container { background: linear-gradient(135deg,#1e2330 0%,#2a3040 100%); padding:30px; border-radius:15px; border:2px dashed #667eea; box-shadow:0 4px 20px rgba(0,0,0,0.4); margin:20px 0; }
    .result-container { background: linear-gradient(135deg,#1e2330 0%,#2a3040 100%); border-radius:15px; padding:30px; box-shadow:0 8px 32px rgba(0,0,0,0.5); margin:20px 0; border:1px solid rgba(102,126,234,0.2); }
    .disease-header { background: linear-gradient(135deg,#f093fb 0%,#f5576c 100%); color:white; padding:25px; border-radius:12px; margin-bottom:25px; box-shadow:0 4px 20px rgba(245,87,108,0.5); border:1px solid rgba(255,255,255,0.1); }
    .disease-name { font-size:2.2rem; font-weight:700; margin-bottom:15px; }
    .disease-meta { font-size:0.95rem; opacity:0.95; display:flex; gap:20px; flex-wrap:wrap; }
    .info-section { background: linear-gradient(135deg,#2a3040 0%,#353d50 100%); border-left:5px solid #667eea; padding:20px; border-radius:8px; margin:15px 0; border:1px solid rgba(102,126,234,0.2); }
    .info-title { font-size:1.2rem; font-weight:700; color:#b0c4ff; margin-bottom:12px; display:flex; align-items:center; gap:10px; }
    .info-content { color:#d0d6e6; line-height:1.8; font-size:0.95rem; }
    .severity-badge { display:inline-block; padding:8px 16px; border-radius:20px; font-weight:600; font-size:0.9rem; }
    .severity-healthy { background-color:#1b5e20; color:#4caf50; }
    .severity-mild { background-color:#004d73; color:#4dd0e1; }
    .severity-moderate { background-color:#633d00; color:#ffc107; }
    .severity-severe { background-color:#5a1a1a; color:#ff6b6b; }
    .type-badge { display:inline-block; padding:6px 12px; border-radius:15px; font-weight:600; font-size:0.85rem; margin:5px 5px 5px 0; }
    .type-fungal { background-color:#4a148c; color:#ce93d8; }
    .type-bacterial { background-color:#0d47a1; color:#64b5f6; }
    .type-viral { background-color:#5c0b0b; color:#ef9a9a; }
    .type-pest { background-color:#4d2600; color:#ffcc80; }
    .type-nutrient { background-color:#0d3a1a; color:#81c784; }
    .type-healthy { background-color:#0d3a1a; color:#81c784; }
    .debug-box { background:#0f1419; border:1px solid #667eea; border-radius:8px; padding:15px; margin:10px 0; font-family:monospace; font-size:0.85rem; max-height:400px; overflow-y:auto; color:#b0c4ff; white-space:pre-wrap; }
    .warning-box { background: linear-gradient(135deg,#4d2600 0%,#3d2000 100%); border:1px solid #ffc107; border-radius:8px; padding:15px; margin:10px 0; color:#ffcc80; }
    .success-box { background: linear-gradient(135deg,#1b5e20 0%,#0d3a1a 100%); border:1px solid #4caf50; border-radius:8px; padding:15px; margin:10px 0; color:#81c784; }
    .error-box { background: linear-gradient(135deg,#5a1a1a 0%,#3d0d0d 100%); border:1px solid #ff6b6b; border-radius:8px; padding:15px; margin:10px 0; color:#ef9a9a; }
    .stButton > button { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%) !important; color:white !important; border:1px solid rgba(255,255,255,0.2) !important; padding:12px 30px !important; font-weight:600 !important; border-radius:8px !important; box-shadow:0 4px 15px rgba(102,126,234,0.4) !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(102,126,234,0.6) !important; }
    .image-container { border-radius:12px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.5); border:1px solid rgba(102,126,234,0.2); }
    .tips-card { background: linear-gradient(135deg,#1a2a47 0%,#2d3050 100%); border:2px solid #667eea; border-radius:10px; padding:15px; margin:10px 0; }
    .tips-card-title { font-weight:700; color:#b0c4ff; margin-bottom:10px; }
    [data-testid="stSidebar"] { background: linear-gradient(135deg,#0f1419 0%,#1a1f2e 100%); }
    [data-testid="metric-container"] { background: linear-gradient(135deg,#2a3040 0%,#353d50 100%); border:1px solid rgba(102,126,234,0.2); border-radius:8px; }
    [data-testid="stExpander"] { background: linear-gradient(135deg,#2a3040 0%,#353d50 100%); border:1px solid rgba(102,126,234,0.2); }
    .streamlit-expanderHeader { color:#b0c4ff !important; }
    input, textarea, select { background: linear-gradient(135deg,#1e2330 0%,#2a3040 100%) !important; border:1px solid rgba(102,126,234,0.3) !important; color:#e4e6eb !important; }
    ::-webkit-scrollbar { width:8px; height:8px; }
    ::-webkit-scrollbar-track { background:#0f1419; }
    ::-webkit-scrollbar-thumb { background:#667eea; border-radius:4px; }
    ::-webkit-scrollbar-thumb:hover { background:#764ba2; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Header + feature cards
# -------------------------
st.markdown(f"""
<div class="header-container">
    <div class="header-title">{T('🌿 AI Plant Doctor - Professional Edition')}</div>
    <div class="header-subtitle">{T('Universal Plant Disease Detection with Expert Analysis')}</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="feature-card">{T("✅ Expert Diagnosis")}</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="feature-card">{T("🔍 Image Zoom")}</div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="feature-card">{T("🐛 Debug Mode")}</div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="feature-card">{T("🚀 Best Accuracy")}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# Sidebar: Settings & Language input (Option 2)
# -------------------------
with st.sidebar:
    st.header(T("⚙️ Settings & Configuration"))
    # Language input: user may enter any language name; default is English
    st.markdown(T("### 🌐 UI Language (Optional)"))
    user_lang_input = st.text_input(
        T("Enter any language name (e.g., Hindi, Tamil, Spanish). Leave blank for English."),
        value=""
    )
    # Determine language code and store
    lang_code = get_lang_code_from_name(user_lang_input) if user_lang_input else "en"
    st.session_state["ui_lang"] = lang_code

    model_choice = st.radio(
        T("🤖 AI Model Selection"),
        [T("Gemini 2.5 Flash (Fast)"), T("Gemini 2.5 Pro (Accurate)")],
        help=T("Flash: 80% accurate, 2-3 sec | Pro: 95% accurate, 5-10 sec")
    )
    debug_mode = st.checkbox(T("🐛 Debug Mode"), value=False, help=T("Show raw API responses"))
    show_tips = st.checkbox(T("💡 Show Photo Tips"), value=True, help=T("Display photo quality tips"))
    confidence_min = st.slider(T("Minimum Confidence (%)"), 0, 100, 50, help=T("Only show results above this confidence"))

    st.markdown("---")
    with st.expander(T("📸 Perfect Photo Checklist"), expanded=False):
        st.markdown(T("""
        ✅ DO THIS:
        - Plain WHITE background
        - Natural, even lighting
        - Sharp and in-focus
        - Close-up of diseased part
        - ONE leaf only
        - Photograph from above

        ❌ AVOID:
        - Blurry photos
        - Dark shadows
        - Busy backgrounds
        - Healthy leaves
        - Multiple leaves
        - Angled shots
        """))

    with st.expander(T("❓ Why Wrong Results?"), expanded=False):
        st.markdown(T("""
        Top 3 Reasons:

        1. Bad Image Quality - Blurry, dark, busy background.
        2. Wrong Subject - Healthy leaf or multiple leaves.
        3. Model Issue - Use Pro for complex diseases.
        """))

# -------------------------
# Upload area
# -------------------------
col_upload, col_empty = st.columns([3, 1])
with col_upload:
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    st.subheader(T("📤 Upload Plant Image"))
    uploaded_file = st.file_uploader(
        T("Drag and drop or click to select your image"),
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Analysis flow
# -------------------------
if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception:
        st.error(T("❌ Could not open the image. Try another file."))
        image = None

    if image is not None:
        original_image = image.copy()
        if show_tips:
            st.markdown(f"""
            <div class="tips-card">
                <div class="tips-card-title">{T('💡 Photo Quality Matters!')}</div>
                {T('For best results: white background + natural light + sharp focus + diseased leaf close-up')}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        col_img, col_zoom = st.columns([3, 1])
        with col_zoom:
            st.markdown(f"### {T('🔍 Zoom')}")
            zoom_level = st.slider(T("Zoom"), min_value=0.5, max_value=2.0, value=1.0, step=0.1, label_visibility="collapsed")
        with col_img:
            st.subheader(T("📸 Preview"))
            display_image = original_image.copy()
            if zoom_level != 1.0:
                display_image = zoom_image(display_image, zoom_level)
            display_image = resize_image(display_image)
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(display_image, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
        with col_b2:
            analyze_btn = st.button(T("🔬 Analyze Plant"), use_container_width=True)

        if analyze_btn:
            progress_placeholder = st.empty()
            with st.spinner(T("🔄 Analyzing... This may take a few seconds")):
                try:
                    progress_placeholder.info(T("📊 Processing image with AI..."))
                    model_name = "Gemini 2.5 Pro" if "Pro" in model_choice else "Gemini 2.5 Flash"
                    model_id = 'gemini-2.5-pro' if "Pro" in model_choice else 'gemini-2.5-flash'
                    model = genai.GenerativeModel(model_id)

                    if debug_mode:
                        st.info(f"{T('📊 Using Model:')} {model_name}")

                    # Call model - pass the prompt and image. Specifics depend on your genai usage.
                    # Keep the prompt in English (diagnosis always English).
                    response = model.generate_content([EXPERT_PROMPT, original_image])
                    raw_response = response.text if hasattr(response, "text") else str(response)

                    if debug_mode:
                        with st.expander(T("🔍 Raw API Response")):
                            st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                            displayed_response = raw_response[:3000] + "..." if len(raw_response) > 3000 else raw_response
                            st.text(displayed_response)
                            st.markdown('</div>', unsafe_allow_html=True)

                    result = extract_json_robust(raw_response)

                    if result is None:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error(T("❌ Could not parse AI response"))
                        st.write(T("This sometimes happens with unusual images. Try:"))
                        st.write(T("• Retake photo with better lighting/focus"))
                        st.write(T("• Use Pro model for better accuracy"))
                        st.write(T("• Enable debug mode to see raw response"))
                        st.markdown('</div>', unsafe_allow_html=True)
                        if debug_mode:
                            with st.expander(T("Full Response (Debug)")):
                                st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                                st.text(raw_response)
                                st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        is_valid, validation_msg = validate_json_result(result)
                        if not is_valid:
                            st.warning(T("⚠️ Incomplete response: ") + validation_msg)

                        confidence = result.get("confidence", 0)
                        if confidence < confidence_min:
                            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                            st.warning(T(f"⚠️ Low Confidence ({confidence}%)"))
                            st.write(result.get("confidence_reason", "AI is uncertain about this diagnosis"))
                            st.write("**" + T("Recommendation:") + "** " + result.get("image_quality_tips", T("Provide a clearer image")))
                            st.markdown('</div>', unsafe_allow_html=True)

                        image_quality = result.get("image_quality", "")
                        if image_quality and ("Poor" in image_quality or "Fair" in image_quality):
                            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                            st.write(T("📸 Image Quality Note: ") + image_quality)
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Present results
                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        disease_name = result.get("disease_name", "Unknown")
                        disease_type = result.get("disease_type", "unknown")
                        severity = result.get("severity", "unknown")
                        plant = result.get("plant_species", "Unknown")
                        severity_class = get_severity_badge_class(severity)
                        type_class = get_type_badge_class(disease_type)

                        st.markdown(f"""
                        <div class="disease-header">
                            <div class="disease-name">{disease_name}</div>
                            <div class="disease-meta">
                                <div>
                                    <span class="severity-badge {severity_class}">{severity.title()}</span>
                                </div>
                                <div>
                                    <span class="type-badge {type_class}">{disease_type.title()}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(T("🌱 Plant"), plant)
                        with col2:
                            st.metric(T("📊 Confidence"), f"{confidence}%")
                        with col3:
                            st.metric(T("🚨 Severity"), severity.title())
                        with col4:
                            st.metric(T("⏱️ Analysis"), datetime.now().strftime("%H:%M"))

                        st.markdown("<br>", unsafe_allow_html=True)
                        col_left, col_right = st.columns(2)
                        with col_left:
                            st.markdown(f"""
                            <div class="info-section">
                                <div class="info-title">{T("🔍 Symptoms Observed")}</div>
                            """, unsafe_allow_html=True)
                            for symptom in result.get("symptoms", []):
                                st.write(f"• {symptom}")
                            st.markdown("</div>", unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class="info-section">
                                <div class="info-title">{T("⚠️ Probable Causes")}</div>
                            """, unsafe_allow_html=True)
                            for cause in result.get("probable_causes", []):
                                st.write(f"• {cause}")
                            st.markdown("</div>", unsafe_allow_html=True)

                        with col_right:
                            st.markdown(f"""
                            <div class="info-section">
                                <div class="info-title">{T("⚡ Immediate Actions")}</div>
                            """, unsafe_allow_html=True)
                            for i, action in enumerate(result.get("immediate_action", []), 1):
                                st.write(f"**{i}.** {action}")
                            st.markdown("</div>", unsafe_allow_html=True)

                        col_treat1, col_treat2 = st.columns(2)
                        with col_treat1:
                            st.markdown(f"""
                            <div class="info-section">
                                <div class="info-title">{T("🌱 Organic Treatments")}</div>
                            """, unsafe_allow_html=True)
                            for treatment in result.get("organic_treatments", []):
                                st.write(f"• {treatment}")
                            st.markdown("</div>", unsafe_allow_html=True)

                        with col_treat2:
                            st.markdown(f"""
                            <div class="info-section">
                                <div class="info-title">{T("💊 Chemical Treatments")}</div>
                            """, unsafe_allow_html=True)
                            for treatment in result.get("chemical_treatments", []):
                                st.write(f"• {treatment}")
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="info-section">
                            <div class="info-title">{T("🛡️ Long-Term Prevention")}</div>
                        """, unsafe_allow_html=True)
                        for tip in result.get("prevention_long_term", []):
                            st.write(f"• {tip}")
                        st.markdown("</div>", unsafe_allow_html=True)

                        if result.get("similar_conditions"):
                            st.markdown(f"""
                            <div class="info-section">
                                <div class="info-title">{T("🔎 Similar Conditions")}</div>
                            """, unsafe_allow_html=True)
                            st.write(result.get("similar_conditions"))
                            st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                        with col_btn1:
                            if st.button(T("📸 Analyze Another Plant"), use_container_width=True):
                                st.rerun()
                        with col_btn3:
                            if st.button(T("🔄 Reset All"), use_container_width=True):
                                st.rerun()

                        progress_placeholder.empty()

                # end try
                except Exception as e:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error(T("❌ Analysis Failed: ") + str(e))
                    st.write(T("**Troubleshooting steps:**"))
                    st.write(T("1. Check your API key is valid"))
                    st.write(T("2. Try a different image with better quality"))
                    st.write(T("3. Switch to Pro model for better accuracy"))
                    st.write(T("4. Enable Debug Mode to see error details"))
                    st.markdown('</div>', unsafe_allow_html=True)
                    if debug_mode:
                        with st.expander(T("🔍 Error Details (Debug)")):
                            st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                            st.text(str(e))
                            st.markdown('</div>', unsafe_allow_html=True)
                    progress_placeholder.empty()

# -------------------------
# Sidebar: Support & Info
# -------------------------
with st.sidebar:
    st.markdown("---")
    st.header(T("📞 Support & Info"))
    with st.expander(T("🌍 How It Works")):
        st.write(T("""
        1. Upload Image - Plant leaf with visible symptoms
        2. AI Analysis - Expert system evaluates the image
        3. Results - Disease identification + treatment plan
        4. Action - Follow recommendations
        """))
    with st.expander(T("✅ Best Results")):
        st.write(T("""
        Image Requirements:
        • Clear, sharp focus
        • Natural lighting (no flash)
        • Plain white/gray background
        • Diseased leaf close-up
        • Single leaf in frame
        """))
    with st.expander(T("⚙️ Settings Tips")):
        st.write(T("""
        Debug Mode:
        - Shows raw AI response
        - Helps troubleshoot issues
        - Shows JSON parsing steps
        """))
    st.markdown("---")
    st.header(T("📋 Free Tier Limits"))
    st.write(T("""
    Always FREE:
    • 1,500 analyses per day
    • 15 analyses per minute
    • Commercial use allowed
    • No credit card required
    """))

# End of file
