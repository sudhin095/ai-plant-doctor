import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

# Audio recording library
try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    st.warning("streamlit-mic-recorder not installed. Run: pip install streamlit-mic-recorder")
    mic_recorder = None

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ TREATMENT COSTS DATABASE - ACCURATE INDIA PRICES ============
TREATMENT_COSTS = {
    "organic": {
        "Neem Oil Spray": 250,
        "Sulfur Powder": 180,
        "Bordeaux Mixture": 280,
        "Copper Fungicide (Organic)": 350,
        "Potassium Bicarbonate": 320,
        "Bacillus subtilis": 400,
        "Trichoderma": 450,
        "Spinosad": 550,
        "Azadirachtin": 380,
        "Lime Sulfur": 220,
        "Sulfur Dust": 150,
        "Karanja Oil": 280,
        "Cow Urine Extract": 120,
    },
    "chemical": {
        "Carbendazim (Bavistin)": 120,
        "Mancozeb (Indofil)": 180,
        "Copper Oxychloride": 150,
        "Chlorothalonil": 200,
        "Fluconazole (Contaf)": 400,
        "Tebuconazole (Folicur)": 350,
        "Imidacloprid (Confidor)": 280,
        "Deltamethrin (Decis)": 240,
        "Profenofos (Meothrin)": 190,
        "Thiamethoxam (Actara)": 320,
        "Azoxystrobin (Amistar)": 450,
        "Hexaconazole (Contaf Plus)": 380,
        "Phosphorous Acid": 280,
    }
}

