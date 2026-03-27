import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ TREATMENT COSTS & QUANTITIES DATABASE ============

TREATMENT_COSTS = {
    "organic": {
        "Cow Urine Extract": {
            "cost": 80,
            "quantity": "2-3 liters per 100 plants",
            "dilution": "1:5 with water",
        },
        "Sulfur Dust": {
            "cost": 120,
            "quantity": "500g per 100 plants",
            "dilution": "Direct dust - 5-10g per plant",
        },
        "Sulfur Powder": {
            "cost": 150,
            "quantity": "200g per 100 plants",
            "dilution": "3% suspension - 20ml per plant",
        },
        "Lime Sulfur": {
            "cost": 180,
            "quantity": "1 liter per 100 plants",
            "dilution": "1:10 with water",
        },
        "Neem Oil Spray": {
            "cost": 250,
            "quantity": "500ml per 100 plants",
            "dilution": "3% solution - 5ml per liter",
        },
        "Bordeaux Mixture": {
            "cost": 250,
            "quantity": "300g per 100 plants",
            "dilution": "1% solution - 10g per liter",
        },
        "Karanja Oil": {
            "cost": 220,
            "quantity": "400ml per 100 plants",
            "dilution": "2.5% solution - 2.5ml per liter",
        },
        "Copper Fungicide (Organic)": {
            "cost": 280,
            "quantity": "250g per 100 plants",
            "dilution": "0.5% solution - 5g per liter",
        },
        "Potassium Bicarbonate": {
            "cost": 300,
            "quantity": "150g per 100 plants",
            "dilution": "1% solution - 10g per liter",
        },
        "Bacillus subtilis": {
            "cost": 350,
            "quantity": "100g per 100 plants",
            "dilution": "0.1% solution - 1g per liter",
        },
        "Azadirachtin": {
            "cost": 380,
            "quantity": "200ml per 100 plants",
            "dilution": "0.3% solution - 3ml per liter",
        },
        "Trichoderma": {
            "cost": 400,
            "quantity": "500g per 100 plants",
            "dilution": "0.5% solution - 5g per liter",
        },
        "Spinosad": {
            "cost": 2000,
            "quantity": "100ml per 100 plants",
            "dilution": "0.02% solution - 0.2ml per liter",
        },
        "Seaweed Extract": {
            "cost": 260,
            "quantity": "250ml per 100 plants",
            "dilution": "0.3% solution - 3ml per liter",
        },
    },
    "chemical": {
        "Carbendazim (Bavistin)": {
            "cost": 120,
            "quantity": "100g per 100 plants",
            "dilution": "0.1% solution - 1g per liter",
        },
        "Mancozeb (Indofil)": {
            "cost": 120,
            "quantity": "150g per 100 plants",
            "dilution": "0.2% solution - 2g per liter",
        },
        "Copper Oxychloride": {
            "cost": 150,
            "quantity": "200g per 100 plants",
            "dilution": "0.25% solution - 2.5g per liter",
        },
        "Profenofos (Meothrin)": {
            "cost": 200,
            "quantity": "100ml per 100 plants",
            "dilution": "0.05% solution - 0.5ml per liter",
        },
        "Chlorothalonil": {
            "cost": 220,
            "quantity": "120g per 100 plants",
            "dilution": "0.15% solution - 1.5g per liter",
        },
        "Deltamethrin (Decis)": {
            "cost": 220,
            "quantity": "50ml per 100 plants",
            "dilution": "0.005% solution - 0.05ml per liter",
        },
        "Imidacloprid (Confidor)": {
            "cost": 350,
            "quantity": "80ml per 100 plants",
            "dilution": "0.008% solution - 0.08ml per liter",
        },
        "Fluconazole (Contaf)": {
            "cost": 350,
            "quantity": "150ml per 100 plants",
            "dilution": "0.06% solution - 0.6ml per liter",
        },
        "Tebuconazole (Folicur)": {
            "cost": 320,
            "quantity": "120ml per 100 plants",
            "dilution": "0.05% solution - 0.5ml per liter",
        },
        "Thiamethoxam (Actara)": {
            "cost": 290,
            "quantity": "100g per 100 plants",
            "dilution": "0.04% solution - 0.4g per liter",
        },
        "Azoxystrobin (Amistar)": {
            "cost": 650,
            "quantity": "80ml per 100 plants",
            "dilution": "0.02% solution - 0.2ml per liter",
        },
        "Hexaconazole (Contaf Plus)": {
            "cost": 350,
            "quantity": "100ml per 100 plants",
            "dilution": "0.04% solution - 0.4ml per liter",
        },
        "Phosphorous Acid": {
            "cost": 250,
            "quantity": "200ml per 100 plants",
            "dilution": "0.3% solution - 3ml per liter",
        },
        "Metalaxyl + Mancozeb (Ridomil Gold)": {
            "cost": 190,
            "quantity": "100g per 100 plants",
            "dilution": "0.25% solution - 2.5g per liter",
        },
        "Propiconazole (Tilt)": {
            "cost": 190,
            "quantity": "100ml per 100 plants",
            "dilution": "0.1% solution - 1ml per liter",
        },
    },
}

# ============ CROP ROTATION DATABASE ============

