import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import os
import json
from datetime import datetime
import re

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🌿 AI Plant Doctor",
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
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 10px;
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
        border-left: 4px solid #667eea;
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
        max-height: 300px;
        overflow-y: auto;
        color: #333;
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
    
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ============================================================================
# MASTER PROMPT - ENHANCED FOR ACCURACY
# ============================================================================

MASTER_PROMPT = """
You are an expert plant pathologist with 25 years of experience in diagnosing plant diseases.
Your role is to provide accurate, detailed plant disease analysis.

CRITICAL INSTRUCTIONS:
1. ALWAYS respond with ONLY valid JSON (no markdown, no explanations)
2. If you cannot identify the plant or disease with confidence, set confidence to below 50
3. Be specific and practical in your recommendations
4. Consider ALL possibilities (fungal, bacterial, viral, pest, nutrient deficiency, environmental stress)

ANALYSIS INSTRUCTIONS:
- Look at leaf coloration, texture, spots, lesions, wilting patterns
- Check for fungal growth, powdery coating, sticky residue (pest damage)
- Identify if symptoms are uniform or localized
- Consider environmental stress (water damage, sun scald, cold injury)

RESPOND WITH THIS EXACT JSON STRUCTURE (no code blocks, no markdown):
{
  "plant_species": "Common name and Scientific name, or 'Unable to identify'",
  "disease_name": "Specific disease name or 'Healthy Plant' or 'Environmental Stress' or 'Nutrient Deficiency'",
  "scientific_name": "Scientific name of pathogen if applicable",
  "disease_type": "fungal/bacterial/viral/pest/nutrient/environmental/healthy",
  "severity": "healthy/mild/moderate/severe",
  "confidence": 85,
  "symptoms": [
    "Specific symptom 1 - what you see",
    "Specific symptom 2 - what you see",
    "Specific symptom 3 - what you see"
  ],
  "causes": [
    "Primary cause with condition",
    "Secondary possible cause",
    "Environmental factor"
  ],
  "immediate_action": [
    "Action 1 - specific and practical",
    "Action 2 - specific and practical"
  ],
  "organic_treatments": [
    "Specific treatment with dosage/frequency",
    "Alternative organic option",
    "Prevention measure"
  ],
  "chemical_treatments": [
    "Specific fungicide/pesticide name and usage",
    "Alternative chemical option"
  ],
  "prevention": [
    "Long-term prevention strategy 1",
    "Long-term prevention strategy 2",
    "Cultural practice to avoid this"
  ],
  "confidence_reason": "Why we are confident/not confident in this diagnosis",
  "image_quality": "Good/Fair/Poor - explanation",
  "recommendations_for_better_diagnosis": "What would help confirm this diagnosis"
}
"""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_type_badge_class(disease_type):
    """Return CSS class for disease type badge"""
    type_lower = disease_type.lower()
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
    severity_lower = severity.lower()
    if "healthy" in severity_lower or "none" in severity_lower:
        return "severity-healthy"
    elif "mild" in severity_lower:
        return "severity-mild"
    elif "moderate" in severity_lower:
        return "severity-moderate"
    elif "severe" in severity_lower:
        return "severity-severe"
    return "severity-moderate"

def resize_image_for_display(image, max_width=600, max_height=500):
    """Resize image while maintaining aspect ratio"""
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

def zoom_image(image, zoom_level):
    """Apply zoom to image"""
    if zoom_level == 1.0:
        return image
    
    width, height = image.size
    new_width = int(width * zoom_level)
    new_height = int(height * zoom_level)
    
    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = left + new_width
    bottom = top + new_height
    
    cropped = image.crop((left, top, right, bottom))
    return cropped.resize((width, height), Image.Resampling.LANCZOS)

def extract_json_from_response(response_text):
    """Robustly extract JSON from response, handling various formats"""
    
    # Try 1: Direct JSON parsing
    try:
        return json.loads(response_text)
    except:
        pass
    
    # Try 2: Extract from markdown code blocks
    if "```json" in response_text:
        try:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        except:
            pass
    
    # Try 3: Extract from generic code blocks
    if "```" in response_text:
        try:
            json_str = response_text.split("```")[1].split("```")[0].strip()
            if json_str.startswith("{"):
                return json.loads(json_str)
        except:
            pass
    
    # Try 4: Find JSON object in text using regex
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    # If all parsing fails, return None
    return None