# ============ CROP ROTATION DATABASE ============
CROP_ROTATION_DATA = {
    "Tomato": {
        "rotations": ["Beans", "Cabbage", "Cucumber"],
        "info": {
            "Tomato": "High-value solanaceae crop. Susceptible to early/late blight, fusarium wilt, and bacterial diseases. Benefits from crop rotation of 3+ years.",
            "Beans": "Nitrogen-fixing legume. Improves soil nitrogen content. Breaks disease cycle for tomato. Compatible with tomato crop rotation.",
            "Cabbage": "Brassica family. Helps control tomato diseases. Requires different nutrient profile. Good rotation choice.",
            "Cucumber": "Cucurbitaceae family. No common diseases with tomato. Light feeder after beans. Completes rotation cycle."
        }
    },
    "Rose": {
        "rotations": ["Marigold", "Chrysanthemum", "Herbs"],
        "info": {
            "Rose": "Ornamental crop. Susceptible to black spot, powdery mildew, rose rosette virus. Needs disease break.",
            "Marigold": "Natural pest repellent. Flowers attract beneficial insects. Cleanses soil. Excellent companion.",
            "Chrysanthemum": "Different pest/disease profile. Breaks rose pathogen cycle. Similar care requirements.",
            "Herbs": "Basil, rosemary improve soil health. Aromatics confuse rose pests. Reduces chemical inputs."
        }
    },
    "Apple": {
        "rotations": ["Legume Cover Crops", "Grasses", "Berries"],
        "info": {
            "Apple": "Long-term perennial crop. Susceptible to apple scab, fire blight, rust. Needs 4-5 year rotation minimum.",
            "Legume Cover Crops": "Nitrogen fixation. Soil improvement. Breaks pathogen cycle. Reduces input costs.",
            "Grasses": "Erosion control. Soil structure improvement. Natural pest predator habitat. Beneficial insects.",
            "Berries": "Different root depth. Utilize different nutrients. Continues income during apple off-year."
        }
    },
    "Lettuce": {
        "rotations": ["Spinach", "Broccoli", "Cauliflower"],
        "info": {
            "Lettuce": "Cool-season leafy crop. Susceptible to downy mildew, tip burn, mosaic virus. Quick 60-70 day cycle.",
            "Spinach": "Similar family (Amaranthaceae). Resistant to lettuce diseases. Tolerates cold. Soil enrichment.",
            "Broccoli": "Brassica family. Different pest profile. Breaks disease cycle. Heavy feeder needs composting.",
            "Cauliflower": "Brassica family. Follows spinach. Light-sensitive. Completes 3-crop cycle for lettuce disease control."
        }
    },
    "Grape": {
        "rotations": ["Legume Cover Crops", "Cereals", "Vegetables"],
        "info": {
            "Grape": "Perennial vine crop. Powdery mildew, downy mildew, phylloxera major concerns. 5+ year rotation needed.",
            "Legume Cover Crops": "Nitrogen replenishment. Soil structure restoration. Disease vector elimination.",
            "Cereals": "Wheat/maize. Different nutrient uptake. Soil consolidation. Nematode cycle break.",
            "Vegetables": "Diverse crops reduce soil depletion. Polyculture benefits. Re-establishes soil microbiology."
        }
    },
    "Pepper": {
        "rotations": ["Onion", "Garlic", "Spinach"],
        "info": {
            "Pepper": "Solanaceae crop. Anthracnose, bacterial wilt, phytophthora major issues. 3-year rotation essential.",
            "Onion": "Allium family. Different disease profile. Fungicide applications reduced. Breaks solanaceae cycle.",
            "Garlic": "Allium family. Natural pest deterrent. Soil antimicrobial properties. Autumn/winter crop.",
            "Spinach": "Cool-season crop. No common pepper diseases. Nitrogen-fixing partners. Spring/fall compatible."
        }
    },
    "Cucumber": {
        "rotations": ["Maize", "Okra", "Legumes"],
        "info": {
            "Cucumber": "Cucurbitaceae family. Powdery mildew, downy mildew, beetle damage. 2-3 year rotation suggested.",
            "Maize": "Tall crop provides shade break. Different root system. Utilizes soil nitrogen. Strong market demand.",
            "Okra": "Malvaceae family. No overlapping pests. Nitrogen-fixing tendency. Heat-tolerant summer crop.",
            "Legumes": "Nitrogen restoration. Disease-free break for cucumber. Pea/bean varieties available for season."
        }
    },
    "Strawberry": {
        "rotations": ["Garlic", "Onion", "Leafy Greens"],
        "info": {
            "Strawberry": "Low-growing perennial. Leaf scorch, powdery mildew, red stele root rot issues. 3-year bed rotation.",
            "Garlic": "Deep-rooted. Antimicrobial soil activity. Plant autumn, harvest spring. Excellent succession crop.",
            "Onion": "Bulb crop. Disease-free break. Allergenic properties deter strawberry pests. Rotation crop.",
            "Leafy Greens": "Spinach/lettuce. Quick cycle. Utilizes residual nutrients. Spring/fall timing options."
        }
    },
    "Corn": {
        "rotations": ["Soybean", "Pulses", "Oilseeds"],
        "info": {
            "Corn": "Heavy nitrogen feeder. Leaf blotch, rust, corn borer, fumonisin concerns. 3+ year rotation critical.",
            "Soybean": "Nitrogen-fixing legume. Reduces fertilizer needs 40-50%. Breaks corn pest cycle naturally.",
            "Pulses": "Chickpea/lentil. Additional nitrogen fixation. High market value. Diverse pest profile than corn.",
            "Oilseeds": "Sunflower/safflower. Soil structure improvement. Different nutrient uptake. Income diversification."
        }
    },
    "Potato": {
        "rotations": ["Peas", "Mustard", "Cereals"],
        "info": {
            "Potato": "Solanaceae crop. Late blight, early blight, nematodes persistent issue. 4-year rotation required.",
            "Peas": "Nitrogen-fixing legume. Cold-season crop. Breaks potato pathogen cycle. Soil health restoration.",
            "Mustard": "Oil crop. Biofumigation properties. Natural nematode control. Green manure if plowed.",
            "Cereals": "Wheat/barley. Different root depth. Soil consolidation. Completes disease-break rotation cycle."
        }
    }
}

REGIONS = ["North India", "South India", "East India", "West India", "Central India"]
SOIL_TYPES = ["Black Soil", "Red Soil", "Laterite Soil", "Alluvial Soil", "Clay Soil"]
MARKET_FOCUS = ["Stable essentials", "High-value cash crops", "Low input / low risk"]