CROP_ROTATION_DATA = {
    "Tomato": {
        "rotations": ["Beans", "Cabbage", "Cucumber"],
        "info": {
            "Tomato": "High-value solanaceae crop. Susceptible to early/late blight, fusarium wilt, and bacterial diseases. Benefits from crop rotation of 3+ years.",
            "Beans": "Nitrogen-fixing legume. Improves soil nitrogen content. Breaks disease cycle for tomato. Compatible with tomato crop rotation.",
            "Cabbage": "Brassica family. Helps control tomato diseases. Requires different nutrient profile. Good rotation choice.",
            "Cucumber": "Cucurbitaceae family. No common diseases with tomato. Light feeder after beans. Completes rotation cycle.",
        },
    },
    "Rose": {
        "rotations": ["Marigold", "Chrysanthemum", "Herbs"],
        "info": {
            "Rose": "Ornamental crop. Susceptible to black spot, powdery mildew, rose rosette virus. Needs disease break.",
            "Marigold": "Natural pest repellent. Flowers attract beneficial insects. Cleanses soil. Excellent companion.",
            "Chrysanthemum": "Different pest/disease profile. Breaks rose pathogen cycle. Similar care requirements.",
            "Herbs": "Basil, rosemary improve soil health. Aromatics confuse rose pests. Reduces chemical inputs.",
        },
    },
    "Apple": {
        "rotations": ["Legume Cover Crops", "Grasses", "Berries"],
        "info": {
            "Apple": "Long-term perennial crop. Susceptible to apple scab, fire blight, rust. Needs 4-5 year rotation minimum.",
            "Legume Cover Crops": "Nitrogen fixation. Soil improvement. Breaks pathogen cycle. Reduces input costs.",
            "Grasses": "Erosion control. Soil structure improvement. Natural pest predator habitat. Beneficial insects.",
            "Berries": "Different root depth. Utilize different nutrients. Continues income during apple off-year.",
        },
    },
    "Lettuce": {
        "rotations": ["Spinach", "Broccoli", "Cauliflower"],
        "info": {
            "Lettuce": "Cool-season leafy crop. Susceptible to downy mildew, tip burn, mosaic virus. Quick 60-70 day cycle.",
            "Spinach": "Similar family (Amaranthaceae). Resistant to lettuce diseases. Tolerates cold. Soil enrichment.",
            "Broccoli": "Brassica family. Different pest profile. Breaks disease cycle. Heavy feeder needs composting.",
            "Cauliflower": "Brassica family. Follows spinach. Light-sensitive. Completes 3-crop cycle for lettuce disease control.",
        },
    },
    "Grape": {
        "rotations": ["Legume Cover Crops", "Cereals", "Vegetables"],
        "info": {
            "Grape": "Perennial vine crop. Powdery mildew, downy mildew, phylloxera major concerns. 5+ year rotation needed.",
            "Legume Cover Crops": "Nitrogen replenishment. Soil structure restoration. Disease vector elimination.",
            "Cereals": "Wheat/maize. Different nutrient uptake. Soil consolidation. Nematode cycle break.",
            "Vegetables": "Diverse crops reduce soil depletion. Polyculture benefits. Re-establishes soil microbiology.",
        },
    },
    "Pepper": {
        "rotations": ["Onion", "Garlic", "Spinach"],
        "info": {
            "Pepper": "Solanaceae crop. Anthracnose, bacterial wilt, phytophthora major issues. 3-year rotation essential.",
            "Onion": "Allium family. Different disease profile. Fungicide applications reduced. Breaks solanaceae cycle.",
            "Garlic": "Allium family. Natural pest deterrent. Soil antimicrobial properties. Autumn/winter crop.",
            "Spinach": "Cool-season crop. No common pepper diseases. Nitrogen-fixing partners. Spring/fall compatible.",
        },
    },
    "Cucumber": {
        "rotations": ["Maize", "Okra", "Legumes"],
        "info": {
            "Cucumber": "Cucurbitaceae family. Powdery mildew, downy mildew, beetle damage. 2-3 year rotation suggested.",
            "Maize": "Tall crop provides shade break. Different root system. Utilizes soil nitrogen. Strong market demand.",
            "Okra": "Malvaceae family. No overlapping pests. Nitrogen-fixing tendency. Heat-tolerant summer crop.",
            "Legumes": "Nitrogen restoration. Disease-free break for cucumber. Pea/bean varieties available for season.",
        },
    },
    "Strawberry": {
        "rotations": ["Garlic", "Onion", "Leafy Greens"],
        "info": {
            "Strawberry": "Low-growing perennial. Leaf scorch, powdery mildew, red stele root rot issues. 3-year bed rotation.",
            "Garlic": "Deep-rooted. Antimicrobial soil activity. Plant autumn, harvest spring. Excellent succession crop.",
            "Onion": "Bulb crop. Disease-free break. Allergenic properties deter strawberry pests. Rotation crop.",
            "Leafy Greens": "Spinach/lettuce. Quick cycle. Utilizes residual nutrients. Spring/fall timing options.",
        },
    },
    "Corn": {
        "rotations": ["Soybean", "Pulses", "Oilseeds"],
        "info": {
            "Corn": "Heavy nitrogen feeder. Leaf blotch, rust, corn borer, fumonisin concerns. 3+ year rotation critical.",
            "Soybean": "Nitrogen-fixing legume. Reduces fertilizer needs 40-50%. Breaks corn pest cycle naturally.",
            "Pulses": "Chickpea/lentil. Additional nitrogen fixation. High market value. Diverse pest profile than corn.",
            "Oilseeds": "Sunflower/safflower. Soil structure improvement. Different nutrient uptake. Income diversification.",
        },
    },
    "Potato": {
        "rotations": ["Peas", "Mustard", "Cereals"],
        "info": {
            "Potato": "Solanaceae crop. Late blight, early blight, nematodes persistent issue. 4-year rotation required.",
            "Peas": "Nitrogen-fixing legume. Cold-season crop. Breaks potato pathogen cycle. Soil health restoration.",
            "Mustard": "Oil crop. Biofumigation properties. Natural nematode control. Green manure if plowed.",
            "Cereals": "Wheat/barley. Different root depth. Soil consolidation. Completes disease-break rotation cycle.",
        },
    },
}

REGIONS = ["North India", "South India", "East India", "West India", "Central India"]
SOIL_TYPES = ["Black Soil", "Red Soil", "Laterite Soil", "Alluvial Soil", "Clay Soil"]
MARKET_FOCUS = ["Stable essentials", "High-value cash crops", "Low input / low risk"]

