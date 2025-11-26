import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

# ------------------------------
# PAGE CONFIG & STYLING
# ------------------------------
st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
... [Your full CSS styling here, unchanged from your current app] ...
</style>""", unsafe_allow_html=True)

# ------------------------------
# GEMINI API CONFIG
# ------------------------------
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except:
    st.error("❌ GEMINI_API_KEY not found in environment variables!")
    st.stop()

# ------------------------------
# TRANSLATION FUNCTION
# ------------------------------
def translate_json_values_via_gemini(obj, target_lang_code: str):
    """Translate all text values in JSON object to selected language."""
    if not target_lang_code or target_lang_code.lower() == "en":
        return obj
    try:
        model = genai.GenerativeModel("gemini-2.0-pro")
        original_json = json.dumps(obj, ensure_ascii=False)
        prompt = (
            f"Translate ALL text values in the following JSON into '{target_lang_code}'. "
            "Keep the JSON structure EXACTLY the same. Only translate values, not keys. "
            "Return ONLY the JSON, no explanations, no markdown.\n\n"
            f"{original_json}"
        )
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except Exception as e:
        if debug_mode:
            st.warning(f"Translation failed: {str(e)}")
        return obj

# ------------------------------
# CONSTANTS AND TEMPLATES
# ------------------------------
EXPERT_PROMPT_TEMPLATE = """You are an elite plant pathologist with 40 years of specialized experience diagnosing diseases in {plant_type}.
... [Full JSON template unchanged from your app] ...
"""

PLANT_COMMON_DISEASES = {
    "Tomato": "Early blight, Late blight, Septoria leaf spot, Fusarium wilt, Bacterial wilt, Spider mites, Powdery mildew",
    "Rose": "Black spot, Powdery mildew, Rose rosette virus, Rose slugs, Rust, Botrytis",
    "Apple": "Apple scab, Fire blight, Powdery mildew, Cedar apple rust, Sooty blotch, Apple maggot",
    "Lettuce": "Lettuce mosaic virus, Downy mildew, Septoria leaf spot, Bottom rot, Tip burn",
    "Grape": "Powdery mildew, Downy mildew, Black rot, Phomopsis cane and leaf spot, Grape phylloxera",
    "Pepper": "Anthracnose, Bacterial wilt, Phytophthora blight, Cercospora leaf spot, Pepper weevil",
    "Cucumber": "Powdery mildew, Downy mildew, Angular leaf spot, Anthracnose, Cucumber beetles",
    "Strawberry": "Leaf scorch, Powdery mildew, Red stele root rot, Angular leaf spot, Slugs",
    "Corn": "Leaf blotch, Rust, Stewart's wilt, Fusarium ear rot, Corn borer",
    "Potato": "Late blight, Early blight, Verticillium wilt, Potato scab, Rhizoctonia",
}

# ------------------------------
# UTILITY FUNCTIONS
# ------------------------------
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

def enhance_image_for_analysis(image):
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.3)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.2)
    return image

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

# ------------------------------
# SIDEBAR SETTINGS
# ------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_choice = st.radio(
        "🤖 AI Model",
        ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Accurate)"],
        help="Pro recommended for best accuracy"
    )
    
    debug_mode = st.checkbox("🐛 Debug Mode", value=False)
    show_tips = st.checkbox("💡 Show Tips", value=True)
    
    confidence_min = st.slider("Min Confidence (%)", 0, 100, 65)
    
    st.markdown("---")
    st.header("🌐 Translate Result")
    target_lang = st.selectbox(
        "Select language",
        ["English", "Hindi", "Bengali", "Tamil", "Marathi", "Urdu", "Arabic", "Japanese"]
    )
    lang_code_map = {
        "English": "en", "Hindi": "hi", "Bengali": "bn", "Tamil": "ta",
        "Marathi": "mr", "Urdu": "ur", "Arabic": "ar", "Japanese": "ja"
    }

# ------------------------------
# PLANT TYPE SELECTION & UPLOAD
# ------------------------------
col_plant, col_upload = st.columns([1, 2])
with col_plant:
    st.subheader("🌱 Select Plant Type")
    plant_options = ["Select a plant..."] + sorted(list(PLANT_COMMON_DISEASES.keys())) + ["Other (Manual Entry)"]
    selected_plant = st.selectbox("What plant do you have?", plant_options, label_visibility="collapsed")
    if selected_plant == "Other (Manual Entry)":
        custom_plant = st.text_input("Enter plant name", placeholder="e.g., Banana, Orange, Pepper")
        plant_type = custom_plant if custom_plant else "Unknown Plant"
    else:
        plant_type = selected_plant if selected_plant != "Select a plant..." else None
    if plant_type and plant_type in PLANT_COMMON_DISEASES:
        st.markdown(f"**Common diseases in {plant_type}:** {PLANT_COMMON_DISEASES[plant_type]}")

with col_upload:
    st.subheader("📤 Upload Leaf Images")
    uploaded_files = st.file_uploader("Select images", type=['jpg','jpeg','png'], accept_multiple_files=True)

# ------------------------------
# ANALYSIS
# ------------------------------
if uploaded_files and plant_type and plant_type != "Select a plant...":
    images = [Image.open(f) for f in uploaded_files[:3]]
    analyze_btn = st.button(f"🔬 Analyze {plant_type}")

    if analyze_btn:
        progress_placeholder = st.empty()
        with st.spinner("🔄 Analyzing images..."):
            try:
                model_id = 'gemini-2.5-pro' if "Pro" in model_choice else 'gemini-2.5-flash'
                model = genai.GenerativeModel(model_id)
                common_diseases = PLANT_COMMON_DISEASES.get(plant_type, "various plant diseases")
                prompt = EXPERT_PROMPT_TEMPLATE.format(plant_type=plant_type, common_diseases=common_diseases)
                
                enhanced_images = [enhance_image_for_analysis(img.copy()) for img in images]
                response = model.generate_content([prompt] + enhanced_images)
                raw_response = response.text
                
                result = extract_json_robust(raw_response)
                
                # ------------------------------
                # TRANSLATE RESULT
                # ------------------------------
                if result and target_lang != "English":
                    result = translate_json_values_via_gemini(result, lang_code_map[target_lang])
                
                # ------------------------------
                # DISPLAY RESULT
                # ------------------------------
                if result:
                    is_valid, msg = validate_json_result(result)
                    if not is_valid:
                        st.warning(f"⚠️ Incomplete response: {msg}")
                    
                    confidence = result.get("confidence", 0)
                    disease_name = result.get("disease_name", "Unknown")
                    disease_type = result.get("disease_type", "unknown")
                    severity = result.get("severity", "unknown")
                    severity_class = get_severity_badge_class(severity)
                    type_class = get_type_badge_class(disease_type)

                    # Result header
                    st.markdown(f"""
                    <div class="disease-header">
                        <div class="disease-name">{disease_name}</div>
                        <div class="disease-meta">
                            <span class="severity-badge {severity_class}">{severity.title()}</span>
                            <span class="type-badge {type_class}">{disease_type.title()}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("🌱 Plant", plant_type)
                    col2.metric("📊 Confidence", f"{confidence}%")
                    col3.metric("🚨 Severity", severity.title())
                    col4.metric("⏱️ Time", datetime.now().strftime("%H:%M"))

                    # Symptoms, Causes, Actions, Treatments, Prevention
                    col_left, col_right = st.columns(2)
                    with col_left:
                        if result.get("symptoms"):
                            st.markdown("<div class='info-section'><div class='info-title'>🔍 Symptoms</div>", unsafe_allow_html=True)
                            for s in result.get("symptoms", []):
                                st.write(f"• {s}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        if result.get("differential_diagnosis"):
                            st.markdown("<div class='info-section'><div class='info-title'>🔀 Other Possibilities</div>", unsafe_allow_html=True)
                            for d in result.get("differential_diagnosis", []):
                                st.write(f"• {d}")
                            st.markdown("</div>", unsafe_allow_html=True)
                    with col_right:
                        if result.get("probable_causes"):
                            st.markdown("<div class='info-section'><div class='info-title'>⚠️ Causes</div>", unsafe_allow_html=True)
                            for c in result.get("probable_causes", []):
                                st.write(f"• {c}")
                            st.markdown("</div>", unsafe_allow_html=True)
                        if result.get("immediate_action"):
                            st.markdown("<div class='info-section'><div class='info-title'>⚡ Actions</div>", unsafe_allow_html=True)
                            for i, a in enumerate(result.get("immediate_action", []), 1):
                                st.write(f"**{i}.** {a}")
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Treatments
                    col_treat1, col_treat2 = st.columns(2)
                    with col_treat1:
                        if result.get("organic_treatments"):
                            st.markdown("<div class='info-section'><div class='info-title'>🌱 Organic Treatments</div>", unsafe_allow_html=True)
                            for t in result.get("organic_treatments", []):
                                st.write(f"• {t}")
                            st.markdown("</div>", unsafe_allow_html=True)
                    with col_treat2:
                        if result.get("chemical_treatments"):
                            st.markdown("<div class='info-section'><div class='info-title'>💊 Chemical Treatments</div>", unsafe_allow_html=True)
                            for t in result.get("chemical_treatments", []):
                                st.write(f"• {t}")
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Prevention
                    if result.get("prevention_long_term"):
                        st.markdown("<div class='info-section'><div class='info-title'>🛡️ Prevention</div>", unsafe_allow_html=True)
                        for p in result.get("prevention_long_term", []):
                            st.write(f"• {p}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Notes & Similar Conditions
                    if result.get("plant_specific_notes"):
                        st.markdown(f"<div class='info-section'><div class='info-title'>📝 {plant_type} Care Notes</div>{result.get('plant_specific_notes')}</div>", unsafe_allow_html=True)
                    if result.get("similar_conditions"):
                        st.markdown(f"<div class='info-section'><div class='info-title'>🔎 Similar Conditions in {plant_type}</div>{result.get('similar_conditions')}</div>", unsafe_allow_html=True)

                else:
                    st.error("❌ Could not parse AI response")
                
            except Exception as e:
                st.error(f"❌ Analysis Failed: {str(e)}")
                if debug_mode:
                    st.text(str(e))

elif uploaded_files and not plant_type:
    st.warning("⚠️ Please select a plant type first for best accuracy!")
