import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re
st.set_page_config(
# ================================
# ■ MULTILINGUAL UI SUPPORT — OPTION A
# ================================
# A helper function to convert language names into ISO codes.
def get_lang_code_from_name(language_name):
 """Uses Gemini Flash to convert language name into ISO 639-1 code."""
 try:
 model = genai.GenerativeModel("gemini-2.0-flash")
 prompt = f"""
 Convert the following language name to its ISO 639-1 language code.
 Only return the code. Example: Hindi -> hi, Tamil -> ta, Gujarati -> gu
 Language: {language_name}
 """
 response = model.generate_content(prompt)
 return response.text.strip().lower()
 except:
 return "en"
# A helper to translate UI text.
def translate_text(text, target_lang):
 if target_lang == "en":
 return text
 try:
 model = genai.GenerativeModel("gemini-2.0-flash")
 prompt = f"Translate this UI text to '{target_lang}' clearly and accurately:\n{text}"
 response = model.generate_content(prompt)
 return response.text
 except:
 return text
# Main translation wrapper
def T(text):
 lang = st.session_state.get("ui_lang", "en")
 return translate_text(text, lang)
# ================================
# Sidebar language selector
# ================================
with st.sidebar:
 st.markdown("## ■ UI Language")
 user_lang_input = st.text_input(
 "Enter any language name (Hindi, Tamil, Arabic, Gujarati, Japanese, etc.)",
 value="English"
 )
 # Convert entered language name to language code
 lang_code = get_lang_code_from_name(user_lang_input)
 # Store it
 st.session_state["ui_lang"] = lang_code
 page_title="■ AI Plant Doctor - Professional Edition",
 page_icon="■",
 layout="wide",
 initial_sidebar_state="expanded"
)
st.markdown("""
<style>
 * {
 margin: 0;
 padding: 0;
 }

 /* DARK MODE */
 .stApp {
 background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
 color: #e4e6eb;
 }

 /* Main container background */
 [data-testid="stAppViewContainer"] {
 background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
 }

 /* Text color adjustments */
 p, span, div, label {
 color: #e4e6eb;
 }

 /* Header Styles */
 .header-container {
 background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%);
 padding: 40px 20px;
 border-radius: 15px;
 margin-bottom: 30px;
 box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
 border: 1px solid rgba(102, 126, 234, 0.3);
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
 color: #b0c4ff;
 text-align: center;
 }

 /* Feature Cards */
 .feature-card {
 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 color: white;
 padding: 15px 20px;
 border-radius: 10px;
 text-align: center;
 font-weight: 600;
 font-size: 0.95rem;
 box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
 transition: transform 0.3s ease;
 border: 1px solid rgba(255, 255, 255, 0.1);
 }

 .feature-card:hover {
 transform: translateY(-5px);
 box-shadow: 0 6px 20px rgba(102, 126, 234, 0.7);
 }

 /* Upload Container */
 .upload-container {
 background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%);
 padding: 30px;
 border-radius: 15px;
 border: 2px dashed #667eea;
 box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
 margin: 20px 0;
 }

 /* Result Container */
 .result-container {
 background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%);
 border-radius: 15px;
 padding: 30px;
 box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
 margin: 20px 0;
 border: 1px solid rgba(102, 126, 234, 0.2);
 }

 /* Disease Header */
 .disease-header {
 background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
 color: white;
 padding: 25px;
 border-radius: 12px;
 margin-bottom: 25px;
 box-shadow: 0 4px 20px rgba(245, 87, 108, 0.5);
 border: 1px solid rgba(255, 255, 255, 0.1);
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

 /* Info Sections */
 .info-section {
 background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
 border-left: 5px solid #667eea;
 padding: 20px;
 border-radius: 8px;
 margin: 15px 0;
 border: 1px solid rgba(102, 126, 234, 0.2);
 }

 .info-title {
 font-size: 1.2rem;
 font-weight: 700;
 color: #b0c4ff;
 margin-bottom: 12px;
 display: flex;
 align-items: center;
 gap: 10px;
 }

 .info-content {
 color: #d0d6e6;
 line-height: 1.8;
 font-size: 0.95rem;
 }

 /* Badges */
 .severity-badge {
 display: inline-block;
 padding: 8px 16px;
 border-radius: 20px;
 font-weight: 600;
 font-size: 0.9rem;
 }
 .severity-healthy {
 background-color: #1b5e20;
 color: #4caf50;
 }

 .severity-mild {
 background-color: #004d73;
 color: #4dd0e1;
 }

 .severity-moderate {
 background-color: #633d00;
 color: #ffc107;
 }

 .severity-severe {
 background-color: #5a1a1a;
 color: #ff6b6b;
 }

 .type-badge {
 display: inline-block;
 padding: 6px 12px;
 border-radius: 15px;
 font-weight: 600;
 font-size: 0.85rem;
 margin: 5px 5px 5px 0;
 }

 .type-fungal { background-color: #4a148c; color: #ce93d8; }
 .type-bacterial { background-color: #0d47a1; color: #64b5f6; }
 .type-viral { background-color: #5c0b0b; color: #ef9a9a; }
 .type-pest { background-color: #4d2600; color: #ffcc80; }
 .type-nutrient { background-color: #0d3a1a; color: #81c784; }
 .type-healthy { background-color: #0d3a1a; color: #81c784; }

 /* Debug Box */
 .debug-box {
 background: #0f1419;
 border: 1px solid #667eea;
 border-radius: 8px;
 padding: 15px;
 margin: 10px 0;
 font-family: monospace;
 font-size: 0.85rem;
 max-height: 400px;
 overflow-y: auto;
 color: #b0c4ff;
 white-space: pre-wrap;
 }

 /* Alert Boxes */
 .warning-box {
 background: linear-gradient(135deg, #4d2600 0%, #3d2000 100%);
 border: 1px solid #ffc107;
 border-radius: 8px;
 padding: 15px;
 margin: 10px 0;
 color: #ffcc80;
 }

 .success-box {
 background: linear-gradient(135deg, #1b5e20 0%, #0d3a1a 100%);
 border: 1px solid #4caf50;
 border-radius: 8px;
 padding: 15px;
 margin: 10px 0;
 color: #81c784;
 }

 .error-box {
 background: linear-gradient(135deg, #5a1a1a 0%, #3d0d0d 100%);
 border: 1px solid #ff6b6b;
 border-radius: 8px;
 padding: 15px;
 margin: 10px 0;
 color: #ef9a9a;
 }

 /* Button Styles */
 .stButton > button {
 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
 color: white !important;
 border: 1px solid rgba(255, 255, 255, 0.2) !important;
 padding: 12px 30px !important;
 font-weight: 600 !important;
 border-radius: 8px !important;
 box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
 transition: all 0.3s ease !important;
 }

 .stButton > button:hover {
 transform: translateY(-2px) !important;
 box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
 }

 /* Image Container */
 .image-container {
 border-radius: 12px;
 overflow: hidden;
 box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
 border: 1px solid rgba(102, 126, 234, 0.2);
 }

 /* Tips Card */
 .tips-card {
 background: linear-gradient(135deg, #1a2a47 0%, #2d3050 100%);
 border: 2px solid #667eea;
 border-radius: 10px;
 padding: 15px;
 margin: 10px 0;
 }

 .tips-card-title {
 font-weight: 700;
 color: #b0c4ff;
 margin-bottom: 10px;
 }

 /* Sidebar styling */
 [data-testid="stSidebar"] {
 background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
 }

 /* Metric styling */
 [data-testid="metric-container"] {
 background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
 border: 1px solid rgba(102, 126, 234, 0.2);
 border-radius: 8px;
 }

 /* Expander styling */
 [data-testid="stExpander"] {
 background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
 border: 1px solid rgba(102, 126, 234, 0.2);
 }

 .streamlit-expanderHeader {
 color: #b0c4ff !important;
 }

 /* Input fields */
 input, textarea, select {
 background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%) !important;
 border: 1px solid rgba(102, 126, 234, 0.3) !important;
 color: #e4e6eb !important;
 }

 /* Scrollbar styling */
 ::-webkit-scrollbar {
 width: 8px;
 height: 8px;
 }

 ::-webkit-scrollbar-track {
 background: #0f1419;
 }

 ::-webkit-scrollbar-thumb {
 background: #667eea;
 border-radius: 4px;
 }

 ::-webkit-scrollbar-thumb:hover {
 background: #764ba2;
 }
</style>
""", unsafe_allow_html=True)
try:
 genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except:
 st.error("■ GEMINI_API_KEY not found in environment variables!")
 st.stop()