# ============ GLOBAL STYLES ============

st.markdown(
    """
<style>
    * { margin: 0; padding: 0; }
    .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); color: #e4e6eb; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
    p, span, div, label { color: #e4e6eb; font-size: 1.1rem; }
    .header-container { background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%); padding: 40px 20px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); border: 1px solid rgba(102, 126, 234, 0.3); }
    .header-title { font-size: 3rem; font-weight: 700; color: #ffffff; text-align: center; margin-bottom: 10px; letter-spacing: 1px; }
    .header-subtitle { font-size: 1.4rem; color: #b0c4ff; text-align: center; }
    .feature-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; border-radius: 10px; text-align: center; font-weight: 600; font-size: 1.1rem; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5); transition: transform 0.3s ease; border: 1px solid rgba(255, 255, 255, 0.1); }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.7); }
    .upload-container { background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%); padding: 30px; border-radius: 15px; border: 2px dashed #667eea; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4); margin: 20px 0; }
    .result-container { background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%); border-radius: 15px; padding: 30px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); margin: 20px 0; border: 1px solid rgba(102, 126, 234, 0.2); }
    .disease-header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 20px rgba(245, 87, 108, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); }
    .disease-name { font-size: 2.8rem; font-weight: 700; margin-bottom: 15px; }
    .disease-meta { font-size: 1.1rem; opacity: 0.95; display: flex; gap: 20px; flex-wrap: wrap; }
    .info-section { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 5px solid #667eea; padding: 20px; border-radius: 8px; margin: 15px 0; border: 1px solid rgba(102, 126, 234, 0.2); }
    .info-title { font-size: 1.4rem; font-weight: 700; color: #b0c4ff; margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }
    .cost-info { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 5px solid #667eea; padding: 12px 16px; border-radius: 6px; margin: 12px 0; font-size: 1rem; color: #b0c4ff; font-weight: 600; }
    .treatment-item { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 5px solid #667eea; padding: 15px; border-radius: 6px; margin: 12px 0; font-size: 0.95rem; color: #b0c4ff; }
    .treatment-name { font-weight: 700; color: #ffffff; margin-bottom: 5px; }
    .treatment-quantity { color: #81c784; font-weight: 600; margin: 5px 0; }
    .treatment-dilution { color: #ffcc80; font-size: 0.9rem; margin: 5px 0; }
    .severity-badge { display: inline-block; padding: 10px 18px; border-radius: 20px; font-weight: 600; font-size: 1rem; }
    .severity-healthy { background-color: #1b5e20; color: #4caf50; }
    .severity-mild { background-color: #004d73; color: #4dd0e1; }
    .severity-moderate { background-color: #633d00; color: #ffc107; }
    .severity-severe { background-color: #5a1a1a; color: #ff6b6b; }
    .type-badge { display: inline-block; padding: 8px 14px; border-radius: 15px; font-weight: 600; font-size: 0.95rem; margin: 5px 5px 5px 0; }
    .type-fungal { background-color: #4a148c; color: #ce93d8; }
    .type-bacterial { background-color: #0d47a1; color: #64b5f6; }
    .type-viral { background-color: #5c0b0b; color: #ef9a9a; }
    .type-pest { background-color: #4d2600; color: #ffcc80; }
    .type-nutrient { background-color: #0d3a1a; color: #81c784; }
    .type-healthy { background-color: #0d3a1a; color: #81c784; }
    .debug-box { background: #0f1419; border: 1px solid #667eea; border-radius: 8px; padding: 15px; margin: 10px 0; font-family: monospace; font-size: 0.95rem; max-height: 400px; overflow-y: auto; color: #b0c4ff; white-space: pre-wrap; }
    .warning-box { background: linear-gradient(135deg, #4d2600 0%, #3d2000 100%); border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin: 10px 0; color: #ffcc80; font-size: 1.1rem; }
    .success-box { background: linear-gradient(135deg, #1b5e20 0%, #0d3a1a 100%); border: 1px solid #4caf50; border-radius: 8px; padding: 15px; margin: 10px 0; color: #81c784; font-size: 1.1rem; }
    .error-box { background: linear-gradient(135deg, #5a1a1a 0%, #3d0d0d 100%); border: 1px solid #ff6b6b; border-radius: 8px; padding: 15px; margin: 10px 0; color: #ef9a9a; font-size: 1.1rem; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; padding: 12px 30px !important; font-weight: 600 !important; font-size: 1.1rem !important; border-radius: 8px !important; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important; }
    .image-container { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); border: 1px solid rgba(102, 126, 234, 0.2); }
    .tips-card { background: linear-gradient(135deg, #1a2a47 0%, #2d3050 100%); border: 2px solid #667eea; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .tips-card-title { font-weight: 700; color: #b0c4ff; margin-bottom: 10px; font-size: 1.2rem; }
    [data-testid="stSidebar"] { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
    [data-testid="metric-container"] { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 8px; }
    [data-testid="stExpander"] { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border: 1px solid rgba(102, 126, 234, 0.2); }
    .streamlit-expanderHeader { color: #b0c4ff !important; font-size: 1.1rem !important; }
    input, textarea, select { background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%) !important; border: 1px solid rgba(102, 126, 234, 0.3) !important; color: #e4e6eb !important; font-size: 1.1rem !important; }
    h2, h3, h4 { font-size: 1.4rem !important; color: #b0c4ff !important; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0f1419; }
    ::-webkit-scrollbar-thumb { background: #667eea; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #764ba2; }
    .chatbot-container { background: linear-gradient(135deg, #1a2a47 0%, #2d3050 100%); border: 2px solid #667eea; border-radius: 12px; padding: 15px; margin: 15px 0; max-height: 500px; overflow-y: auto; }
    .chat-message { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 4px solid #667eea; padding: 12px; margin: 8px 0; border-radius: 8px; font-size: 0.95rem; }
    .page-header { background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%); padding: 30px 20px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); border: 1px solid rgba(102, 126, 234, 0.3); }
    .page-title { font-size: 2.5rem; font-weight: 700; color: #ffffff; text-align: center; letter-spacing: 1px; }
    .page-subtitle { font-size: 1.2rem; color: #b0c4ff; text-align: center; margin-top: 10px; }
    .stat-box { background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border: 2px solid #667eea; border-radius: 12px; padding: 20px; margin: 10px 0; text-align: center; }
    .stat-value { font-size: 2rem; font-weight: 700; color: #667eea; margin: 10px 0; }
    .stat-label { font-size: 1rem; color: #b0c4ff; }
    .rotation-card { background: linear-gradient(135deg, #2d4a7a15 0%, #667eea15 100%); border: 2px solid rgba(102, 126, 234, 0.4); border-radius: 12px; padding: 20px; margin: 15px 0; }
    .rotation-year { font-size: 1.3rem; font-weight: 700; color: #667eea; margin-bottom: 10px; }
    .crop-name { font-size: 1.3rem; font-weight: 600; color: #667eea; margin: 10px 0; }
    .crop-description { font-size: 0.95rem; color: #b0c4ff; margin-top: 10px; line-height: 1.6; }
    .kisan-response-box { background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); border: 3px solid #667eea; border-radius: 15px; padding: 25px; margin: 20px 0; font-size: 1.25rem; line-height: 1.8; color: #b0c4ff; font-weight: 500; }
</style>
""",
    unsafe_allow_html=True,
)