def get_image_quality_tips():
    """Return tips for better image quality"""
    return """
    📸 **TIPS FOR BETTER PLANT PHOTOS:**
    
    ✅ **DO THIS:**
    • Use natural, even lighting (cloudy day is perfect)
    • Focus on ONE symptomatic leaf
    • Use plain white or neutral background
    • Get close-up of the affected area
    • Avoid shadows covering the leaf
    • Take photo from directly above the leaf
    • Show both sides of the leaf if possible
    
    ❌ **AVOID THIS:**
    • Blurry or out-of-focus images
    • Dark shadows or harsh sun glare
    • Busy, cluttered backgrounds
    • Photos of healthy leaves when diagnosing disease
    • Wide shots showing whole plant
    • Photos taken through windows
    • Low light conditions
    """

# ============================================================================
# MAIN APP
# ============================================================================

# Header Section
st.markdown("""
<div class="header-container">
    <div class="header-title">🌿 AI Plant Doctor v2</div>
    <div class="header-subtitle">Advanced Disease Detection with Debug Tools</div>
</div>
""", unsafe_allow_html=True)

# Features Section
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card">✓ Expert Diagnosis</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">✓ Debug Mode</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">✓ Model Selection</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card">✓ Better Accuracy</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Settings Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_choice = st.radio(
        "Choose AI Model",
        ["Gemini 2.5 Flash (Faster)", "Gemini 2.5 Pro (More Accurate)"],
        help="Pro is slower but more accurate for difficult diagnoses"
    )
    
    debug_mode = st.checkbox(
        "🐛 Debug Mode",
        help="Show raw AI response and error details"
    )
    
    confidence_threshold = st.slider(
        "Minimum Confidence",
        min_value=0,
        max_value=100,
        value=50,
        help="Only show results above this confidence level"
    )
    
    st.markdown("---")
    
    with st.expander("📸 Image Quality Guide"):
        st.info(get_image_quality_tips())

# Main Content
col_upload, col_info = st.columns([3, 1])

