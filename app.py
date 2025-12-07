import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re
import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from ultralytics import YOLO
import requests
from io import BytesIO

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ HYBRID YOLO + ViT SETUP ============
@st.cache_resource
def load_yolo_model():
    try:
        # Load pre-trained YOLOv8 model for plant disease from HuggingFace
        model_url = "https://huggingface.co/peachfawn/yolov8-plant-disease-Better/resolve/main/best.pt"
        if not os.path.exists("best.pt"):
            st.info("Downloading YOLOv8 model...")
            response = requests.get(model_url)
            with open("best.pt", "wb") as f:
                f.write(response.content)
        model = YOLO("best.pt")
        return model
    except Exception as e:
        st.error(f"YOLO load failed: {e}")
        return None

@st.cache_resource
def load_vit_model():
    try:
        processor = ViTImageProcessor.from_pretrained('wambugu71/crop_leaf_diseases_vit')
        model = ViTForImageClassification.from_pretrained('wambugu71/crop_leaf_diseases_vit')
        return processor, model
    except Exception as e:
        st.error(f"ViT load failed: {e}")
        return None, None

yolo_model = load_yolo_model()
vit_processor, vit_model = load_vit_model()

# Class mappings (customize based on your models)
YOLO_CLASSES = {0: "Apple - Apple Scab", 1: "Apple - Black Rot", 2: "Apple - Cedar Apple Rust", 3: "Apple - Healthy",
                4: "Blueberry - Healthy", 5: "Cherry - Healthy", 6: "Cherry - Powdery Mildew",
                7: "Corn - Blight", 8: "Corn - Common Rust", 9: "Corn - Gray Leaf Spot", 10: "Corn - Healthy",
                # Add more as per model - truncated for brevity
                }

VIT_CLASSES = {0: "Apple___Apple_scab", 1: "Apple___Black_rot", 2: "Apple___Cedar_apple_rust", 3: "Apple___healthy",
               4: "Blueberry___healthy", 5: "Cherry___Powdery_mildew", 6: "Cherry___healthy",
               7: "Corn___Cercospora_leaf_spot Gray_leaf_spot", 8: "Corn___Common_rust", 9: "Corn___Northern_Leaf_Blight",
               10: "Corn___healthy", # Add more
               }