# ============ GEMINI CONFIG ============

try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    st.error("GEMINI_API_KEY not found in environment variables!")
    st.stop()

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
{
  "plant_species": "{plant_type}",
  "disease_name": "Specific disease name or Unable to diagnose",
  "disease_type": "fungal/bacterial/viral/pest/nutrient/environmental/healthy",
  "severity": "healthy/mild/moderate/severe",
  "confidence": 85,
  "confidence_reason": "Detailed explanation specific to {plant_type}",
  "image_quality": "Excellent/Good/Fair/Poor - explanation",
  "symptoms": ["Specific symptom seen in {plant_type}", "Secondary symptom", "Tertiary symptom if present"],
  "differential_diagnosis": ["Disease A (common in {plant_type}): Why it might be this", "Disease B (common in {plant_type}): Why it might be this", "Disease C: Why this is unlikely for {plant_type}"],
  "probable_causes": ["Primary cause relevant to {plant_type}", "Secondary cause", "Environmental factor"],
  "immediate_action": ["Action 1: Specific to {plant_type}", "Action 2: Specific to {plant_type}", "Action 3: Specific to {plant_type}"],
  "organic_treatments": ["Treatment 1: Product and application for {plant_type}", "Treatment 2: Alternative for {plant_type}"],
  "chemical_treatments": [
    "Chemical 1: Safe for {plant_type} with dilution",
    "Chemical 2: Alternative safe for {plant_type}"
  ],
  "prevention_long_term": ["Prevention strategy 1 for {plant_type}", "Prevention strategy 2 for {plant_type}", "Resistant varieties: If available for {plant_type}"],
  "plant_specific_notes": "Important notes specific to {plant_type} care and disease management",
  "similar_conditions": "Other {plant_type} conditions that look similar"
}
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
    severity_lower = severity.lower() if severity else "moderate"
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
    costs = TREATMENT_COSTS.get(treatment_type, {})
    treatment_name_lower = treatment_name.lower()
    for key, value in costs.items():
        if key.lower() == treatment_name_lower:
            return value["cost"] if isinstance(value, dict) else value
    for key, value in costs.items():
        if key.lower() in treatment_name_lower or treatment_name_lower in key.lower():
            return value["cost"] if isinstance(value, dict) else value
    return 300 if treatment_type == "organic" else 250


def get_treatment_info(treatment_type, treatment_name):
    costs = TREATMENT_COSTS.get(treatment_type, {})
    for key, value in costs.items():
        if key.lower() == treatment_name.lower():
            if isinstance(value, dict):
                return value
            return {
                "cost": value,
                "quantity": "As per package",
                "dilution": "Follow label instructions",
            }
    for key, value in costs.items():
        if key.lower() in treatment_name.lower() or treatment_name.lower() in key.lower():
            if isinstance(value, dict):
                return value
            return {
                "cost": value,
                "quantity": "As per package",
                "dilution": "Follow label instructions",
            }
    return {
        "cost": 300 if treatment_type == "organic" else 250,
        "quantity": "As per package",
        "dilution": "Follow label instructions",
    }


def normalize_treatment_name(raw_name: str) -> str:
    if not isinstance(raw_name, str):
        return ""
    name = raw_name.strip()
    if " - " in name:
        name = name.split(" - ", 1)[0].strip()
    if ":" in name:
        name = name.split(":", 1)[0].strip()
    return name