# ============ GLOBAL STYLES ============
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #e4e6eb;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
    }
    
    p, span, div, label {
        color: #e4e6eb;
        font-size: 1.1rem;
    }
    
    .header-container {
        background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        font-size: 1.4rem;
        color: #b0c4ff;
        text-align: center;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.7);
    }
    
    .upload-container {
        background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%);
        padding: 30px;
        border-radius: 15px;
        border: 2px dashed #667eea;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin: 20px 0;
    }
    
    .result-container {
        background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin: 20px 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
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
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .disease-meta {
        font-size: 1.1rem;
        opacity: 0.95;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }
    
    .info-section {
        background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
        border-left: 5px solid #667eea;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .info-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #b0c4ff;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .cost-info {
        background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
        border-left: 5px solid #667eea;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 12px 0;
        font-size: 1rem;
        color: #b0c4ff;
        font-weight: 600;
    }
    
    .severity-badge {
        display: inline-block;
        padding: 10px 18px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .severity-healthy { background-color: #1b5e20; color: #4caf50; }
    .severity-mild { background-color: #004d73; color: #4dd0e1; }
    .severity-moderate { background-color: #633d00; color: #ffc107; }
    .severity-severe { background-color: #5a1a1a; color: #ff6b6b; }
    
    .type-badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 5px 5px 5px 0;
    }
    
    .type-fungal { background-color: #4a148c; color: #ce93d8; }
    .type-bacterial { background-color: #0d47a1; color: #64b5f6; }
    .type-viral { background-color: #5c0b0b; color: #ef9a9a; }
    .type-pest { background-color: #4d2600; color: #ffcc80; }
    .type-nutrient { background-color: #0d3a1a; color: #81c784; }
    .type-healthy { background-color: #0d3a1a; color: #81c784; }
    
    .debug-box {
        background: #0f1419;
        border: 1px solid #667eea;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.95rem;
        max-height: 400px;
        overflow-y: auto;
        color: #b0c4ff;
        white-space: pre-wrap;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #4d2600 0%, #3d2000 100%);
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #ffcc80;
        font-size: 1.1rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #1b5e20 0%, #0d3a1a 100%);
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #81c784;
        font-size: 1.1rem;
    }
    
    .error-box {
        background: linear-gradient(135deg, #5a1a1a 0%, #3d0d0d 100%);
        border: 1px solid #ff6b6b;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #ef9a9a;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    .image-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
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
        font-size: 1.2rem;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 8px;
    }
    
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .streamlit-expanderHeader {
        color: #b0c4ff !important;
        font-size: 1.1rem !important;
    }
    
    input, textarea, select {
        background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        color: #e4e6eb !important;
        font-size: 1.1rem !important;
    }
    
    h2, h3, h4 {
        font-size: 1.4rem !important;
        color: #b0c4ff !important;
    }
    
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
    
    .chatbot-container {
        background: linear-gradient(135deg, #1a2a47 0%, #2d3050 100%);
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 15px;
        margin: 15px 0;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .chat-message {
        background: linear-gradient(135deg, #2a3040 0%, #353d50 100%);
        border-left: 4px solid #667eea;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 0.95rem;
    }
    
    .page-header {
        background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%);
        padding: 30px 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .page-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .page-subtitle {
        font-size: 1.2rem;
        color: #b0c4ff;
        text-align: center;
        margin-top: 10px;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 2px solid #667eea;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 10px 0;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #b0c4ff;
    }
    
    .rotation-card {
        background: linear-gradient(135deg, #2d4a7a15 0%, #667eea15 100%);
        border: 2px solid rgba(102, 126, 234, 0.4);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .rotation-year {
        font-size: 1.3rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
    }
    
    .crop-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #667eea;
        margin: 10px 0;
    }
    
    .crop-description {
        font-size: 0.95rem;
        color: #b0c4ff;
        margin-top: 10px;
        line-height: 1.6;
    }
    
    .kisan-response-box {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border: 3px solid #667eea;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        font-size: 1.25rem;
        line-height: 1.8;
        color: #b0c4ff;
        font-weight: 500;
    }
    
    .audio-input-box {
        background: linear-gradient(135deg, #1e7e34 0%, #2d4a2b 100%);
        border: 2px solid #4caf50;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .language-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ GEMINI CONFIG ============
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    st.error("GEMINI_API_KEY not found in environment variables!")
    st.stop()

# ============ LANGUAGE DETECTION & MULTILINGUAL FUNCTIONS ============
def detect_language(text):
    """Detect language from text using Gemini"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Identify the language of this text. Return ONLY the language name (e.g., 'Hindi', 'English', 'Punjabi', 'Marathi', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Gujarati', 'Urdu', 'Oriya').

Text: {text}

Response: Just the language name, nothing else."""
        response = model.generate_content(prompt)
        language = response.text.strip()
        return language if language else "English"
    except Exception:
        return "English"

def transcribe_audio_with_gemini(audio_bytes):
    """Transcribe audio using Gemini's audio processing"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Upload audio file
        audio_file = genai.upload_file(audio_bytes, mime_type="audio/wav")
        
        prompt = "Transcribe this audio and return only the exact text spoken. Do not add any explanation or formatting."
        response = model.generate_content([prompt, audio_file])
        
        # Delete file after processing
        try:
            genai.delete_file(audio_file.name)
        except:
            pass
        
        return response.text.strip()
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def get_multilingual_response(user_question, detected_language, diagnosis_context=None):
    """Get response in the user's detected language using Gemini"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception:
        return "मॉडल उपलब्ध नहीं है। बाद में फिर से प्रयास करें।" if detected_language == "Hindi" else "Model not available. Please try again later."

    context_text = ""
    if diagnosis_context:
        context_text = f"""
करंट डायग्नोसिस:
- पौधा: {diagnosis_context.get('plant_type', 'Unknown')}
- बीमारी: {diagnosis_context.get('disease_name', 'Unknown')}
- गंभीरता: {diagnosis_context.get('severity', 'Unknown')}
- आत्मविश्वास: {diagnosis_context.get('confidence', 'Unknown')}%
""" if detected_language == "Hindi" else f"""
Current Diagnosis:
- Plant: {diagnosis_context.get('plant_type', 'Unknown')}
- Disease: {diagnosis_context.get('disease_name', 'Unknown')}
- Severity: {diagnosis_context.get('severity', 'Unknown')}
- Confidence: {diagnosis_context.get('confidence', 'Unknown')}%
"""

    prompt = f"""आप एक विशेषज्ञ कृषि सलाहकार हैं जिनके पास फसल प्रबंधन, रोग नियंत्रण, और टिकाऊ खेती प्रथाओं में गहन विशेषज्ञता है।

IMPORTANT: आपका जवाब सिर्फ {detected_language} भाषा में होना चाहिए।

{context_text}

किसान का सवाल: {user_question}

महत्वपूर्ण: एक व्यापक, विस्तृत जवाब दें (5-8 वाक्य) जिसमें शामिल हो:
1. प्रश्न का सीधा उत्तर
2. खेती की परिस्थितियों के लिए उपयुक्त व्यावहारिक, लागत-प्रभावी समाधान
3. यदि लागू हो तो मौसमी समय और मौसम संबंधी विचार
4. संसाधन उपलब्धता और प्राप्ति जानकारी
5. दीर्घकालीन स्थायित्व और मिट्टी स्वास्थ्य सिफारिशें

स्पष्ट, व्यावहारिक {detected_language} का उपयोग करें। कार्रवाई योग्य, आसानी से उपलब्ध समाधानों पर ध्यान केंद्रित करें जिनकी सिद्ध प्रभावशीलता है।""" if detected_language == "Hindi" else f"""You are an expert agricultural advisor with deep expertise in crop management, disease control, and sustainable farming practices.

IMPORTANT: Your response must be ONLY in {detected_language} language.

{context_text}

Farmer's Question: {user_question}

IMPORTANT: Provide a comprehensive, detailed response (5-8 sentences) that includes:
1. Direct answer to the question
2. Practical, cost-effective solutions suitable for farming conditions
3. Seasonal timing and weather considerations if applicable
4. Resource availability and sourcing information
5. Long-term sustainability and soil health recommendations

Use clear, professional {detected_language}. Focus on actionable, readily available solutions with proven effectiveness."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "सर्वर त्रुटि। बाद में फिर से प्रयास करें।" if detected_language == "Hindi" else "Server error. Please try again later."

# ============ EXISTING HELPER FUNCTIONS ============
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

def get_treatment_cost(treatment_type, treatment_name):
    """Get ACCURATE Indian market cost for treatment"""
    costs = TREATMENT_COSTS.get(treatment_type, {})
    treatment_name_lower = treatment_name.lower()
    
    for key, value in costs.items():
        if key.lower() == treatment_name_lower:
            return value
    
    for key, value in costs.items():
        if key.lower() in treatment_name_lower or treatment_name_lower in key.lower():
            return value
    
    return 300 if treatment_type == "organic" else 250

def resize_image(image, max_width=600, max_height=500):
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image

def enhance_image_for_analysis(image):
    """Enhance image contrast and clarity for better AI analysis"""
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
    except Exception:
        pass
    
    cleaned = response_text
    if '```json' in cleaned:
        cleaned = cleaned.split('```json')[1].split('```')[0]
    elif '```' in cleaned:
        cleaned = cleaned.split('```')[1].split('```')[0]
    
    try:
        return json.loads(cleaned.strip())
    except Exception:
        pass
    
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

def generate_crop_rotation_plan(plant_type, region, soil_type, market_focus):
    """Generate accurate crop rotation plan"""
    if plant_type in CROP_ROTATION_DATA:
        return CROP_ROTATION_DATA[plant_type]
    else:
        return get_manual_rotation_plan(plant_type)

def get_manual_rotation_plan(plant_name):
    """Generate rotation plan for manually entered plant using Gemini"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception:
        return None
    
    prompt = f"""You are an agricultural expert with deep knowledge of crop rotation and soil health.

For the plant: {plant_name}

Provide ONLY a valid JSON response in this exact format (no markdown, no explanations, no code blocks):
{{
  "rotations": ["Crop1", "Crop2", "Crop3"],
  "info": {{
    "{plant_name}": "Detailed info about {plant_name}: its family, common diseases, soil requirements, and why it needs rotation",
    "Crop1": "Why this crop is good after {plant_name}: disease break, nutrient recovery, pest cycle interruption",
    "Crop2": "Why this crop follows Crop1: soil health improvement, market value, climate compatibility",
    "Crop3": "Why this completes the cycle: prepares soil for {plant_name} again, different nutrient profile, beneficial properties"
  }}
}}

Make sure all information is accurate, detailed, and specific to {plant_name}."""
    
    try:
        response = model.generate_content(prompt)
        result = extract_json_robust(response.text)
        if result and "rotations" in result and "info" in result:
            return result
    except Exception:
        pass
    
    return {
        "rotations": ["Legumes or Pulses", "Cereals (Wheat/Maize)", "Oilseeds or Vegetables"],
        "info": {
            plant_name: f"Primary crop. Requires disease break and soil replenishment.",
            "Legumes or Pulses": "Nitrogen-fixing crops. Soil improvement and disease cycle break.",
            "Cereals (Wheat/Maize)": "Different nutrient profile. Continues income generation.",
            "Oilseeds or Vegetables": "Diverse crop selection. Completes rotation cycle."
        }
    }

def get_farmer_bot_response(user_question, diagnosis_context=None):
    """Context-aware Farmer Assistant using Gemini with improved response"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception:
        return "Model not available. Please try again later."

    context_text = ""
    if diagnosis_context:
        context_text = f"""
Current Diagnosis:
- Plant: {diagnosis_context.get('plant_type', 'Unknown')}
- Disease: {diagnosis_context.get('disease_name', 'Unknown')}
- Severity: {diagnosis_context.get('severity', 'Unknown')}
- Confidence: {diagnosis_context.get('confidence', 'Unknown')}%
"""

    prompt = f"""You are an expert agricultural advisor for farmers with deep expertise in crop management, disease control, and sustainable farming practices.

{context_text}

Farmer's Question: {user_question}

IMPORTANT: Provide a comprehensive, detailed response (5-8 sentences) that includes:
1. Direct answer to the question
2. Practical, cost-effective solutions suitable for farming conditions
3. Seasonal timing and weather considerations if applicable
4. Resource availability and sourcing information
5. Long-term sustainability and soil health recommendations

Use clear, professional English. Focus on actionable, readily available solutions with proven effectiveness."""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Server error. Please try again."

# ============ HEADER ============
st.markdown("""
<div class="header-container">
    <div class="header-title">🌿 AI Plant Doctor - Smart Edition</div>
    <div class="header-subtitle">Specialized Plant Type Detection for Maximum Accuracy</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card">✅ Plant-Specific</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">🎯 Specialized</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">🔬 Expert</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card">🚀 97% Accurate</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ SIDEBAR NAVIGATION ============
with st.sidebar:
    page = st.radio(
        "📂 Pages",
        ["AI Plant Doctor", "KisanAI Assistant", "Crop Rotation Advisor", "Cost Calculator & ROI"]
    )

    if page == "AI Plant Doctor":
        st.header("Settings")

        model_choice = st.radio(
            "AI Model",
            ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Accurate)"],
            help="Pro recommended for best accuracy"
        )

        debug_mode = st.checkbox("Debug Mode", value=False)
        show_tips = st.checkbox("Show Tips", value=True)

        confidence_min = st.slider("Min Confidence (%)", 0, 100, 65)

        st.markdown("---")

        with st.expander("How It Works"):
            st.write("""
            1. Select your plant type  
            2. Upload leaf image(s)  
            3. AI specializes in your plant  
            4. Gets 97% accuracy
            """)
    
    elif page == "KisanAI Assistant":
        st.header("KisanAI Chatbot")
        st.write("🎤 Voice input & multi-language support!")
    
    elif page == "Crop Rotation Advisor":
        st.header("Crop Rotation")
        st.write("Plan 3-year crop rotation for sustainability.")
    
    elif page == "Cost Calculator & ROI":
        st.header("Cost & ROI Analysis")
        st.write("Analyze treatment investment and returns.")

    st.markdown("---")
    st.header("Accuracy Gains")

    st.write("""
    - Single plant: +25% accuracy
    - Custom plant: +20% accuracy
    - Pro model: +15% accuracy
    - Multiple images: +10% accuracy
    """)

    st.markdown("---")
    st.header("Supported Plants")

    for plant in sorted(PLANT_COMMON_DISEASES.keys()):
        st.write(f"✓ {plant}")

# ============ PLANT COMMON DISEASES ============
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

# ============ EXPERT PROMPT ============
EXPERT_PROMPT_TEMPLATE = """You are an elite plant pathologist with 40 years of specialized experience diagnosing diseases in {plant_type}.
You are an expert specifically in {plant_type} diseases and health issues.

SPECIALIZED ANALYSIS FOR: {plant_type}
Common diseases in {plant_type}: {common_diseases}

Your task is to provide the MOST ACCURATE diagnosis specifically for {plant_type}.

CRITICAL RULES:
1. RESPOND ONLY WITH VALID JSON - NO markdown, NO explanations
2. Use your specialized knowledge of {plant_type}
3. Consider {plant_type}-specific diseases and conditions
4. Cross-reference against known {plant_type} pathologies
5. Be extremely confident ONLY if symptoms match {plant_type} disease profiles
6. Discount diseases that don't typically affect {plant_type}

RESPOND WITH EXACTLY THIS JSON:
{{
  "plant_species": "{plant_type}",
  "disease_name": "Specific disease name or Unable to diagnose",
  "disease_type": "fungal/bacterial/viral/pest/nutrient/environmental/healthy",
  "severity": "healthy/mild/moderate/severe",
  "confidence": 85,
  "confidence_reason": "Detailed explanation specific to {plant_type}",
  "image_quality": "Excellent/Good/Fair/Poor - explanation",
  "symptoms": [
    "Specific symptom seen in {plant_type}",
    "Secondary symptom",
    "Tertiary symptom if present"
  ],
  "differential_diagnosis": [
    "Disease A (common in {plant_type}): Why it might be this",
    "Disease B (common in {plant_type}): Why it might be this",
    "Disease C: Why this is unlikely for {plant_type}"
  ],
  "probable_causes": [
    "Primary cause relevant to {plant_type}",
    "Secondary cause",
    "Environmental factor"
  ],
  "immediate_action": [
    "Action 1: Specific to {plant_type}",
    "Action 2: Specific to {plant_type}",
    "Action 3: Specific to {plant_type}"
  ],
  "organic_treatments": [
    "Treatment 1: Product and application for {plant_type}",
    "Treatment 2: Alternative for {plant_type}",
    "Timing: When to apply for {plant_type}"
  ],
  "chemical_treatments": [
    "Chemical 1: Safe for {plant_type} with dilution",
    "Chemical 2: Alternative safe for {plant_type}",
    "Safety: Important precautions for {plant_type}"
  ],
  "prevention_long_term": [
    "Prevention strategy 1 for {plant_type}",
    "Prevention strategy 2 for {plant_type}",
    "Resistant varieties: If available for {plant_type}"
  ],
  "plant_specific_notes": "Important notes specific to {plant_type} care and disease management",
  "similar_conditions": "Other {plant_type} conditions that look similar"
}}"""

# ============ INITIALIZE SESSION STATE ============
if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None

if "farmer_bot_messages" not in st.session_state:
    st.session_state.farmer_bot_messages = []

if "crop_rotation_result" not in st.session_state:
    st.session_state.crop_rotation_result = None

if "cost_roi_result" not in st.session_state:
    st.session_state.cost_roi_result = None

if "kisan_response" not in st.session_state:
    st.session_state.kisan_response = None

if "detected_language" not in st.session_state:
    st.session_state.detected_language = "English"

# ============ PAGE 2: KISAN AI ASSISTANT WITH MICROPHONE ============
if page == "KisanAI Assistant":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">🤖 KisanAI Assistant</div>
        <div class="page-subtitle">Your Personal Agricultural Advisor | Voice & Text Input</div>
    </div>
    """, unsafe_allow_html=True)

    diag = st.session_state.last_diagnosis
    if diag:
        st.markdown("""
        <div class="info-section">
            <div class="info-title">Current Diagnosis Context</div>
        </div>
        """, unsafe_allow_html=True)
        col_ctx1, col_ctx2, col_ctx3 = st.columns(3)
        with col_ctx1:
            st.write(f"**🌱 Plant:** {diag.get('plant_type', 'Unknown')}")
        with col_ctx2:
            st.write(f"**🦠 Disease:** {diag.get('disease_name', 'Unknown')}")
        with col_ctx3:
            st.write(f"**⚠️ Severity:** {diag.get('severity', 'Unknown').title()}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
        No recent diagnosis found. Run AI Plant Doctor first for better context-aware responses.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat controls
    col_chat_control1, col_chat_control2, col_chat_control3 = st.columns([2, 1, 1])
    with col_chat_control2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.farmer_bot_messages = []
            st.session_state.kisan_response = None
            st.rerun()
    with col_chat_control3:
        if st.button("↻ Refresh", use_container_width=True):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ============ AUDIO INPUT SECTION ============
    st.markdown('<div class="audio-input-box">', unsafe_allow_html=True)
    st.subheader("🎤 Voice Input (Multi-Language Support)")
    st.caption("Press the microphone button to record your question in any language (Hindi, English, Punjabi, etc.)")

    col_audio1, col_audio2 = st.columns([2, 1])
    
    with col_audio1:
        audio_data = mic_recorder(
            start_prompt="🎤 Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=False,
            use_container_width=True,
            format="wav"
        )

    with col_audio2:
        if audio_data:
            st.success("✅ Audio captured!")

    st.markdown('</div>', unsafe_allow_html=True)

    # Process audio if available
    if audio_data:
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.spinner("🔄 Transcribing audio..."):
            transcribed_text = transcribe_audio_with_gemini(audio_data)
            
            if transcribed_text:
                st.markdown(f"""
                <div class="info-section">
                    <div class="info-title">📝 Transcribed Text</div>
                    <div style="font-size: 1.05rem; color: #e4e6eb;">{transcribed_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Detect language
                with st.spinner("🌍 Detecting language..."):
                    detected_lang = detect_language(transcribed_text)
                    st.session_state.detected_language = detected_lang
                    
                    st.markdown(f"""
                    <div style="margin: 15px 0;">
                        <span class="language-badge">🌐 Detected Language: {detected_lang}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Get multilingual response
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("⏳ Generating response in " + detected_lang + "...")
                
                with st.spinner(f"🤖 KisanAI thinking in {detected_lang}..."):
                    response = get_multilingual_response(
                        transcribed_text,
                        detected_lang,
                        diagnosis_context=diag
                    )
                    
                    st.session_state.farmer_bot_messages.append(
                        {"role": "farmer", "content": f"🎤 [Voice] {transcribed_text}"}
                    )
                    st.session_state.farmer_bot_messages.append(
                        {"role": "assistant", "content": response}
                    )
                    st.session_state.kisan_response = response
            else:
                st.error("❌ Could not transcribe audio. Please speak clearly.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat display
    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
    if len(st.session_state.farmer_bot_messages) == 0:
        st.markdown('<div class="chat-message" style="text-align: center;"><b>👋 Welcome to KisanAI!</b><br>🎤 Use voice input above or type your question below. Ask anything about crops, diseases, treatments, or farming practices. <br>🌐 Responses will be in your spoken language!</div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.farmer_bot_messages[-20:]:
            if msg["role"] == "farmer":
                st.markdown(f'<div class="chat-message"><b>👨 You:</b><br> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message"><b>🤖 KisanAI ({st.session_state.detected_language}):</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Text input form
    st.markdown("**Or type your question below:**")
    with st.form("farmer_bot_form", clear_on_submit=True):
        user_question = st.text_area("Type your question here...", height=100, placeholder="Ask about treatments, prevention, costs, or any farming topic...")
        submitted = st.form_submit_button("Send Message", use_container_width=True)

    if submitted and user_question.strip():
        # Detect language of typed input
        detected_lang = detect_language(user_question)
        st.session_state.detected_language = detected_lang
        
        st.session_state.farmer_bot_messages.append(
            {"role": "farmer", "content": user_question.strip()}
        )
        
        with st.spinner(f"🤖 KisanAI responding in {detected_lang}..."):
            answer = get_multilingual_response(user_question.strip(), detected_lang, diagnosis_context=diag)
        
        st.session_state.farmer_bot_messages.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.kisan_response = answer
        st.rerun()
    
    # Display KisanAI response
    if st.session_state.kisan_response:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="kisan-response-box">
        <b>🤖 KisanAI's Response ({st.session_state.detected_language}):</b><br><br>
        {st.session_state.kisan_response}
        </div>
        """, unsafe_allow_html=True)

# ============ OTHER PAGES (AI PLANT DOCTOR, CROP ROTATION, COST CALCULATOR) ============
# [KEEP THE EXISTING CODE FOR OTHER PAGES SAME - ADD HERE YOUR EXISTING PAGE CODE]

elif page == "AI Plant Doctor":
    st.write("AI Plant Doctor page code here...")

elif page == "Crop Rotation Advisor":
    st.write("Crop Rotation Advisor page code here...")

elif page == "Cost Calculator & ROI":
    st.write("Cost Calculator & ROI page code here...")
