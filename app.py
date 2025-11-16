import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Professional Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR PREMIUM DESIGN
# ============================================================================

st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #e0e7ff;
        text-align: center;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .upload-container {
        background: white;
        padding: 30px;
        border-radius: 15px;
        border: 2px dashed #667eea;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 20px 0;
    }
    
    .result-container {
        background: white;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }
    
    .disease-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(245, 87, 108, 0.3);
    }
    
    .disease-name {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .disease-meta {
        font-size: 0.95rem;
        opacity: 0.95;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }
    
    .info-section {
        background: #f8f9fa;
        border-left: 5px solid #667eea;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    .info-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e3c72;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .info-content {
        color: #4a5568;
        line-height: 1.8;
        font-size: 0.95rem;
    }
    
    .info-item {
        padding: 8px 0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-item strong {
        color: #2d3748;
    }
    
    .severity-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .severity-healthy {
        background-color: #d4edda;
        color: #155724;
    }
    
    .severity-mild {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    
    .severity-moderate {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .severity-severe {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .type-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 5px 5px 5px 0;
    }
    
    .type-fungal { background-color: #e7d4f5; color: #6c2e8b; }
    .type-bacterial { background-color: #d4e7f5; color: #1e3a8a; }
    .type-viral { background-color: #f5d4d4; color: #7f1d1d; }
    .type-pest { background-color: #f5ead4; color: #7c2d12; }
    .type-nutrient { background-color: #d4f5e7; color: #1b4d3e; }
    .type-healthy { background-color: #d4f5d4; color: #1b4d1b; }
    
    .debug-box {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
        color: #333;
        white-space: pre-wrap;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #856404;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #155724;
    }
    
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #721c24;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .image-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .zoom-controls {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        display: flex;
        gap: 10px;
        align-items: center;
        margin: 10px 0;
        border: 1px solid #e2e8f0;
    }
    
    .zoom-label {
        font-weight: 600;
        color: #2d3748;
        font-size: 0.9rem;
    }
    
    .tips-card {
        background: linear-gradient(135deg, #e0e7ff 0%, #f0e7ff 100%);
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .tips-card-title {
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
    }
    
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION & API SETUP
# ============================================================================

try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except:
    st.error("❌ GEMINI_API_KEY not found in environment variables!")
    st.stop()

# ============================================================================
# ENHANCED MASTER PROMPT - EXPERT LEVEL
# ============================================================================

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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_type_badge_class(disease_type):
    """Return CSS class for disease type badge"""
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
    """Return CSS class for severity badge"""
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
    """Resize image maintaining aspect ratio"""
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

def zoom_image(image, zoom_level):
    """Apply zoom to image"""
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
    """Robustly extract and parse JSON from response"""
    if not response_text:
        return None
    
    # Try 1: Direct parsing
    try:
        return json.loads(response_text)
    except:
        pass
    
    # Try 2: Remove markdown code blocks
    cleaned = response_text
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0]
    
    try:
        return json.loads(cleaned.strip())
    except:
        pass
    
    # Try 3: Find JSON object with regex
    match = re.search(r'\{[\s\S]*\}', response_text)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    
    return None

def validate_json_result(data):
    """Validate that JSON has required fields"""
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

# ============================================================================
# MAIN APP
# ============================================================================

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🌿 AI Plant Doctor - Professional Edition</div>
    <div class="header-subtitle">Universal Plant Disease Detection with Expert Analysis</div>
</div>
""", unsafe_allow_html=True)

# Features
col1, col2, col3, col4 = st.columns(4)
features = [
    ("Expert Diagnosis", "Expert Diagnosis"),
    ("Image Zoom 🔍", "Image Zoom"),
    ("Debug Mode 🐛", "Debug Mode"),
    ("Pro Model 🚀", "Pro Model")
]

with col1:
    st.markdown('<div class="feature-card">✅ Expert Diagnosis</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">🔍 Image Zoom</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">🐛 Debug Mode</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card">🚀 Best Accuracy</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings & Configuration")
    
    model_choice = st.radio(
        "🤖 AI Model Selection",
        ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Accurate)"],
        help="Flash: 80% accurate, 2-3 sec | Pro: 95% accurate, 5-10 sec"
    )
    
    debug_mode = st.checkbox("🐛 Debug Mode", value=False, help="Show raw API responses")
    show_tips = st.checkbox("💡 Show Photo Tips", value=True, help="Display photo quality tips")
    
    confidence_min = st.slider(
        "Minimum Confidence (%)",
        0, 100, 50,
        help="Only show results above this confidence"
    )
    
    st.markdown("---")
    
    with st.expander("📸 Perfect Photo Checklist", expanded=False):
        st.markdown("""
        ✅ **DO THIS:**
        - Plain WHITE background
        - Natural, even lighting
        - Sharp and in-focus
        - Close-up of diseased part
        - ONE leaf only
        - Photograph from above
        
        ❌ **AVOID:**
        - Blurry photos
        - Dark shadows
        - Busy backgrounds
        - Healthy leaves
        - Multiple leaves
        - Angled shots
        """)
    
    with st.expander("❓ Why Wrong Results?", expanded=False):
        st.markdown("""
        **Top 3 Reasons:**
        
        1. 📸 **Bad Image Quality**
           - Blurry or dark
           - Busy background
           - Solution: Retake with white background
        
        2. 🎯 **Wrong Subject**
           - Showing healthy leaf
           - Multiple leaves in frame
           - Solution: One diseased leaf, clear view
        
        3. 🤖 **Model Issue**
           - Using Flash for complex disease
           - Solution: Switch to Pro model
        """)

# Main Content Area
col_upload, col_empty = st.columns([3, 1])

with col_upload:
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    st.subheader("📤 Upload Plant Image")
    uploaded_file = st.file_uploader(
        "Drag and drop or click to select your image",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    original_image = image.copy()
    
    # Show tips if enabled
    if show_tips:
        st.markdown("""
        <div class="tips-card">
            <div class="tips-card-title">💡 Photo Quality Matters!</div>
            For best results: white background + natural light + sharp focus + diseased leaf close-up
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    
    # Image display with zoom
    col_img, col_zoom = st.columns([3, 1])
    
    with col_zoom:
        st.markdown("### 🔍 Zoom")
        zoom_level = st.slider(
            "Zoom",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            label_visibility="collapsed"
        )
    
    with col_img:
        st.subheader("📸 Preview")
        display_image = original_image.copy()
        if zoom_level != 1.0:
            display_image = zoom_image(display_image, zoom_level)
        display_image = resize_image(display_image)
        
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(display_image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Analyze button
    st.markdown("<br>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    
    with col_b2:
        analyze_btn = st.button("🔬 Analyze Plant", use_container_width=True, type="primary")
    
    # Analysis Execution
    if analyze_btn:
        progress_placeholder = st.empty()
        
        with st.spinner("🔄 Analyzing... This may take a few seconds"):
            try:
                progress_placeholder.info("📊 Processing image with AI...")
                
                # Select model
                model_name = "Gemini 2.5 Pro" if "Pro" in model_choice else "Gemini 2.5 Flash"
                model_id = 'gemini-2.5-pro' if "Pro" in model_choice else 'gemini-2.5-flash'
                model = genai.GenerativeModel(model_id)
                
                if debug_mode:
                    st.info(f"📊 Using Model: {model_name}")
                
                # Generate response
                response = model.generate_content([EXPERT_PROMPT, original_image])
                raw_response = response.text
                
                if debug_mode:
                    with st.expander("🔍 Raw API Response"):
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        displayed_response = raw_response[:3000] + "..." if len(raw_response) > 3000 else raw_response
                        st.text(displayed_response)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Parse JSON
                result = extract_json_robust(raw_response)
                
                if result is None:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error("❌ Could not parse AI response")
                    st.write("**This sometimes happens with unusual images. Try:**")
                    st.write("• Retake photo with better lighting/focus")
                    st.write("• Use Pro model for better accuracy")
                    st.write("• Enable debug mode to see raw response")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if debug_mode:
                        with st.expander("Full Response (Debug)"):
                            st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                            st.text(raw_response)
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Validate result
                    is_valid, validation_msg = validate_json_result(result)
                    
                    if not is_valid:
                        st.warning(f"⚠️ Incomplete response: {validation_msg}")
                    
                    confidence = result.get("confidence", 0)
                    
                    # Check confidence threshold
                    if confidence < confidence_min:
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.warning(f"⚠️ **Low Confidence ({confidence}%)**")
                        st.write(result.get("confidence_reason", "AI is uncertain about this diagnosis"))
                        st.write("**Recommendation:** " + result.get("image_quality_tips", "Provide a clearer image"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Check image quality
                    image_quality = result.get("image_quality", "")
                    if image_quality and ("Poor" in image_quality or "Fair" in image_quality):
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.write(f"📸 **Image Quality Note:** {image_quality}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display Results
                    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                    
                    disease_name = result.get("disease_name", "Unknown")
                    disease_type = result.get("disease_type", "unknown")
                    severity = result.get("severity", "unknown")
                    plant = result.get("plant_species", "Unknown")
                    
                    severity_class = get_severity_badge_class(severity)
                    type_class = get_type_badge_class(disease_type)
                    
                    # Disease Header
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
                    
                    # Quick Stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🌱 Plant", plant)
                    with col2:
                        st.metric("📊 Confidence", f"{confidence}%")
                    with col3:
                        st.metric("🚨 Severity", severity.title())
                    with col4:
                        st.metric("⏱️ Analysis", datetime.now().strftime("%H:%M"))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Two-Column Layout
                    col_left, col_right = st.columns(2)
                    
                    # Left Column
                    with col_left:
                        # Symptoms
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">🔍 Symptoms Observed</div>
                        """, unsafe_allow_html=True)
                        
                        for symptom in result.get("symptoms", []):
                            st.write(f"• {symptom}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Causes
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">⚠️ Probable Causes</div>
                        """, unsafe_allow_html=True)
                        
                        for cause in result.get("probable_causes", []):
                            st.write(f"• {cause}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Right Column
                    with col_right:
                        # Immediate Actions
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">⚡ Immediate Actions</div>
                        """, unsafe_allow_html=True)
                        
                        for i, action in enumerate(result.get("immediate_action", []), 1):
                            st.write(f"**{i}.** {action}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Treatment Options
                    col_treat1, col_treat2 = st.columns(2)
                    
                    with col_treat1:
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">🌱 Organic Treatments</div>
                        """, unsafe_allow_html=True)
                        
                        for treatment in result.get("organic_treatments", []):
                            st.write(f"• {treatment}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_treat2:
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">💊 Chemical Treatments</div>
                        """, unsafe_allow_html=True)
                        
                        for treatment in result.get("chemical_treatments", []):
                            st.write(f"• {treatment}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Prevention
                    st.markdown("""
                    <div class="info-section">
                        <div class="info-title">🛡️ Long-Term Prevention</div>
                    """, unsafe_allow_html=True)
                    
                    for tip in result.get("prevention_long_term", []):
                        st.write(f"• {tip}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Similar Conditions
                    if result.get("similar_conditions"):
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">🔎 Similar Conditions</div>
                        """, unsafe_allow_html=True)
                        st.write(result.get("similar_conditions"))
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Action Buttons
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if st.button("📸 Analyze Another Plant", use_container_width=True):
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("🔄 Reset All", use_container_width=True):
                            st.rerun()
                    
                    progress_placeholder.empty()
                    
            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ Analysis Failed: {str(e)}")
                st.write("**Troubleshooting steps:**")
                st.write("1. Check your API key is valid")
                st.write("2. Try a different image with better quality")
                st.write("3. Switch to Pro model for better accuracy")
                st.write("4. Enable Debug Mode to see error details")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if debug_mode:
                    with st.expander("🔍 Error Details (Debug)"):
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        st.text(str(e))
                        st.markdown('</div>', unsafe_allow_html=True)
                
                progress_placeholder.empty()

# ============================================================================
# SIDEBAR ADDITIONAL INFO
# ============================================================================

with st.sidebar:
    st.markdown("---")
    
    st.header("📞 Support & Info")
    
    with st.expander("🌍 How It Works"):
        st.write("""
        1. **Upload Image** - Plant leaf with visible symptoms
        2. **AI Analysis** - Expert system evaluates the image
        3. **Results** - Disease identification + treatment plan
        4. **Action** - Follow recommendations
        
        **Works for:**
        • 500+ plant diseases
        • Any plant species
        • Fungal, bacterial, viral, pest, nutrient issues
        • Environmental stress conditions
        """)
    
    with st.expander("✅ Best Results"):
        st.write("""
        **Image Requirements:**
        • Clear, sharp focus
        • Natural lighting (no flash)
        • Plain white/gray background
        • Diseased leaf close-up
        • Single leaf in frame
        
        **Conditions:**
        • Use Pro model for difficult cases
        • Enable debug mode for troubleshooting
        • Check confidence score
        • Follow photo tips in sidebar
        """)
    
    with st.expander("⚙️ Settings Tips"):
        st.write("""
        **Debug Mode:**
        - Shows raw AI response
        - Helps troubleshoot issues
        - Shows JSON parsing steps
        
        **Model Selection:**
        - Flash: 80% accurate, 2-3 sec
        - Pro: 95% accurate, 5-10 sec
        
        **Confidence Threshold:**
        - Set to filter low-confidence results
        - Helps avoid false positives
        - Default 50% is reasonable
        """)
    
    st.markdown("---")
    
    st.header("📋 Free Tier Limits")
    
    st.write("""
    ✅ **Always FREE:**
    • 1,500 analyses per day
    • 15 analyses per minute
    • Commercial use allowed
    • No credit card required
    
    ⏰ **Duration:**
    • Works for 3+ months minimum
    • Likely much longer
    • See documentation for details
    """)