def render_treatment_selection_ui(
    plant_type: str,
    disease_name: str,
    organic_treatments,
    chemical_treatments,
    default_infected_count: int,
):
    st.markdown(
        """<div class="info-section"><div class="info-title">Setup Cost Calculator & ROI</div></div>""",
        unsafe_allow_html=True,
    )

    default_n = max(int(default_infected_count or 1), 1)
    infected_plants = st.number_input(
        "Number of infected plants you want to treat (for cost & ROI)",
        min_value=1,
        step=1,
        value=default_n,
        key="cost_calc_infected_plants",
    )

    organic_names = [
        normalize_treatment_name(t)
        for t in (organic_treatments or [])
        if isinstance(t, str)
    ]
    chemical_names = [
        normalize_treatment_name(t)
        for t in (chemical_treatments or [])
        if isinstance(t, str)
    ]

    st.markdown(
        "<br><div class='info-section'><div class='info-title'>Select Treatment for Cost Calculation</div></div>",
        unsafe_allow_html=True,
    )

    treatment_type_choice = st.radio(
        "Which treatment will you actually use?",
        ["Organic", "Chemical"],
        horizontal=True,
        key="cost_calc_treatment_type",
    )
    selected_type_key = "organic" if treatment_type_choice == "Organic" else "chemical"

    if selected_type_key == "organic":
        if not organic_names:
            st.warning(
                "No organic treatments were suggested. "
                "You can still enter custom costs on the Cost Calculator page."
            )
            st.session_state.treatment_selection = None
            return
        selected_name = st.selectbox(
            "Select organic treatment (from AI suggestions)",
            organic_names,
            key="cost_calc_selected_organic_treatment",
        )
    else:
        if not chemical_names:
            st.warning(
                "No chemical treatments were suggested. "
                "You can still enter custom costs on the Cost Calculator page."
            )
            st.session_state.treatment_selection = None
            return
        selected_name = st.selectbox(
            "Select chemical treatment (from AI suggestions)",
            chemical_names,
            key="cost_calc_selected_chemical_treatment",
        )

    info = get_treatment_info(selected_type_key, selected_name)
    unit_cost = info.get("cost", 0)
    quantity = info.get("quantity", "As per package")

    base_plants = 100
    if infected_plants <= base_plants:
        total_cost = int(round(unit_cost))
    else:
        total_cost = int(round(unit_cost * infected_plants / base_plants))

    st.session_state.treatment_selection = {
        "plant_type": plant_type,
        "disease_name": disease_name,
        "treatment_type": selected_type_key,
        "treatment_name": selected_name,
        "infected_plants": infected_plants,
        "unit_cost": unit_cost,
        "base_plants": base_plants,
        "total_cost": total_cost,
        "quantity": quantity,
    }

    st.markdown(
        f"""
        <div class="cost-info" style="margin-top: 10px;">
            Selected: <b>{selected_name}</b> ({treatment_type_choice})<br>
            Quantity guideline: {quantity}<br>
            Estimated total treatment cost for {infected_plants} plants: <b>Rs {total_cost}</b><br>
            <span style="font-size:0.9rem; color:#b0c4ff;">
                This is based on typical Indian retail prices and standard doses
                for about 100 plants.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diagnosis_and_treatments(result: dict, plant_type: str, infected_count: int):
    disease_name = result.get("disease_name", "Unknown")
    disease_type = result.get("disease_type", "unknown")
    severity = result.get("severity", "unknown")
    confidence = result.get("confidence", 0)

    severity_class = get_severity_badge_class(severity)
    type_class = get_type_badge_class(disease_type)

    st.markdown(
        f"""
        <div class="disease-header">
            <div class="disease-name">{disease_name}</div>
            <div class="disease-meta">
                <span class="severity-badge {severity_class}">{severity.title()}</span>
                <span class="type-badge {type_class}">{disease_type.title()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Plant", plant_type)
    with col2:
        st.metric("Confidence", f"{confidence}%")
    with col3:
        st.metric("Severity", severity.title())

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(
            """<div class="info-section"><div class="info-title">Symptoms</div>""",
            unsafe_allow_html=True,
        )
        for symptom in result.get("symptoms", []):
            st.write(f"• {symptom}")
        st.markdown("</div>", unsafe_allow_html=True)

        if result.get("differential_diagnosis"):
            st.markdown(
                """<div class="info-section"><div class="info-title">Other Possibilities</div>""",
                unsafe_allow_html=True,
            )
            for diag in result.get("differential_diagnosis", []):
                st.write(f"• {diag}")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            """<div class="info-section"><div class="info-title">Causes</div>""",
            unsafe_allow_html=True,
        )
        for cause in result.get("probable_causes", []):
            st.write(f"• {cause}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """<div class="info-section"><div class="info-title">Actions</div>""",
            unsafe_allow_html=True,
        )
        for i, action in enumerate(result.get("immediate_action", []), 1):
            st.write(f"**{i}.** {action}")
        st.markdown("</div>", unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)
    organic_total_block = 0
    chemical_total_block = 0

    with col_t1:
        st.markdown(
            """<div class="info-section"><div class="info-title">Organic Treatments</div>""",
            unsafe_allow_html=True,
        )
        organic_treatments = result.get("organic_treatments", [])
        for treatment in organic_treatments:
            if not isinstance(treatment, str):
                continue
            t_name = normalize_treatment_name(treatment)
            info = get_treatment_info("organic", t_name)
            cost = info.get("cost", 300)
            quantity = info.get("quantity", "As per package")
            dilution = info.get("dilution", "Follow label instructions")
            organic_total_block += cost
            st.markdown(
                f"""
                <div class="treatment-item">
                    <div class="treatment-name">💊 {t_name}</div>
                    <div class="treatment-quantity">Quantity: {quantity}</div>
                    <div class="treatment-dilution">Dilution: {dilution}</div>
                    <div class="cost-info" style="margin-top: 8px; border-left: 5px solid #81c784;">
                        Cost: Rs {cost}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_t2:
        st.markdown(
            """<div class="info-section"><div class="info-title">Chemical Treatments</div>""",
            unsafe_allow_html=True,
        )
        chemical_treatments = result.get("chemical_treatments", [])
        for treatment in chemical_treatments:
            if not isinstance(treatment, str):
                continue
            t_name = normalize_treatment_name(treatment)
            info = get_treatment_info("chemical", t_name)
            cost = info.get("cost", 250)
            quantity = info.get("quantity", "As per package")
            dilution = info.get("dilution", "Follow label instructions")
            chemical_total_block += cost
            st.markdown(
                f"""
                <div class="treatment-item">
                    <div class="treatment-name">⚗️ {t_name}</div>
                    <div class="treatment-quantity">Quantity: {quantity}</div>
                    <div class="treatment-dilution">Dilution: {dilution}</div>
                    <div class="cost-info" style="margin-top: 8px; border-left: 5px solid #64b5f6;">
                        Cost: Rs {cost}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """<div class="info-section"><div class="info-title">Prevention</div>""",
        unsafe_allow_html=True,
    )
    for tip in result.get("prevention_long_term", []):
        st.write(f"• {tip}")
    st.markdown("</div>", unsafe_allow_html=True)

    if result.get("plant_specific_notes"):
        st.markdown(
            f"""
            <div class="info-section">
                <div class="info-title">{plant_type} Care Notes</div>
                {result.get("plant_specific_notes")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result.get("similar_conditions"):
        st.markdown(
            f"""
            <div class="info-section">
                <div class="info-title">Similar Conditions in {plant_type}</div>
                {result.get("similar_conditions")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_treatment_selection_ui(
        plant_type=plant_type,
        disease_name=disease_name,
        organic_treatments=organic_treatments,
        chemical_treatments=chemical_treatments,
        default_infected_count=infected_count,
    )

    return organic_total_block, chemical_total_block


def calculate_loss_percentage(disease_severity, infected_count, total_plants=100):
    """
    Estimate yield loss (%) based on:
    1) Severity band (healthy/mild/moderate/severe) -> typical loss range
    2) Fraction of plants that are infected
    """
    severity_bands = {
        "healthy": (0, 2),
        "mild": (5, 15),
        "moderate": (20, 40),
        "severe": (50, 70),
    }

    sev = (disease_severity or "moderate").lower()
    low, high = severity_bands.get(sev, severity_bands["moderate"])
    base_loss = (low + high) / 2.0

    if total_plants <= 0:
        infected_ratio = 1.0
    else:
        infected_ratio = max(0.0, min(infected_count / total_plants, 1.0))

    loss_percent = base_loss * infected_ratio
    loss_percent = max(0.0, min(loss_percent, 80.0))

    return int(round(loss_percent))


def resize_image(image, max_width=600, max_height=500):
    image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image


def enhance_image_for_analysis(image):
    from PIL import ImageEnhance

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)
    return image


def extract_json_robust(response_text: str):
    if not response_text:
        return None
    # First try direct
    try:
        return json.loads(response_text)
    except Exception:
        pass

    cleaned = response_text
    # Strip markdown code fences if present
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1]
        cleaned = cleaned.split("```", 1)
    elif "```" in cleaned:
        parts = cleaned.split("```")
        if len(parts) >= 3:
            cleaned = parts[13]
    try:
        return json.loads(cleaned.strip())
    except Exception:
        pass

    # Fallback: take first {...} block
    match = re.search(r"\{[\s\S]*\}", response_text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


def validate_json_result(data):
    required_fields = [
        "disease_name",
        "disease_type",
        "severity",
        "confidence",
        "symptoms",
        "probable_causes",
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, "OK"


# ============ SESSION STATE INIT ============

if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None
if "farmer_bot_messages" not in st.session_state:
    st.session_state.farmer_bot_messages = []
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Gemini 2.5 Flash"
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "show_tips" not in st.session_state:
    st.session_state.show_tips = True
if "confidence_min" not in st.session_state:
    st.session_state.confidence_min = 65
if "treatment_selection" not in st.session_state:
    st.session_state.treatment_selection = None

# ============ SIDEBAR ============

with st.sidebar:
    st.title("🌿 Smart Farmer Hub")
    page = st.radio(
        "Go to",
        [
            "AI Plant Doctor",
            "Cost Calculator & ROI",
            "KisanAI Assistant",
            "Crop Rotation Advisor",
        ],
    )
    if page == "AI Plant Doctor":
        st.header("Settings")
        st.session_state.model_choice = "Gemini 2.5 Flash"
        st.session_state.debug_mode = st.checkbox("Debug Mode", value=False)
        st.session_state.show_tips = st.checkbox("Show Tips", value=True)
        st.session_state.confidence_min = st.slider("Min Confidence (%)", 0, 100, 65)
        st.markdown("---")
        with st.expander("How It Works"):
            st.write(
                "1. Select your plant type\n"
                "2. Upload leaf image(s)\n"
                "3. AI analyses the leaf image\n"
                "4. High-accuracy diagnosis using Gemini"
            )
    st.header("Model Info")
    st.info("**Gemini Mode**\nAdvanced reasoning\nHigh accuracy\nAPI required")

# ============ MAIN PAGES ============

# Header
if page == "AI Plant Doctor":
    st.markdown(
        """
        <div class="header-container">
            <div class="header-title">🌿 AI Plant Doctor - Smart Edition</div>
            <div class="header-subtitle">
                Upload your plant leaf images and get instant disease diagnosis,
                treatments, and ROI guidance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown(
            '<div class="feature-card">📸 Image-based Diagnosis</div>',
            unsafe_allow_html=True,
        )
    with col_f2:
        st.markdown(
            '<div class="feature-card">💊 Organic & Chemical Treatments</div>',
            unsafe_allow_html=True,
        )
    with col_f3:
        st.markdown(
            '<div class="feature-card">📈 Cost & ROI Ready</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    plant_type = st.selectbox(
        "Select Plant Type", list(PLANT_COMMON_DISEASES.keys()), index=0
    )

    st.markdown(
        '<div class="upload-container"><h3>📤 Upload Leaf Images</h3>',
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Upload clear images of affected leaves (you can upload multiple)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    images = []
    if uploaded_files:
        st.markdown("#### Preview")
        img_cols = st.columns(len(uploaded_files))
        for i, file in enumerate(uploaded_files):
            img = Image.open(file)
            img = resize_image(img)
            images.append(img)
            with img_cols[i]:
                st.image(img, use_column_width=True)

    infected_count = st.number_input(
        "Estimated number of infected plants",
        min_value=1,
        value=50,
        step=1,
    )

    analyze_btn = st.button("🔍 Analyze Plant Health")

    result = None

    if analyze_btn:
        if not images:
            st.error("Please upload at least one leaf image to analyze.")
        else:
            progress_placeholder = st.empty()
            with st.spinner(f"Analyzing {plant_type}..."):
                try:
                    progress_placeholder.info(f"Processing {plant_type} leaf...")
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    if st.session_state.debug_mode:
                        st.info("Using: Gemini 2.5 Flash")
                    common_diseases = PLANT_COMMON_DISEASES.get(
                        plant_type, "various plant diseases"
                    )
                    prompt = EXPERT_PROMPT_TEMPLATE.format(
                        plant_type=plant_type,
                        common_diseases=common_diseases,
                    )
                    enhanced_images = [
                        enhance_image_for_analysis(img.copy()) for img in images
                    ]
                    response = model.generate_content([prompt] + enhanced_images)
                    raw_response = response.text or ""
                    if st.session_state.debug_mode:
                        with st.expander("Raw Response"):
                            st.markdown(
                                '<div class="debug-box">', unsafe_allow_html=True
                            )
                            displayed = (
                                raw_response[:3000] + "..."
                                if len(raw_response) > 3000
                                else raw_response
                            )
                            st.text(displayed)
                            st.markdown("</div>", unsafe_allow_html=True)

                    result = extract_json_robust(raw_response)
                    if result is None:
                        st.error("Could not parse AI response as valid JSON.")
                    progress_placeholder.empty()
                except Exception as e:
                    st.error(f"Analysis Failed: {str(e)}")
                    progress_placeholder.empty()

            if result:
                is_valid, validation_msg = validate_json_result(result)
                confidence = result.get("confidence", 0)
                if confidence < st.session_state.confidence_min:
                    st.warning(f"Low Confidence ({confidence}%)")

                st.markdown("<div class='result-container'>", unsafe_allow_html=True)

                organic_sum, chemical_sum = render_diagnosis_and_treatments(
                    result=result, plant_type=plant_type, infected_count=infected_count
                )

                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.last_diagnosis = {
                    "plant_type": plant_type,
                    "disease_name": result.get("disease_name", "Unknown"),
                    "disease_type": result.get("disease_type", "unknown"),
                    "severity": result.get("severity", "unknown"),
                    "confidence": confidence,
                    "organic_cost": organic_sum,
                    "chemical_cost": chemical_sum,
                    "infected_count": infected_count,
                    "timestamp": datetime.now().isoformat(),
                    "result": result,
                }

    elif st.session_state.last_diagnosis:
        st.markdown(
            """<div class="success-box">
                Showing results from your last diagnosis. You can visit other pages while keeping these results.
            </div>""",
            unsafe_allow_html=True,
        )
        last = st.session_state.last_diagnosis
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        organic_sum, chemical_sum = render_diagnosis_and_treatments(
            result=last.get("result", {}),
            plant_type=last.get("plant_type", "Unknown"),
            infected_count=last.get("infected_count", 1),
        )
        last["organic_cost"] = organic_sum
        last["chemical_cost"] = chemical_sum
        st.session_state.last_diagnosis = last
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Cost Calculator & ROI":
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title">📈 Treatment Cost Calculator & ROI</div>
            <div class="page-subtitle">
                Estimate treatment costs, yield impact, and return on investment based on your AI diagnosis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    diag = st.session_state.last_diagnosis
    if not diag:
        st.markdown(
            """<div class="warning-box">
                First run a diagnosis in the AI Plant Doctor page to auto-fill disease and treatment details.
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div class="info-section"><div class="info-title">Diagnosis Information</div></div>""",
            unsafe_allow_html=True,
        )

        plant_name = diag.get("plant_type", "Unknown")
        disease_name = diag.get("disease_name", "Unknown")

        selection = st.session_state.treatment_selection
        if selection and isinstance(selection.get("infected_plants"), int):
            infected_count = selection["infected_plants"]
        else:
            infected_count = diag.get("infected_count", 50)

        col_diag1, col_diag2, col_diag3, col_diag4, col_diag5 = st.columns(5)
        with col_diag1:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Plant</div>
                <div class="stat-value">{plant_name}</div></div>""",
                unsafe_allow_html=True,
            )
        with col_diag2:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Disease</div>
                <div class="stat-value">{disease_name[:12]}...</div></div>""",
                unsafe_allow_html=True,
            )
        with col_diag3:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Severity</div>
                <div class="stat-value">{diag.get('severity', 'Unknown').title()}</div></div>""",
                unsafe_allow_html=True,
            )
        with col_diag4:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Confidence</div>
                <div class="stat-value">{diag.get('confidence', 0)}%</div></div>""",
                unsafe_allow_html=True,
            )
        with col_diag5:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Infected Plants</div>
                <div class="stat-value">{infected_count}</div></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div class="info-section"><div class="info-title">Treatment Costs & Yield Data</div></div>""",
            unsafe_allow_html=True,
        )

        if selection and isinstance(selection.get("total_cost"), int):
            use_cost = selection["total_cost"]
            if selection["treatment_type"] == "organic":
                organic_default = use_cost
                chemical_default = 0
            else:
                organic_default = 0
                chemical_default = use_cost
        else:
            organic_default = int(diag.get("organic_cost", 300) * infected_count)
            chemical_default = int(diag.get("chemical_cost", 200) * infected_count)

        col_input1, col_input2, col_input3, col_input4 = st.columns(4)
        with col_input1:
            organic_cost_total = st.number_input(
                "Organic Treatment Cost (Rs) - All Plants",
                value=organic_default,
                min_value=0,
                step=100,
                help=f"Total cost for treating {infected_count} plants",
            )
        with col_input2:
            chemical_cost_total = st.number_input(
                "Chemical Treatment Cost (Rs) - All Plants",
                value=chemical_default,
                min_value=0,
                step=100,
                help=f"Total cost for treating {infected_count} plants",
            )
        with col_input3:
            yield_per_plant = st.number_input(
                "Average Yield per Healthy Plant (kg)",
                value=2.0,
                min_value=0.0,
                step=0.1,
            )
        with col_input4:
            price_per_kg = st.number_input(
                "Market Price (Rs per kg)", value=30.0, min_value=0.0, step=1.0
            )

        total_plants = st.number_input(
            "Total Plants in Field", value=max(infected_count * 2, 100), min_value=1
        )

        disease_severity = diag.get("severity", "moderate")
        loss_percent = calculate_loss_percentage(
            disease_severity, infected_count, total_plants
        )

        st.markdown(
            """<div class="info-section"><div class="info-title">Estimated Yield Loss & ROI</div></div>""",
            unsafe_allow_html=True,
        )

        potential_yield = total_plants * yield_per_plant
        potential_revenue = potential_yield * price_per_kg
        expected_loss_kg = potential_yield * (loss_percent / 100)
        expected_loss_rs = expected_loss_kg * price_per_kg

        col_loss1, col_loss2, col_loss3 = st.columns(3)
        with col_loss1:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Potential Yield (No Disease)</div>
                <div class="stat-value">{potential_yield:.0f} kg</div></div>""",
                unsafe_allow_html=True,
            )
        with col_loss2:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Expected Loss Due to Disease</div>
                <div class="stat-value">{expected_loss_kg:.0f} kg</div></div>""",
                unsafe_allow_html=True,
            )
        with col_loss3:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Expected Loss (Rs)</div>
                <div class="stat-value">Rs {expected_loss_rs:.0f}</div></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        col_roi1, col_roi2 = st.columns(2)
        with col_roi1:
            if organic_cost_total > 0:
                net_saving_org = expected_loss_rs - organic_cost_total
                roi_org = (
                    (net_saving_org / organic_cost_total) * 100
                    if organic_cost_total > 0
                    else 0
                )
            else:
                net_saving_org = 0
            st.markdown(
                """<div class="info-section"><div class="info-title">Organic Treatment ROI</div>""",
                unsafe_allow_html=True,
            )
            st.write(f"Total Organic Cost: Rs {organic_cost_total}")
            st.write(f"Estimated Loss Prevented: Rs {expected_loss_rs:.0f}")
            st.write(f"Net Saving: Rs {net_saving_org:.0f}")
            if organic_cost_total > 0:
                st.write(f"ROI: {roi_org:.1f}%")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_roi2:
            if chemical_cost_total > 0:
                net_saving_chem = expected_loss_rs - chemical_cost_total
                roi_chem = (
                    (net_saving_chem / chemical_cost_total) * 100
                    if chemical_cost_total > 0
                    else 0
                )
            else:
                net_saving_chem = 0
            st.markdown(
                """<div class="info-section"><div class="info-title">Chemical Treatment ROI</div>""",
                unsafe_allow_html=True,
            )
            st.write(f"Total Chemical Cost: Rs {chemical_cost_total}")
            st.write(f"Estimated Loss Prevented: Rs {expected_loss_rs:.0f}")
            st.write(f"Net Saving: Rs {net_saving_chem:.0f}")
            if chemical_cost_total > 0:
                st.write(f"ROI: {roi_chem:.1f}%")
            st.markdown("</div>", unsafe_allow_html=True)

elif page == "KisanAI Assistant":
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title">🤖 KisanAI - Farming Assistant</div>
            <div class="page-subtitle">
                Ask any question about crops, pests, fertilizers, irrigation, or government schemes in simple language.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_query = st.text_area(
        "Ask your question (Hindi, Punjabi, English all supported):",
        height=120,
        placeholder="Example: मेरी टमाटर की फसल में पत्तों पर सफेद धब्बे आ रहे हैं, क्या करूँ?",
    )
    ask_btn = st.button("Ask KisanAI")

    if ask_btn and user_query.strip():
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = (
                "You are KisanAI, an Indian agriculture expert. "
                "Explain in simple farmer-friendly language. Use bullet points where helpful. "
                "Keep answers practical and specific to Indian conditions.\n\n"
                f"Farmer's question:\n{user_query}"
            )
            resp = model.generate_content(prompt)
            answer = resp.text or "No answer generated."
            st.markdown(
                f"""<div class="kisan-response-box">{answer}</div>""",
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Error from KisanAI: {e}")

elif page == "Crop Rotation Advisor":
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title">🔄 Smart Crop Rotation Advisor</div>
            <div class="page-subtitle">
                Design 3-4 year crop rotations that improve soil health, break disease cycles, and increase farm income.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    base_crop = st.selectbox("Current Main Crop", list(CROP_ROTATION_DATA.keys()))
    region = st.selectbox("Region", REGIONS)
    soil_type = st.selectbox("Soil Type", SOIL_TYPES)
    market_focus = st.selectbox("Market Focus", MARKET_FOCUS)

    if st.button("Generate Rotation Plan"):
        data = CROP_ROTATION_DATA[base_crop]
        rotations = data["rotations"]
        info = data["info"]

        st.markdown(
            f"""<div class="info-section"><div class="info-title">Recommended 3-Year Rotation for {base_crop}</div></div>""",
            unsafe_allow_html=True,
        )

        year_cols = st.columns(3)
        all_crops = [base_crop] + rotations
        for year, (col, crop) in enumerate(zip(year_cols, all_crops), start=1):
            with col:
                st.markdown(
                    f"""<div class="rotation-card">
                        <div class="rotation-year">Year {year}</div>
                        <div class="crop-name">{crop}</div>
                        <div class="crop-description">{info.get(crop, '')}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown(
            """<div class="info-section"><div class="info-title">Why This Rotation Works</div>""",
            unsafe_allow_html=True,
        )
        st.write(
            "- Breaks disease and pest cycles specific to your main crop.\n"
            "- Balances nutrient use and replenishment across years.\n"
            "- Matches Indian market demand and typical price patterns.\n"
            "- Adapts to your region and soil type for better resilience."
        )
        st.markdown("</div>", unsafe_allow_html=True)