with col_upload:
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    st.subheader("📤 Upload Plant Image")
    uploaded_file = st.file_uploader(
        "Drag and drop or click to select",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_info:
    st.info("💡 **Tip:** Clear, well-lit photos with plain backgrounds give the best results!")

# Image Display and Zoom
if uploaded_file:
    image = Image.open(uploaded_file)
    original_image = image.copy()
    
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    
    col_img, col_zoom = st.columns([3, 1])
    
    with col_zoom:
        st.markdown("### 🔍 Zoom")
        zoom_level = st.slider(
            "Zoom Level",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            label_visibility="collapsed"
        )
    
    with col_img:
        st.subheader("📸 Plant Image Preview")
        display_image = original_image.copy()
        if zoom_level != 1.0:
            display_image = zoom_image(display_image, zoom_level)
        display_image = resize_image_for_display(display_image)
        
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(display_image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analyze Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        analyze_clicked = st.button(
            "🔬 Analyze Plant",
            use_container_width=True,
            key="analyze_btn"
        )
    
    # Analysis Section
    if analyze_clicked:
        with st.spinner("🔄 Analyzing plant... Please wait"):
            try:
                # Select model
                if "Flash" in model_choice:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    model_name = "Gemini 2.5 Flash"
                else:
                    model = genai.GenerativeModel('gemini-2.5-pro')
                    model_name = "Gemini 2.5 Pro"
                
                if debug_mode:
                    st.info(f"📊 Using model: {model_name}")
                
                # Generate content
                response = model.generate_content([MASTER_PROMPT, original_image])
                raw_response = response.text
                
                if debug_mode:
                    st.markdown("### 🔍 Debug Information")
                    with st.expander("Raw API Response"):
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        st.text(raw_response[:2000] + "..." if len(raw_response) > 2000 else raw_response)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Parse response
                result = extract_json_from_response(raw_response)
                
                if result is None:
                    st.error("❌ Could not parse AI response as JSON")
                    st.warning("This sometimes happens if the API response is malformed. Try again or check your image quality.")
                    if debug_mode:
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        st.text(raw_response)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Check confidence
                    confidence = result.get("confidence", 0)
                    
                    if confidence < confidence_threshold:
                        st.warning(f"⚠️ **Low Confidence ({confidence}%)**")
                        st.info(result.get("confidence_reason", "AI is not confident in this diagnosis."))
                        st.write(result.get("recommendations_for_better_diagnosis", "Please provide a clearer image."))
                    
                    # Image Quality Alert
                    image_quality = result.get("image_quality", "")
                    if "Poor" in image_quality or "Fair" in image_quality:
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.write(f"📸 **Image Quality:** {image_quality}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display Results
                    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                    
                    # Disease Header
                    disease_name = result.get("disease_name", "Unknown")
                    disease_type = result.get("disease_type", "unknown").lower()
                    severity = result.get("severity", "unknown").lower()
                    plant = result.get("plant_species", "Unknown")
                    
                    severity_class = get_severity_badge_class(severity)
                    type_class = get_type_badge_class(disease_type)
                    
                    st.markdown(f"""
                    <div class="disease-header">
                        <div class="disease-name">{disease_name}</div>
                        <div class="disease-meta">
                            <div style="margin-right: 10px;">
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
                        st.metric("Plant", plant)
                    with col2:
                        st.metric("Confidence", f"{confidence}%")
                    with col3:
                        st.metric("Severity", severity.title())
                    with col4:
                        st.metric("Analysis Time", datetime.now().strftime("%H:%M"))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Symptoms
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-title">🔍 Symptoms Observed</div>
                    """, unsafe_allow_html=True)
                    
                    for symptom in result.get("symptoms", []):
                        st.write(f"• {symptom}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Causes
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-title">⚠️ Causes</div>
                    """, unsafe_allow_html=True)
                    
                    for cause in result.get("causes", []):
                        st.write(f"• {cause}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Immediate Action
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-title">⚡ Immediate Actions</div>
                    """, unsafe_allow_html=True)
                    
                    for i, action in enumerate(result.get("immediate_action", []), 1):
                        st.write(f"{i}. {action}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Treatments - Two Columns
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown(f"""
                        <div class="info-section">
                            <div class="info-title">🌱 Organic Treatments</div>
                        """, unsafe_allow_html=True)
                        
                        for treatment in result.get("organic_treatments", []):
                            st.write(f"• {treatment}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_right:
                        st.markdown(f"""
                        <div class="info-section">
                            <div class="info-title">💊 Chemical Treatments</div>
                        """, unsafe_allow_html=True)
                        
                        for treatment in result.get("chemical_treatments", []):
                            st.write(f"• {treatment}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Prevention
                    st.markdown(f"""
                    <div class="info-section">
                        <div class="info-title">🛡️ Prevention Tips</div>
                    """, unsafe_allow_html=True)
                    
                    for tip in result.get("prevention", []):
                        st.write(f"• {tip}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Scientific Info
                    if result.get("scientific_name") and result.get("scientific_name") != "Not applicable":
                        st.markdown(f"""
                        <div class="info-section">
                            <div class="info-title">🔬 Scientific Information</div>
                            <strong>Scientific Name:</strong> <em>{result.get("scientific_name")}</em>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Action Buttons
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if st.button("📸 Analyze Another Plant", use_container_width=True):
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("🔄 Reset", use_container_width=True):
                            st.rerun()
                            
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("**What to try:**\n- Check your Gemini API key\n- Verify the image is a valid plant leaf\n- Try a clearer, better-lit image\n- Use the Gemini 2.5 Pro model for better accuracy")
                if debug_mode:
                    st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                    st.text(f"Error: {str(e)}")
                    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("---")
    st.header("ℹ️ About v2 Updates")
    
    st.write("""
    ### What's New:
    
    ✨ **Better Accuracy** - Improved prompt for more reliable diagnosis
    
    🐛 **Debug Mode** - See raw AI responses and troubleshoot issues
    
    🚀 **Model Selection** - Choose between Fast (Flash) or Accurate (Pro)
    
    🎯 **Image Quality Tips** - Built-in guidance for better photos
    
    📊 **Confidence Settings** - Filter results by confidence threshold
    """)
    
    st.markdown("---")
    st.header("❓ Why Wrong Output?")
    
    st.write("""
    **Top Reasons for Inaccurate Results:**
    
    1. 📸 **Image Quality**
       - Blurry or dark image
       - Busy background
       - Poor lighting
       - **Solution:** Use clear, well-lit photos on plain backgrounds
    
    2. 🎯 **Wrong Subject**
       - Photo shows healthy leaf, not diseased one
       - Multiple plants/leaves in frame
       - **Solution:** Focus on ONE symptomatic leaf
    
    3. 🤖 **Model Limitations**
       - Using Flash (fast but less accurate)
       - **Solution:** Switch to Pro model for difficult cases
    
    4. 🌍 **Environmental Issues**
       - Water damage, sun scald, cold injury
       - **Solution:** Describe growing conditions
    """)
    
    st.markdown("---")
    
    st.header("✅ Best Practices")
    
    with st.expander("📸 Perfect Photo Checklist"):
        st.write("""
        - [ ] Sharp, in-focus image
        - [ ] Natural, even lighting
        - [ ] Plain white/neutral background
        - [ ] Single diseased leaf (close-up)
        - [ ] Shows both top and bottom (if possible)
        - [ ] Under 20MB file size
        - [ ] JPG or PNG format
        """)
    
    with st.expander("🔧 Troubleshooting Steps"):
        st.write("""
        1. **Try a different image** - Same leaf, different angle/lighting
        2. **Use Pro model** - Better for complex diagnoses
        3. **Enable debug mode** - See what the AI actually sees
        4. **Check image quality** - Follow the photo checklist
        5. **Verify your API key** - Make sure it's valid and has quota
        """)