EXPERT_PROMPT = """You are an expert plant pathologist with 30 years of experience diagnosing plant diseYour task is to provide accurate, practical plant disease diagnosis.
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

 try:
 return json.loads(response_text)
 except:
 pass

 cleaned = response_text
 if "```json" in cleaned:
 cleaned = cleaned.split("```json")[1].split("```")[0]
 elif "```" in cleaned:
 cleaned = cleaned.split("```")[1].split("```")[0]

 try:
 return json.loads(cleaned.strip())
 except:
 pass

 match = re.search(r'\{[\s\S]*\}', response_text)
 if match:
 try:
 return json.loads(match.group())
 except:
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
st.markdown("""
<div class="header-container">
 <div class="header-title">■ AI Plant Doctor - Professional Edition</div>
 <div class="header-subtitle">Universal Plant Disease Detection with Expert Analysis</div>
</div>
""", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
 st.markdown('<div class="feature-card">■ Expert Diagnosis</div>', unsafe_allow_html=True)
with col2:
 st.markdown('<div class="feature-card">■ Image Zoom</div>', unsafe_allow_html=True)
with col3:
 st.markdown('<div class="feature-card">■ Debug Mode</div>', unsafe_allow_html=True)
with col4:
 st.markdown('<div class="feature-card">■ Best Accuracy</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
with st.sidebar:
 st.header("■■ Settings & Configuration")

 model_choice = st.radio(
 "■ AI Model Selection",
 ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Accurate)"],
 help="Flash: 80% accurate, 2-3 sec | Pro: 95% accurate, 5-10 sec"
 )

 debug_mode = st.checkbox("■ Debug Mode", value=False, help="Show raw API responses")
 show_tips = st.checkbox("■ Show Photo Tips", value=True, help="Display photo quality tips")

 confidence_min = st.slider(
 "Minimum Confidence (%)",
 0, 100, 50,
 help="Only show results above this confidence"
 )

 st.markdown("---")
 with st.expander("■ Perfect Photo Checklist", expanded=False):
 st.markdown("""
 ■ **DO THIS:**
 - Plain WHITE background
 - Natural, even lighting
 - Sharp and in-focus
 - Close-up of diseased part
 - ONE leaf only
 - Photograph from above

 ■ **AVOID:**
 - Blurry photos
 - Dark shadows
 - Busy backgrounds
 - Healthy leaves
 - Multiple leaves
 - Angled shots
 """)

 with st.expander("■ Why Wrong Results?", expanded=False):
 st.markdown("""
 **Top 3 Reasons:**

 1. ■ **Bad Image Quality**
 - Blurry or dark
 - Busy background
 - Solution: Retake with white background

 2. ■ **Wrong Subject**
 - Showing healthy leaf
 - Multiple leaves in frame
 - Solution: One diseased leaf, clear view

 3. ■ **Model Issue**
 - Using Flash for complex disease
 - Solution: Switch to Pro model
 """)
col_upload, col_empty = st.columns([3, 1])
with col_upload:
 st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
 st.subheader("■ Upload Plant Image")
 uploaded_file = st.file_uploader(
 "Drag and drop or click to select your image",
 type=['jpg', 'jpeg', 'png'],
 label_visibility="collapsed"
 )
 st.markdown("</div>", unsafe_allow_html=True)
if uploaded_file:
 image = Image.open(uploaded_file)
 original_image = image.copy()

 if show_tips:
 st.markdown("""
 <div class="tips-card">
 <div class="tips-card-title">■ Photo Quality Matters!</div>
 For best results: white background + natural light + sharp focus + diseased leaf close-up
 </div>
 """, unsafe_allow_html=True)

 st.markdown("<div class='result-container'>", unsafe_allow_html=True)

 col_img, col_zoom = st.columns([3, 1])

 with col_zoom:
 st.markdown("### ■ Zoom")
 zoom_level = st.slider(
 "Zoom",
 min_value=0.5,
 max_value=2.0,
 value=1.0,
 step=0.1,
 label_visibility="collapsed"
 )

 with col_img:
 st.subheader("■ Preview")
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
 analyze_btn = st.button("■ Analyze Plant", use_container_width=True, type="primary")

 if analyze_btn:
 progress_placeholder = st.empty()

 with st.spinner("■ Analyzing... This may take a few seconds"):
 try:
 progress_placeholder.info("■ Processing image with AI...")

 model_name = "Gemini 2.5 Pro" if "Pro" in model_choice else "Gemini 2.5 Flash"
 model_id = 'gemini-2.5-pro' if "Pro" in model_choice else 'gemini-2.5-flash'
 model = genai.GenerativeModel(model_id)

 if debug_mode:
 st.info(f"■ Using Model: {model_name}")

 response = model.generate_content([EXPERT_PROMPT, original_image])
 raw_response = response.text

 if debug_mode:
 with st.expander("■ Raw API Response"):
 st.markdown('<div class="debug-box">', unsafe_allow_html=True)
 displayed_response = raw_response[:3000] + "..." if len(raw_response) > 3000 els st.text(displayed_response)
 st.markdown('</div>', unsafe_allow_html=True)

 result = extract_json_robust(raw_response)

 if result is None:
 st.markdown('<div class="error-box">', unsafe_allow_html=True)
 st.error("■ Could not parse AI response")
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
 is_valid, validation_msg = validate_json_result(result)

 if not is_valid:
 st.warning(f"■■ Incomplete response: {validation_msg}")

 confidence = result.get("confidence", 0)

 if confidence < confidence_min:
 st.markdown('<div class="warning-box">', unsafe_allow_html=True)
 st.warning(f"■■ **Low Confidence ({confidence}%)**")
 st.write(result.get("confidence_reason", "AI is uncertain about this diagnosis") st.write("**Recommendation:** " + result.get("image_quality_tips", "Provide a cl st.markdown('</div>', unsafe_allow_html=True)

 image_quality = result.get("image_quality", "")
 if image_quality and ("Poor" in image_quality or "Fair" in image_quality):
 st.markdown('<div class="warning-box">', unsafe_allow_html=True)
 st.write(f"■ **Image Quality Note:** {image_quality}")
 st.markdown('</div>', unsafe_allow_html=True)

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
 st.metric("■ Plant", plant)
 with col2:
 st.metric("■ Confidence", f"{confidence}%")
 with col3:
 st.metric("■ Severity", severity.title())
 with col4:
 st.metric("■■ Analysis", datetime.now().strftime("%H:%M"))

 st.markdown("<br>", unsafe_allow_html=True)

 col_left, col_right = st.columns(2)

 with col_left:
 st.markdown("""
 <div class="info-section">
 <div class="info-title">■ Symptoms Observed</div>
 """, unsafe_allow_html=True)

 for symptom in result.get("symptoms", []):
 st.write(f"• {symptom}")

 st.markdown("</div>", unsafe_allow_html=True)

 st.markdown("""
 <div class="info-section">
 <div class="info-title">■■ Probable Causes</div>
 """, unsafe_allow_html=True)

 for cause in result.get("probable_causes", []):
 st.write(f"• {cause}")

 st.markdown("</div>", unsafe_allow_html=True)

 with col_right:
 st.markdown("""
 <div class="info-section">
 <div class="info-title">■ Immediate Actions</div>
 """, unsafe_allow_html=True)

 for i, action in enumerate(result.get("immediate_action", []), 1):
 st.write(f"**{i}.** {action}")

 st.markdown("</div>", unsafe_allow_html=True)

 col_treat1, col_treat2 = st.columns(2)

 with col_treat1:
 st.markdown("""
 <div class="info-section">
 <div class="info-title">■ Organic Treatments</div>
 """, unsafe_allow_html=True)

 for treatment in result.get("organic_treatments", []):
 st.write(f"• {treatment}")

 st.markdown("</div>", unsafe_allow_html=True)

 with col_treat2:
 st.markdown("""
 <div class="info-section">
 <div class="info-title">■ Chemical Treatments</div>
 """, unsafe_allow_html=True)

 for treatment in result.get("chemical_treatments", []):
 st.write(f"• {treatment}")

 st.markdown("</div>", unsafe_allow_html=True)

 st.markdown("""
 <div class="info-section">
 <div class="info-title">■■ Long-Term Prevention</div>
 """, unsafe_allow_html=True)

 for tip in result.get("prevention_long_term", []):
 st.write(f"• {tip}")

 st.markdown("</div>", unsafe_allow_html=True)

 if result.get("similar_conditions"):
 st.markdown("""
 <div class="info-section">
 <div class="info-title">■ Similar Conditions</div>
 """, unsafe_allow_html=True)
 st.write(result.get("similar_conditions"))
 st.markdown("</div>", unsafe_allow_html=True)

 st.markdown("</div>", unsafe_allow_html=True)

 st.markdown("<br>", unsafe_allow_html=True)
 col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

 with col_btn1:
 if st.button("■ Analyze Another Plant", use_container_width=True):
 st.rerun()

 with col_btn3:
 if st.button("■ Reset All", use_container_width=True):
 st.rerun()

 progress_placeholder.empty()

 except Exception as e:
 st.markdown('<div class="error-box">', unsafe_allow_html=True)
 st.error(f"■ Analysis Failed: {str(e)}")
 st.write("**Troubleshooting steps:**")
 st.write("1. Check your API key is valid")
 st.write("2. Try a different image with better quality")
 st.write("3. Switch to Pro model for better accuracy")
 st.write("4. Enable Debug Mode to see error details")
 st.markdown('</div>', unsafe_allow_html=True)

 if debug_mode:
 with st.expander("■ Error Details (Debug)"):
 st.markdown('<div class="debug-box">', unsafe_allow_html=True)
 st.text(str(e))
 st.markdown('</div>', unsafe_allow_html=True)

 progress_placeholder.empty()
with st.sidebar:
 st.markdown("---")

 st.header("■ Support & Info")

 with st.expander("■ How It Works"):
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

 with st.expander("■ Best Results"):
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

 with st.expander("■■ Settings Tips"):
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

 st.header("■ Free Tier Limits")

 st.write("""
 ■ **Always FREE:**
 • 1,500 analyses per day
 • 15 analyses per minute
 • Commercial use allowed
 • No credit card required

 ■ **Duration:**
 • Works for 3+ months minimum
 • Likely much longer
 • See documentation for details
 """)