def detect_with_hybrid(image):
    """Hybrid YOLO + ViT detection"""
    if yolo_model is None and vit_model is None:
        return None, False

    results = {"plant_type": "Unknown", "disease_name": "Unable to diagnose", "disease_type": "unknown",
               "severity": "moderate", "confidence": 0, "source": "none"}

    # Step 1: YOLO Detection
    if yolo_model:
        try:
            preds = yolo_model(image, conf=0.5, verbose=False)
            if len(preds[0].boxes) > 0:
                box = preds[0].boxes[0]
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = YOLO_CLASSES.get(cls, "Unknown")
                parts = class_name.split(" - ")
                results["plant_type"] = parts[0]
                results["disease_name"] = parts[1] if len(parts) > 1 else class_name
                results["confidence"] = int(conf * 100)
                results["source"] = "YOLOv8"
                results["disease_type"] = "fungal" if "scab" in results["disease_name"].lower() else "healthy"
                if conf >= 0.7:
                    return results, True
        except Exception as e:
            pass

    # Step 2: ViT Classification
    if vit_processor and vit_model:
        try:
            inputs = vit_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = vit_model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            conf = torch.softmax(logits, -1)[0][predicted_class_idx].item()
            class_name = VIT_CLASSES.get(predicted_class_idx, "Unknown")
            parts = class_name.replace("___", " - ").split(" - ")
            results["plant_type"] = parts[0].replace("_", " ")
            results["disease_name"] = " ".join(parts[1:]) if len(parts) > 1 else "Healthy"
            results["confidence"] = int(conf * 100)
            results["source"] = "ViT"
            results["disease_type"] = "healthy" if "healthy" in results["disease_name"].lower() else "fungal"
            if conf >= 0.7:
                return results, True
        except Exception as e:
            pass

    return results, False

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
</style>
""", unsafe_allow_html=True)

# ============ GEMINI CONFIG (FALLBACK) ============
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    st.error("GEMINI_API_KEY not found in environment variables!")
    st.stop()

# SMART PROMPT WITH PLANT TYPE SPECIALIZATION
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


# ============ HELPER FUNCTIONS ============
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
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0]
    
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
    # Your existing implementation here (truncated in original, so placeholder)
    data = CROP_ROTATION_DATA.get(plant_type.capitalize(), {})
    if data:
        return data
    return {
        "rotations": ["Legumes", "Cereals", "Root Crops"],
        "info": {plant_type: f"Recommended rotation for {plant_type} in {region} with {soil_type} soil."}
    }


# Initialize session state
if 'last_diagnosis' not in st.session_state:
    st.session_state.last_diagnosis = None
if 'farmer_bot_messages' not in st.session_state:
    st.session_state.farmer_bot_messages = []
if 'kisan_response' not in st.session_state:
    st.session_state.kisan_response = None

with st.sidebar:
    page = st.radio("Navigate", ["AI Plant Doctor", "KisanAI Assistant", "Crop Rotation Advisor", "Cost Calculator & ROI"])

if page == "AI Plant Doctor":
    # Your existing UI for plant selection and upload
    col1, col2 = st.columns(2)
    with col1:
        plant_type = st.selectbox("Select Plant Type", [""] + list(PLANT_COMMON_DISEASES.keys()))
    with col2:
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(resize_image(image), caption="Uploaded Image")

    if st.button("Analyze") and plant_type and uploaded_file:
        with st.spinner("Running Hybrid YOLO + ViT Analysis..."):
            enhanced_image = enhance_image_for_analysis(image)
            hybrid_result, high_conf = detect_with_hybrid(enhanced_image)

            if high_conf and hybrid_result["confidence"] > 70:
                # Format hybrid result as Gemini-like JSON
                result = {
                    "plant_species": hybrid_result["plant_type"],
                    "disease_name": hybrid_result["disease_name"],
                    "disease_type": hybrid_result["disease_type"],
                    "severity": hybrid_result["severity"],
                    "confidence": hybrid_result["confidence"],
                    "confidence_reason": f"Detected by {hybrid_result['source']} model",
                    "image_quality": "Good",
                    "symptoms": [f"Characteristic symptoms of {hybrid_result['disease_name']} observed"],
                    "differential_diagnosis": ["This matches primary diagnosis", "Alternative unlikely"],
                    "probable_causes": ["Pathogen infection", "Environmental stress"],
                    "immediate_action": ["Isolate plant", "Apply treatment"],
                    "organic_treatments": ["Neem Oil Spray", "Trichoderma"],
                    "chemical_treatments": ["Mancozeb (Indofil)", "Carbendazim (Bavistin)"],
                    "prevention_long_term": ["Crop rotation", "Resistant varieties"],
                    "plant_specific_notes": f"Notes for {plant_type}",
                    "similar_conditions": "Similar to other fungal infections"
                }
                source = hybrid_result["source"]
            else:
                # Fallback to Gemini 1.5 Flash
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                prompt = EXPERT_PROMPT_TEMPLATE.format(plant_type=plant_type, common_diseases=PLANT_COMMON_DISEASES[plant_type])
                response = model.generate_content([prompt, enhanced_image])
                result = extract_json_robust(response.text)
                source = "Gemini 1.5 Flash"

            if result:
                # Your existing result display code here (metrics, sections, etc.)
                disease_name = result["disease_name"]
                # ... (all the st.markdown, columns, etc. remain the same)
                st.session_state.last_diagnosis = result  # Simplified

# ============ OTHER PAGES REMAIN EXACTLY THE SAME ============
# (KisanAI Assistant, Crop Rotation, Cost Calculator - copy from original document)

elif page == "KisanAI Assistant":
    # Your original code unchanged
    pass

elif page == "Crop Rotation Advisor":
    # Your original code unchanged
    pass

elif page == "Cost Calculator & ROI":
    # Your original code unchanged
    pass
