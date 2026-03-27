import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re
import numpy as np
import torch
import torch.nn.functional as F

# ============ OPTIONAL CV2 FOR PREPROCESSING (fixes libGL error) ============
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# ============ HYBRID IMPORTS ============
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import timm
    VIT_AVAILABLE = True
except ImportError:
    VIT_AVAILABLE = False

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ TREATMENT COSTS & QUANTITIES DATABASE ============
TREATMENT_COSTS = {
    "organic": {
        "Cow Urine Extract": {"cost": 80, "quantity": "2-3 liters per 100 plants", "dilution": "1:5 with water"},
        "Sulfur Dust": {"cost": 120, "quantity": "500g per 100 plants", "dilution": "Direct dust - 5-10g per plant"},
        "Sulfur Powder": {"cost": 150, "quantity": "200g per 100 plants", "dilution": "3% suspension - 20ml per plant"},
        "Lime Sulfur": {"cost": 180, "quantity": "1 liter per 100 plants", "dilution": "1:10 with water"},
        "Neem Oil Spray": {"cost": 200, "quantity": "500ml per 100 plants", "dilution": "3% solution - 5ml per liter"},
        "Bordeaux Mixture": {"cost": 250, "quantity": "300g per 100 plants", "dilution": "1% solution - 10g per liter"},
        "Karanja Oil": {"cost": 220, "quantity": "400ml per 100 plants", "dilution": "2.5% solution - 2.5ml per liter"},
        "Copper Fungicide (Organic)": {"cost": 280, "quantity": "250g per 100 plants", "dilution": "0.5% solution - 5g per liter"},
        "Potassium Bicarbonate": {"cost": 300, "quantity": "150g per 100 plants", "dilution": "1% solution - 10g per liter"},
        "Bacillus subtilis": {"cost": 350, "quantity": "100g per 100 plants", "dilution": "0.1% solution - 1g per liter"},
        "Azadirachtin": {"cost": 380, "quantity": "200ml per 100 plants", "dilution": "0.3% solution - 3ml per liter"},
        "Trichoderma": {"cost": 400, "quantity": "500g per 100 plants", "dilution": "0.5% solution - 5g per liter"},
        "Spinosad": {"cost": 480, "quantity": "100ml per 100 plants", "dilution": "0.02% solution - 0.2ml per liter"},
    },
    "chemical": {
        "Carbendazim (Bavistin)": {"cost": 80, "quantity": "100g per 100 plants", "dilution": "0.1% solution - 1g per liter"},
        "Copper Oxychloride": {"cost": 100, "quantity": "200g per 100 plants", "dilution": "0.25% solution - 2.5g per liter"},
        "Mancozeb (Indofil)": {"cost": 140, "quantity": "150g per 100 plants", "dilution": "0.2% solution - 2g per liter"},
        "Profenofos (Meothrin)": {"cost": 150, "quantity": "100ml per 100 plants", "dilution": "0.05% solution - 0.5ml per liter"},
        "Chlorothalonil": {"cost": 180, "quantity": "120g per 100 plants", "dilution": "0.15% solution - 1.5g per liter"},
        "Deltamethrin (Decis)": {"cost": 200, "quantity": "50ml per 100 plants", "dilution": "0.005% solution - 0.05ml per liter"},
        "Imidacloprid (Confidor)": {"cost": 240, "quantity": "80ml per 100 plants", "dilution": "0.008% solution - 0.08ml per liter"},
        "Fluconazole (Contaf)": {"cost": 350, "quantity": "150ml per 100 plants", "dilution": "0.06% solution - 0.6ml per liter"},
        "Tebuconazole (Folicur)": {"cost": 320, "quantity": "120ml per 100 plants", "dilution": "0.05% solution - 0.5ml per liter"},
        "Thiamethoxam (Actara)": {"cost": 290, "quantity": "100g per 100 plants", "dilution": "0.04% solution - 0.4g per liter"},
        "Azoxystrobin (Amistar)": {"cost": 400, "quantity": "80ml per 100 plants", "dilution": "0.02% solution - 0.2ml per liter"},
        "Hexaconazole (Contaf Plus)": {"cost": 350, "quantity": "100ml per 100 plants", "dilution": "0.04% solution - 0.4ml per liter"},
        "Phosphorous Acid": {"cost": 250, "quantity": "200ml per 100 plants", "dilution": "0.3% solution - 3ml per liter"},
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

# ============ PLANT DISEASE CLASSES FOR ViT ============
PLANT_DISEASE_CLASSES = {
    0: "Apple - Apple Scab", 1: "Apple - Black Rot", 2: "Apple - Cedar Rust", 3: "Apple - Healthy",
    4: "Blueberry - Healthy", 5: "Cherry - Powdery Mildew", 6: "Cherry - Healthy",
    7: "Corn - Gray Leaf Spot", 8: "Corn - Common Rust", 9: "Corn - Northern Leaf Blight", 10: "Corn - Healthy",
    11: "Grape - Black Rot", 12: "Grape - Esca (Black Measles)", 13: "Grape - Leaf Blight", 14: "Grape - Healthy",
    15: "Orange - Huanglongbing (Citrus Greening)",
    16: "Peach - Bacterial Spot", 17: "Peach - Healthy",
    18: "Pepper - Bacterial Spot", 19: "Pepper - Healthy",
    20: "Potato - Early Blight", 21: "Potato - Late Blight", 22: "Potato - Healthy",
    23: "Raspberry - Healthy",
    24: "Soybean - Healthy",
    25: "Squash - Powdery Mildew",
    26: "Strawberry - Leaf Scorch", 27: "Strawberry - Healthy",
    28: "Tomato - Bacterial Spot", 29: "Tomato - Early Blight", 30: "Tomato - Late Blight",
    31: "Tomato - Leaf Mold", 32: "Tomato - Septoria Leaf Spot", 33: "Tomato - Spider Mites",
    34: "Tomato - Target Spot", 35: "Tomato - Mosaic Virus", 36: "Tomato - Yellow Leaf Curl Virus", 37: "Tomato - Healthy"
}

# ============ DISEASE KNOWLEDGE BASE ============
DISEASE_KNOWLEDGE_BASE = {
    "Apple - Apple Scab": {
        "type": "fungal",
        "symptoms": ["Brown lesions with velvety texture on leaves", "Dark brown spots on fruit surface", "Leaf curling and distortion", "Premature defoliation", "Lesions with concentric rings"],
        "causes": ["Venturia inaequalis fungus", "High humidity and wet conditions", "Contaminated fallen leaves", "Poor air circulation"],
        "immediate": ["Remove infected leaves and branches", "Improve air circulation around tree", "Avoid overhead watering", "Apply fungicide spray"],
        "organic": ["Sulfur Dust", "Bordeaux Mixture", "Lime Sulfur"],
        "chemical": ["Carbendazim (Bavistin)", "Mancozeb (Indofil)", "Copper Oxychloride"],
        "prevention": ["Prune branches to improve air flow", "Remove fallen leaves from ground", "Apply preventive fungicides before rainy season", "Use scab-resistant varieties"],
        "differential": ["Powdery Mildew: White powdery coating on leaves", "Cedar Rust: Orange pustules on fruit", "Black Rot: Concentric rings on fruit"],
        "notes": "Common in cool, wet climates. Most damaging at bloom stage.",
    },
    "Apple - Black Rot": {
        "type": "fungal",
        "symptoms": ["Large dark brown lesions with concentric rings on fruit", "White pustules in concentric circles", "Fruit rot and mummification", "Cankers on branches with dark borders"],
        "causes": ["Botryosphaeria obtusa fungus", "Damaged fruit providing entry points", "Pruning wounds on branches"],
        "immediate": ["Remove and destroy infected fruit", "Prune out cankers with 10 inches clearance", "Sanitize pruning tools", "Apply fungicide"],
        "organic": ["Neem Oil Spray", "Sulfur Powder", "Bordeaux Mixture"],
        "chemical": ["Mancozeb (Indofil)", "Copper Fungicide", "Carbendazim (Bavistin)"],
        "prevention": ["Remove mummified fruit from tree", "Avoid wounding fruit during harvest", "Improve fruit spacing for air circulation", "Apply dormant oil spray in winter"],
        "differential": ["Flyspeck: Small black spots without rings", "Sooty Blotch: Superficial dark coating"],
        "notes": "Often develops during storage. Infected fruit shows large lesions with rings.",
    },
    "Tomato - Early Blight": {
        "type": "fungal",
        "symptoms": ["Brown spots with concentric rings on lower leaves", "Target-like lesions starting on oldest leaves", "Yellow halo around brown spots", "Leaf yellowing and defoliation starting from bottom", "Lesions typically less than 1cm diameter"],
        "causes": ["Alternaria solani fungus", "Overhead watering and wet foliage", "Poor plant spacing and air circulation", "Soil splash from infected debris"],
        "immediate": ["Remove lower infected leaves (6-8 inches from soil)", "Avoid wetting foliage during irrigation", "Increase plant spacing", "Apply fungicide spray"],
        "organic": ["Sulfur Powder", "Bordeaux Mixture", "Neem Oil Spray"],
        "chemical": ["Mancozeb (Indofil)", "Carbendazim (Bavistin)", "Chlorothalonil"],
        "prevention": ["Mulch around base to prevent soil splash", "Stake plants for better air flow", "Remove lower leaves preemptively", "Avoid working in wet field", "Destroy crop residue after harvest"],
        "differential": ["Late Blight: Larger lesions, water-soaked appearance, white sporulation on underside", "Septoria Leaf Spot: Smaller spots with dark borders and gray center"],
        "notes": "Starts on lower leaves. Worse in warm, wet conditions. Can defoliate entire plant.",
    },
    "Tomato - Late Blight": {
        "type": "fungal",
        "symptoms": ["Large irregularly shaped water-soaked lesions on leaves", "White fuzzy growth on underside of infected leaves", "Rapid leaf wilting and collapse", "Fruit develops brown sunken lesions", "Entire plant can collapse in 3-5 days"],
        "causes": ["Phytophthora infestans oomycete", "Cool wet weather (50-70°F)", "High humidity and rainfall", "Contaminated seed or soil"],
        "immediate": ["Remove entire infected plant section", "Improve air circulation urgently", "Do not work in field when wet", "Apply fungicide immediately - cannot wait"],
        "organic": ["Bordeaux Mixture", "Lime Sulfur", "Copper Fungicide (Organic)"],
        "chemical": ["Metalaxyl-based fungicide", "Mancozeb (Indofil)", "Chlorothalonil"],
        "prevention": ["Use resistant varieties if possible", "Avoid planting near potato fields", "Remove volunteer potatoes near field", "Proper spacing and pruning", "Destroy all infected plant material"],
        "differential": ["Early Blight: Concentric ring pattern, starts on lower leaves", "Leaf Mold: Yellow patches with dark undersides on older leaves only"],
        "notes": "Most destructive tomato disease. Requires aggressive management. Spreads very rapidly in cool wet weather.",
    },
    "Pepper - Anthracnose": {
        "type": "fungal",
        "symptoms": ["Small circular spots on leaves and fruit", "Dark brown/black lesions with reddish border", "Pink or orange spore masses in center of lesion (wet conditions)", "Fruit becomes unmarketable", "Leaf spotting and premature defoliation"],
        "causes": ["Colletotrichum species fungus", "High temperature and humidity", "Overhead watering", "Contaminated seed"],
        "immediate": ["Remove infected leaves and fruit", "Reduce humidity by pruning", "Avoid overhead watering", "Apply fungicide"],
        "organic": ["Sulfur Powder", "Bordeaux Mixture", "Trichoderma"],
        "chemical": ["Carbendazim (Bavistin)", "Mancozeb (Indofil)", "Hexaconazole (Contaf Plus)"],
        "prevention": ["Use disease-free seed", "Space plants properly for air flow", "Drip irrigation instead of overhead", "Remove fallen infected fruit", "Clean up crop residue"],
        "differential": ["Bacterial Spot: Angular lesions with yellow halo", "Phytophthora Blight: Large water-soaked lesions, white sporulation"],
        "notes": "Most problematic in warm humid climate. Worst in rainy season.",
    },
    "Grape - Powdery Mildew": {
        "type": "fungal",
        "symptoms": ["White powdery coating on leaves, stems and fruit", "Leaves become distorted and curl", "Berry splitting and cracking", "Berries develop distinctive frosted appearance", "Powdery coating wipes off easily"],
        "causes": ["Uncinula necator fungus", "Moderate temperature (70-80°F)", "High humidity but dry foliage", "Dense grape foliage"],
        "immediate": ["Remove heavily infected leaves", "Prune to improve air circulation", "Avoid overhead watering", "Apply sulfur-based fungicide"],
        "organic": ["Sulfur Powder", "Sulfur Dust", "Potassium Bicarbonate"],
        "chemical": ["Hexaconazole (Contaf Plus)", "Tebuconazole (Folicur)", "Azoxystrobin (Amistar)"],
        "prevention": ["Plant resistant varieties", "Maintain open canopy through pruning", "Avoid excessive nitrogen fertilizer", "Apply preventive sprays before disease appears"],
        "differential": ["Downy Mildew: Yellow patches on upper leaf, white sporulation on underside", "Black Rot: Brown lesions with concentric rings on fruit"],
        "notes": "Appears early in season. Easier to prevent than cure. Sulfur is very effective.",
    },
    "Potato - Late Blight": {
        "type": "fungal",
        "symptoms": ["Water-soaked spots on leaves and stems", "White mold on underside of leaves", "Rapid leaf collapse and death", "Brown lesions develop on potato tubers", "Wet rot smell from infected tubers", "Entire plant death in 1-2 weeks"],
        "causes": ["Phytophthora infestans oomycete", "Cool wet weather (50-65°F)", "High humidity and rainfall", "Infected seed potatoes"],
        "immediate": ["Remove and destroy entire plant", "Do not harvest from infected field for 2 weeks", "Do not work in field when wet", "Apply fungicide if plants still living"],
        "organic": ["Bordeaux Mixture", "Lime Sulfur", "Copper Fungicide (Organic)"],
        "chemical": ["Metalaxyl fungicide", "Mancozeb (Indofil)", "Chlorothalonil"],
        "prevention": ["Use certified disease-free seed", "Improve drainage in field", "Avoid planting in low areas", "Hill up soil to prevent tuber exposure"],
        "differential": ["Early Blight: Targets lesions on older leaves, doesn't cause rapid collapse", "Vertical Wilt: Yellowing of vascular tissues"],
        "notes": "Most damaging disease. Requires very aggressive management. Can destroy entire crop in wet season.",
    }
}

# ============ GLOBAL STYLES ============
st.markdown("""
<style>
    /* Your full CSS styles from the original code - kept unchanged */
    * { margin: 0; padding: 0; }
    .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); color: #e4e6eb; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
    /* ... (all other CSS rules from your original file) ... */
</style>
""", unsafe_allow_html=True)

# ============ GEMINI CONFIG ============
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    st.error("GEMINI_API_KEY not found in environment variables!")
    st.stop()

# ============ PROMPTS ============
EXPERT_PROMPT_TEMPLATE = """You are an elite plant pathologist..."""  # (your full prompt - kept as original)

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
def preprocess_image_for_detection(image):
    if not CV2_AVAILABLE:
        return np.array(image)
    try:
        img_array = np.array(image)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced_lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        return enhanced
    except:
        return np.array(image)

def get_treatment_info(treatment_type, treatment_name):
    costs = TREATMENT_COSTS.get(treatment_type, {})
    for key, value in costs.items():
        if key.lower() == treatment_name.lower():
            return value if isinstance(value, dict) else {"cost": value, "quantity": "As per package", "dilution": "Follow label instructions"}
    for key, value in costs.items():
        if key.lower() in treatment_name.lower() or treatment_name.lower() in key.lower():
            return value if isinstance(value, dict) else {"cost": value, "quantity": "As per package", "dilution": "Follow label instructions"}
    return {"cost": 300 if treatment_type == "organic" else 250, "quantity": "As per package", "dilution": "Follow label instructions"}

def get_type_badge_class(disease_type):
    t = disease_type.lower() if disease_type else "healthy"
    if "fungal" in t: return "type-fungal"
    elif "bacterial" in t: return "type-bacterial"
    elif "viral" in t: return "type-viral"
    elif "pest" in t: return "type-pest"
    elif "nutrient" in t: return "type-nutrient"
    return "type-healthy"

def get_severity_badge_class(severity):
    s = severity.lower() if severity else "moderate"
    if "healthy" in s: return "severity-healthy"
    elif "mild" in s: return "severity-mild"
    elif "moderate" in s: return "severity-moderate"
    elif "severe" in s: return "severity-severe"
    return "severity-moderate"

# ... (load_yolo_model, load_vit_model, predict_hybrid, convert_hybrid_to_diagnosis, generate_crop_rotation_plan, get_farmer_bot_response - keep your original implementations)

# ====================== DISPLAY FULL DIAGNOSIS (TOTAL COST LINES REMOVED) ======================
def display_full_diagnosis(diag):
    if not diag or "result" not in diag:
        return
    result = diag["result"]
    plant_type = diag.get("plant_type")
    disease_name = result.get("disease_name", "Unknown")
    disease_type = result.get("disease_type", "unknown")
    severity = result.get("severity", "unknown")
    confidence = result.get("confidence", 0)

    severity_class = get_severity_badge_class(severity)
    type_class = get_type_badge_class(disease_type)

    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    st.markdown(f"""<div class="disease-header"><div class="disease-name">{disease_name}</div><div class="disease-meta"><span class="severity-badge {severity_class}">{severity.title()}</span><span class="type-badge {type_class}">{disease_type.title()}</span></div></div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Plant", plant_type)
    with col2: st.metric("Confidence", f"{confidence}%")
    with col3: st.metric("Severity", severity.title())

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("""<div class="info-section"><div class="info-title">Symptoms</div>""", unsafe_allow_html=True)
        for symptom in result.get("symptoms", []):
            st.write(f"• {symptom}")
        st.markdown("</div>", unsafe_allow_html=True)
        if result.get("differential_diagnosis"):
            st.markdown("""<div class="info-section"><div class="info-title">Other Possibilities</div>""", unsafe_allow_html=True)
            for d in result.get("differential_diagnosis", []):
                st.write(f"• {d}")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""<div class="info-section"><div class="info-title">Causes</div>""", unsafe_allow_html=True)
        for cause in result.get("probable_causes", []):
            st.write(f"• {cause}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""<div class="info-section"><div class="info-title">Immediate Actions</div>""", unsafe_allow_html=True)
        for i, action in enumerate(result.get("immediate_action", []), 1):
            st.write(f"**{i}.** {action}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Organic & Chemical Treatments - TOTAL COST LINES REMOVED
    col_treat1, col_treat2 = st.columns(2)
    with col_treat1:
        st.markdown("""<div class="info-section"><div class="info-title">Organic Treatments</div>""", unsafe_allow_html=True)
        for treatment in result.get("organic_treatments", []):
            name = treatment.split(" - ")[0] if " - " in treatment else treatment.split(":")[0]
            info = get_treatment_info("organic", name)
            st.markdown(f"""<div class="treatment-item"><div class="treatment-name">💊 {name}</div><div class="treatment-quantity">Quantity: {info.get("quantity")}</div><div class="treatment-dilution">Dilution: {info.get("dilution")}</div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_treat2:
        st.markdown("""<div class="info-section"><div class="info-title">Chemical Treatments</div>""", unsafe_allow_html=True)
        for treatment in result.get("chemical_treatments", []):
            name = treatment.split(" - ")[0] if " - " in treatment else treatment.split(":")[0]
            info = get_treatment_info("chemical", name)
            st.markdown(f"""<div class="treatment-item"><div class="treatment-name">⚗️ {name}</div><div class="treatment-quantity">Quantity: {info.get("quantity")}</div><div class="treatment-dilution">Dilution: {info.get("dilution")}</div></div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""<div class="info-section"><div class="info-title">Prevention</div>""", unsafe_allow_html=True)
    for tip in result.get("prevention_long_term", []):
        st.write(f"• {tip}")
    st.markdown("</div>", unsafe_allow_html=True)

    if result.get("plant_specific_notes"):
        st.markdown(f"""<div class="info-section"><div class="info-title">{plant_type} Care Notes</div>{result.get("plant_specific_notes")}</div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ============ MAIN APP ============
st.markdown("""<div class="header-container"><div class="header-title">🌿 AI Plant Doctor - Smart Edition</div></div>""", unsafe_allow_html=True)

with st.sidebar:
    page = st.radio("📂 Pages", ["AI Plant Doctor", "KisanAI Assistant", "Crop Rotation Advisor", "Cost Calculator & ROI"])
    # ... (your full sidebar code with settings, model choice, supported plants, etc.)

if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None

if page == "AI Plant Doctor":
    # Plant selection and image upload (your original code)
    col_plant, col_upload = st.columns([1, 2])
    # ... (plant type selectbox, custom plant input, uploaded_files uploader)

    if uploaded_files and len(uploaded_files) > 0 and plant_type and plant_type != "Select a plant...":
        # ... (your full analysis logic with Gemini or Hybrid)

        if result:
            st.session_state.last_diagnosis = {
                "plant_type": plant_type,
                "disease_name": disease_name,
                "disease_type": disease_type,
                "severity": severity,
                "confidence": confidence,
                "organic_cost": 0,
                "chemical_cost": 0,
                "infected_count": 10,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            display_full_diagnosis(st.session_state.last_diagnosis)

            # Treatment selector
            st.markdown("---")
            st.subheader("🛠️ Finalize Treatment Plan")
            infected_count = st.number_input("Number of infected plants/trees", value=10, min_value=1, step=1)
            # organic_options and chemical_options extraction + selectboxes + button (your code)
            # ... 

    elif st.session_state.last_diagnosis:
        st.markdown("""<div class="success-box">✅ Previous diagnosis loaded. Full result is shown below.</div>""", unsafe_allow_html=True)
        display_full_diagnosis(st.session_state.last_diagnosis)

elif page == "KisanAI Assistant":
    # your full KisanAI code

elif page == "Crop Rotation Advisor":
    # your full Crop Rotation code

else:  # Cost Calculator & ROI
    st.markdown("""<div class="page-header"><div class="page-title">💰 Cost Calculator & ROI Analysis</div></div>""", unsafe_allow_html=True)
    diag = st.session_state.last_diagnosis
    if not diag:
        st.markdown("""<div class="warning-box">No diagnosis data found. Run AI Plant Doctor first.</div>""", unsafe_allow_html=True)
    else:
        organic_cost_total = diag.get("organic_cost", 0)
        chemical_cost_total = diag.get("chemical_cost", 0)
        infected_count = diag.get("infected_count", 10)
        # your full ROI calculation and display code here
