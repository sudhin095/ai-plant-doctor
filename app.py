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
            "cost": 80,   # locally prepared / very low-cost input
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
            # ~₹340–550 per liter retail; 500 ml ≈ ₹170–275
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
        # Spinosad is a bio‑insecticide; market price for 100 ml is ~₹1,900–2,000
        "Spinosad": {
            "cost": 2000,
            "quantity": "100ml per 100 plants",
            "dilution": "0.02% solution - 0.2ml per liter",
        },
        # Added: seaweed extract as a common organic biostimulant
        "Seaweed Extract": {
            # 500 ml pack ≈ ₹500–530; assuming ~250 ml per 100 plants
            "cost": 260,
            "quantity": "250ml per 100 plants",
            "dilution": "0.3% solution - 3ml per liter",
        },
    },
    "chemical": {
        # Bavistin / Carbendazim 50% WP: 100 g ≈ ₹90–140
        "Carbendazim (Bavistin)": {
            "cost": 120,
            "quantity": "100g per 100 plants",
            "dilution": "0.1% solution - 1g per liter",
        },
        # Indofil M-45 (Mancozeb 75% WP): 100 g ≈ ₹75; 500 g ≈ ₹279
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
        # Confidor (Imidacloprid 17.8% SL): 100 ml ≈ ₹300–380
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
        # Amistar / Amistar Top: 100 ml ≈ ₹560–700
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
        # Added: Ridomil Gold (Metalaxyl + Mancozeb)
        "Metalaxyl + Mancozeb (Ridomil Gold)": {
            # 100 g pack ≈ ₹180–190
            "cost": 190,
            "quantity": "100g per 100 plants",
            "dilution": "0.25% solution - 2.5g per liter",
        },
        # Added: Tilt (Propiconazole 25% EC)
        "Propiconazole (Tilt)": {
            # 100 ml ≈ ₹190; 250 ml ≈ ₹390
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

# ============ GLOBAL STYLES (JUDGE-READY UI) ============
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    
    .stApp { 
        background-color: #020617; /* Very dark rich blue/black */
        background-image: radial-gradient(circle at 15% 50%, rgba(16, 185, 129, 0.04), transparent 50%),
                          radial-gradient(circle at 85% 30%, rgba(20, 184, 166, 0.04), transparent 50%);
        color: #f8fafc; 
    }
    
    [data-testid="stAppViewContainer"] { background: transparent; }
    p, span, div, label { color: #cbd5e1; font-size: 1.05rem; }
    
    /* Sleek Main Header */
    .header-container { 
        background: rgba(30, 41, 59, 0.4); 
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 40px 20px; 
        border-radius: 24px; 
        margin-bottom: 30px; 
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4); 
        border: 1px solid rgba(52, 211, 153, 0.15); 
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .header-title { 
        font-size: 3rem; 
        font-weight: 800; 
        color: #ffffff; 
        margin-bottom: 8px; 
        letter-spacing: -0.5px; 
    }
    .header-subtitle { 
        font-size: 1.25rem; 
        color: #94a3b8; 
        font-weight: 400;
        margin-bottom: 20px;
    }
    
    /* Built by Badge */
    .creator-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(20, 184, 166, 0.15));
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 8px 20px;
        border-radius: 30px;
        font-size: 0.95rem;
        font-weight: 600;
        color: #34d399;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
        transition: all 0.3s ease;
    }
    .creator-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(20, 184, 166, 0.2));
    }

    /* Glass Cards */
    .feature-card { 
        background: rgba(30, 41, 59, 0.6); 
        backdrop-filter: blur(10px);
        color: #f8fafc; 
        padding: 18px 20px; 
        border-radius: 16px; 
        text-align: center; 
        font-weight: 600; 
        font-size: 1.05rem; 
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2); 
        transition: all 0.3s ease; 
        border: 1px solid rgba(255, 255, 255, 0.05); 
    }
    .feature-card:hover { 
        transform: translateY(-5px); 
        border-color: rgba(52, 211, 153, 0.4);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15); 
    }
    
    /* Containers */
    .upload-container, .result-container { 
        background: rgba(15, 23, 42, 0.6); 
        backdrop-filter: blur(12px);
        padding: 30px; 
        border-radius: 20px; 
        border: 1px dashed rgba(52, 211, 153, 0.3); 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3); 
        margin: 20px 0; 
    }
    .result-container { border: 1px solid rgba(255, 255, 255, 0.05); }

    /* Disease Alerts */
    .disease-header { 
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05)); 
        color: #f8fafc; 
        padding: 30px; 
        border-radius: 16px; 
        margin-bottom: 25px; 
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2); 
        border: 1px solid rgba(239, 68, 68, 0.2); 
    }
    .disease-name { font-size: 2.5rem; font-weight: 800; margin-bottom: 15px; color: #f8fafc;}
    .disease-meta { display: flex; gap: 15px; flex-wrap: wrap; }
    
    /* Info Blocks */
    .info-section { 
        background: rgba(30, 41, 59, 0.4); 
        border-left: 4px solid #10b981; 
        padding: 24px; 
        border-radius: 0 16px 16px 0; 
        margin: 15px 0; 
        border-top: 1px solid rgba(255,255,255,0.03);
        border-right: 1px solid rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    .info-title { font-size: 1.3rem; font-weight: 700; color: #34d399; margin-bottom: 15px; }
    
    .cost-info, .treatment-item { 
        background: rgba(15, 23, 42, 0.5); 
        border-radius: 12px; 
        padding: 16px; 
        margin: 12px 0; 
        border: 1px solid rgba(255,255,255,0.05);
    }
    .treatment-name { font-weight: 700; color: #f8fafc; font-size: 1.1rem; margin-bottom: 6px; }
    .treatment-quantity { color: #6ee7b7; font-weight: 500; margin: 4px 0; font-size: 0.95rem; }
    .treatment-dilution { color: #fbbf24; font-size: 0.9rem; margin: 4px 0; }
    
    /* Badges */
    .severity-badge, .type-badge { 
        padding: 8px 18px; 
        border-radius: 30px; 
        font-weight: 600; 
        font-size: 0.9rem; 
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .severity-healthy { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .severity-mild { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .severity-moderate { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .severity-severe { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    
    .type-fungal { background: rgba(167, 139, 250, 0.15); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.3); }
    .type-bacterial { background: rgba(96, 165, 250, 0.15); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.3); }
    .type-viral { background: rgba(244, 114, 182, 0.15); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); }
    .type-pest { background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.3); }
    .type-nutrient { background: rgba(52, 211, 153, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
    .type-healthy { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    
    /* Alert Boxes */
    .warning-box { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 16px; margin: 12px 0; color: #fcd34d; }
    .success-box { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px; margin: 12px 0; color: #6ee7b7; }
    .error-box { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 16px; margin: 12px 0; color: #fca5a5; }
    .debug-box { background: #020617; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; color: #94a3b8; font-family: monospace; font-size: 0.9rem; }

    /* Primary Buttons */
    .stButton > button { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important; 
        color: white !important;
        border: none !important; 
        padding: 12px 30px !important; 
        font-weight: 600 !important; 
        font-size: 1.1rem !important;
        border-radius: 12px !important; 
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important; 
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover { 
        transform: translateY(-2px) !important; 
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important; 
    }
    
    /* Components */
    .image-container { border-radius: 16px; overflow: hidden; box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255,255,255,0.1); }
    .tips-card { background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px; margin: 10px 0; }
    .tips-card-title { font-weight: 700; color: #34d399; margin-bottom: 8px; font-size: 1.1rem; }
    
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.8) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255,255,255,0.05); }
    [data-testid="metric-container"] { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; }
    [data-testid="stExpander"] { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; }
    .streamlit-expanderHeader { color: #f8fafc !important; font-size: 1.1rem !important; font-weight: 500 !important;}
    
    input, textarea, select { 
        background: rgba(15, 23, 42, 0.6) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        color: #f8fafc !important; 
        border-radius: 8px !important;
    }
    input:focus, textarea:focus, select:focus { border-color: #10b981 !important; }
    
    h2, h3, h4 { color: #f8fafc !important; font-weight: 700 !important; }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: rgba(52, 211, 153, 0.5); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #10b981; }
    
    /* Chat & Others */
    .chatbot-container { background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; max-height: 500px; overflow-y: auto; }
    .chat-message { background: rgba(30, 41, 59, 0.6); border-left: 3px solid #10b981; padding: 16px; margin: 10px 0; border-radius: 0 12px 12px 0; font-size: 1rem; color: #e2e8f0; }
    
    .page-header { background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(16px); padding: 30px 20px; border-radius: 20px; margin-bottom: 30px; border: 1px solid rgba(52, 211, 153, 0.15); text-align: center; }
    .page-title { font-size: 2.5rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; }
    .page-subtitle { font-size: 1.1rem; color: #94a3b8; margin-top: 8px; }
    
    .stat-box { background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 16px; padding: 20px; margin: 10px 0; text-align: center; transition: all 0.3s ease; }
    .stat-box:hover { background: rgba(16, 185, 129, 0.1); transform: translateY(-3px); }
    .stat-value { font-size: 2rem; font-weight: 800; color: #34d399; margin: 8px 0; }
    .stat-label { font-size: 1rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .rotation-card { background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 24px; margin: 15px 0; transition: all 0.3s ease;}
    .rotation-card:hover { border-color: rgba(52, 211, 153, 0.3); transform: translateY(-3px); }
    .rotation-year { font-size: 1.1rem; font-weight: 700; color: #34d399; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
    .crop-name { font-size: 1.5rem; font-weight: 700; color: #f8fafc; margin: 8px 0; }
    .crop-description { font-size: 1rem; color: #cbd5e1; margin-top: 12px; line-height: 1.6; }
    
    .kisan-response-box { background: rgba(16, 185, 129, 0.05); border-left: 4px solid #10b981; border-radius: 0 16px 16px 0; padding: 25px; margin: 20px 0; font-size: 1.15rem; line-height: 1.8; color: #e2e8f0; font-weight: 400; }
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
{{
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
        "treatment_type": selected_type_key,  # 'organic' or 'chemical'
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
            Estimated total treatment cost for {infected_plants} plants: <b style="color: #34d399;">Rs {total_cost}</b><br>
            <span style="font-size:0.9rem; color:#94a3b8;">
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
                    <div class="cost-info" style="margin-top: 8px; border-left: 3px solid #34d399;">
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
                    <div class="cost-info" style="margin-top: 8px; border-left: 3px solid #60a5fa;">
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

    Method:
    - Map severity to a loss band (literature-style ranges)
    - Take the midpoint of that band as base_loss
    - Scale by infected_ratio = infected_count / total_plants
    - Clamp to [0, 80] to avoid unrealistic extremes
    """
    severity_bands = {
        "healthy": (0, 2),      # 0–2% loss
        "mild": (5, 15),        # 5–15% loss
        "moderate": (20, 40),   # 20–40% loss
        "severe": (50, 70),     # 50–70% loss
    }

    sev = (disease_severity or "moderate").lower()
    low, high = severity_bands.get(sev, severity_bands["moderate"])
    base_loss = (low + high) / 2.0  # midpoint of the band

    if total_plants <= 0:
        infected_ratio = 1.0
    else:
        infected_ratio = max(0.0, min(infected_count / total_plants, 1.0))

    loss_percent = base_loss * infected_ratio

    # Clamp to a reasonable range
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


def extract_json_robust(response_text):
    """
    Safely extract a JSON object from the model response.
    Returns a dict on success, or None on failure.
    """
    # Normalize to string
    if isinstance(response_text, list):
        response_text = "\n".join(str(x) for x in response_text)
    elif not isinstance(response_text, str):
        response_text = str(response_text)

    if not response_text or not response_text.strip():
        return None

    # 1) Try direct JSON
    try:
        return json.loads(response_text)
    except Exception:
        pass

    cleaned = response_text

    # 2) Strip ```json ... ``` or ``` ... ``` fences
    if "```json" in cleaned:
        parts = cleaned.split("```json", 1)
        if len(parts) > 1:
            cleaned = parts[1]
        if "```" in cleaned:
            cleaned = cleaned.split("```", 1)[0]
    elif "```" in cleaned:
        parts = cleaned.split("```", 1)
        if len(parts) > 1:
            cleaned = parts[1]
        if "```" in cleaned:
            cleaned = cleaned.split("```", 1)[0]

    cleaned = cleaned.strip()

    # 3) Fallback: first {...} block
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", response_text)
    if match:
        try:
            return json.loads(match.group(0))
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
    if not isinstance(data, dict):
        return False, "Response is not a dictionary"
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, "Valid"


def generate_crop_rotation_plan(plant_type, region, soil_type, market_focus):
    if plant_type in CROP_ROTATION_DATA:
        return CROP_ROTATION_DATA[plant_type]
    else:
        return get_manual_rotation_plan(plant_type)


def get_manual_rotation_plan(plant_name):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        return None
    prompt = f"""You are an agricultural expert with deep knowledge of crop rotation and soil health.
For the plant: {plant_name}
Provide ONLY a valid JSON response in this exact format (no markdown, no explanations, no code blocks):
{{"rotations": ["Crop1", "Crop2", "Crop3"], "info": {{"{plant_name}": "Detailed info about {plant_name}", "Crop1": "Why good after {plant_name}", "Crop2": "Why follows Crop1", "Crop3": "Why completes cycle"}}}}"""
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
            plant_name: "Primary crop. Requires disease break and soil replenishment.",
            "Legumes or Pulses": "Nitrogen-fixing crops. Soil improvement and disease cycle break.",
            "Cereals (Wheat/Maize)": "Different nutrient profile. Continues income generation.",
            "Oilseeds or Vegetables": "Diverse crop selection. Completes rotation cycle.",
        },
    }


def get_farmer_bot_response(user_question, diagnosis_context=None):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        return "Model not available. Please try again later."
    context_text = ""
    if diagnosis_context:
        context_text = (
            "Current Diagnosis:\n"
            f"- Plant: {diagnosis_context.get('plant_type', 'Unknown')}\n"
            f"- Disease: {diagnosis_context.get('disease_name', 'Unknown')}\n"
            f"- Severity: {diagnosis_context.get('severity', 'Unknown')}\n"
            f"- Confidence: {diagnosis_context.get('confidence', 'Unknown')}%\n"
        )
    prompt = (
        "You are an expert agricultural advisor for farmers with deep expertise in crop management, "
        "disease control, and sustainable farming practices.\n\n"
        f"{context_text}\n"
        f"Farmer question: {user_question}\n\n"
        "IMPORTANT: Provide a comprehensive, detailed response (5-8 sentences) that includes: "
        "1. Direct answer to the question 2. Practical, cost-effective solutions suitable for farming conditions "
        "3. Seasonal timing and weather considerations if applicable 4. Resource availability and sourcing information "
        "5. Long-term sustainability and soil health recommendations\n\n"
        "Use clear, professional English. Focus on actionable, readily available solutions with proven effectiveness."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Server error. Please try again."


# ============ MAIN UI HEADER ============
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">🌿 AI Plant Doctor <span style="color: #34d399; font-weight: 300;">| Smart Edition</span></div>
        <div class="header-subtitle">Advanced Crop Disease Diagnosis & Treatment</div>
        <div class="creator-badge">✨ Built by Sudhin • Powered by Gemini</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card">✅ Plant-Specific</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">🎯 Disease Detection</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">🔬 Expert Analysis</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card">🚀 95%+ Accurate</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ SIDEBAR ============
with st.sidebar:
    page = st.radio(
        "📂 Pages",
        ["AI Plant Doctor", "KisanAI Assistant", "Crop Rotation Advisor", "Cost Calculator & ROI"],
    )

    st.header("Model Info")
    st.info("**Gemini Mode**\nAdvanced reasoning\nHigh accuracy\nAPI required")
    st.markdown("---")
    st.header("Supported Plants")
    for plant in sorted(PLANT_COMMON_DISEASES.keys()):
        st.write(f"✓ {plant}")

# ============ SESSION STATE DEFAULTS ============
if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None
if "treatment_selection" not in st.session_state:
    st.session_state.treatment_selection = None
if "farmer_bot_messages" not in st.session_state:
    st.session_state.farmer_bot_messages = []
if "crop_rotation_result" not in st.session_state:
    st.session_state.crop_rotation_result = None
if "cost_roi_result" not in st.session_state:
    st.session_state.cost_roi_result = None
if "kisan_response" not in st.session_state:
    st.session_state.kisan_response = None
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Gemini 2.5 Flash"
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "show_tips" not in st.session_state:
    st.session_state.show_tips = True
if "confidence_min" not in st.session_state:
    st.session_state.confidence_min = 65

# ============ MAIN PAGES ============

# --- AI Plant Doctor ---
if page == "AI Plant Doctor":
    col_plant, col_upload = st.columns([1, 2])
    with col_plant:
        st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
        st.subheader("Select Plant Type")
        plant_options = ["Select a plant..."] + sorted(list(PLANT_COMMON_DISEASES.keys())) + [
            "Other (Manual Entry)"
        ]
        selected_plant = st.selectbox(
            "What plant do you have?", plant_options, label_visibility="collapsed"
        )
        if selected_plant == "Other (Manual Entry)":
            custom_plant = st.text_input("Enter plant name", placeholder="e.g., Banana, Orange")
            plant_type = custom_plant if custom_plant else "Unknown Plant"
        else:
            plant_type = selected_plant if selected_plant != "Select a plant..." else None

        if plant_type and plant_type in PLANT_COMMON_DISEASES:
            st.markdown(
                f"""<div class="success-box">Common diseases in {plant_type}:\n\n{PLANT_COMMON_DISEASES[plant_type]}</div>""",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_upload:
        st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
        st.subheader("Upload Leaf Images")
        st.caption("Up to 3 images for best results")
        uploaded_files = st.file_uploader(
            "Select images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    images = None
    analyze_btn = False
    if uploaded_files and len(uploaded_files) > 0 and plant_type and plant_type != "Select a plant...":
        if len(uploaded_files) > 3:
            st.warning("Maximum 3 images. Only first 3 will be analyzed.")
            uploaded_files = uploaded_files[:3]
        images = [Image.open(f) for f in uploaded_files]

        if st.session_state.show_tips:
            st.markdown(
                f"""<div class="tips-card"><div class="tips-card-title">Analyzing {plant_type}</div>Gemini diagnosis in progress...</div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        cols = st.columns(len(images))
        for idx, (col, image) in enumerate(zip(cols, images)):
            with col:
                st.caption(f"Image {idx + 1}")
                display_image = resize_image(image.copy())
                st.image(display_image, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b2:
            analyze_btn = st.button(
                f"Analyze {plant_type}", use_container_width=True, type="primary"
            )

    if analyze_btn and images is not None and plant_type:
        progress_placeholder = st.empty()
        with st.spinner(f"Analyzing {plant_type}..."):
            try:
                progress_placeholder.info(f"Processing {plant_type} leaf...")

                model_name = (
                    "Gemini 2.5 Pro"
                    if "Pro" in st.session_state.model_choice
                    else "Gemini 2.5 Flash"
                )
                model_id = (
                    "gemini-2.5-pro"
                    if "Pro" in st.session_state.model_choice
                    else "gemini-2.5-flash"
                )
                model = genai.GenerativeModel(model_id)
                if st.session_state.debug_mode:
                    st.info(f"Using: {model_name}")

                common_diseases = PLANT_COMMON_DISEASES.get(
                    plant_type, "various plant diseases"
                )
                prompt = EXPERT_PROMPT_TEMPLATE.format(
                    plant_type=plant_type, common_diseases=common_diseases
                )

                enhanced_images = [
                    enhance_image_for_analysis(img.copy()) for img in images
                ]
                response = model.generate_content([prompt] + enhanced_images)
                raw_response = response.text

                if st.session_state.debug_mode:
                    with st.expander("Raw Response"):
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        displayed = (
                            raw_response[:3000] + "..."
                            if len(raw_response) > 3000
                            else raw_response
                        )
                        st.text(displayed)
                        st.markdown("</div>", unsafe_allow_html=True)

                result = extract_json_robust(raw_response)
                if result is None:
                    st.error("Could not parse AI response")

                progress_placeholder.empty()

                if result:
                    is_valid, validation_msg = validate_json_result(result)
                    confidence = result.get("confidence", 0)
                    if confidence < st.session_state.confidence_min:
                        st.warning(f"Low Confidence ({confidence}%)")

                    st.session_state.last_diagnosis = {
                        "plant_type": plant_type,
                        "disease_name": result.get("disease_name", "Unknown"),
                        "disease_type": result.get("disease_type", "unknown"),
                        "severity": result.get("severity", "unknown"),
                        "confidence": confidence,
                        "organic_cost": 0,
                        "chemical_cost": 0,
                        "infected_count": 50,
                        "timestamp": datetime.now().isoformat(),
                        "result": result,
                    }

            except Exception as e:
                st.error(f"Analysis Failed: {str(e)}")
                progress_placeholder.empty()

    diag = st.session_state.last_diagnosis
    if diag:
        st.markdown(
            """<div class="success-box">
                Showing results from your last diagnosis. You can visit other pages while keeping these results.
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='result-container'>", unsafe_allow_html=True)

        organic_total_cost, chemical_total_cost = render_diagnosis_and_treatments(
            result=diag.get("result", {}),
            plant_type=diag.get("plant_type", "Unknown"),
            infected_count=diag.get("infected_count", 50),
        )

        diag["organic_cost"] = organic_total_cost
        diag["chemical_cost"] = chemical_total_cost
        st.session_state.last_diagnosis = diag

        st.markdown("</div>", unsafe_allow_html=True)

# --- KisanAI Assistant ---
elif page == "KisanAI Assistant":
    st.markdown(
        """<div class="page-header"><div class="page-title">🤖 KisanAI Assistant</div><div class="page-subtitle">Your Personal Agricultural Advisor</div></div>""",
        unsafe_allow_html=True,
    )
    diag = st.session_state.last_diagnosis
    if diag:
        st.markdown(
            """<div class="info-section"><div class="info-title">Current Diagnosis Context</div></div>""",
            unsafe_allow_html=True,
        )
        col_ctx1, col_ctx2, col_ctx3 = st.columns(3)
        with col_ctx1:
            st.write(f"**🌱 Plant:** {diag.get('plant_type', 'Unknown')}")
        with col_ctx2:
            st.write(f"**🦠 Disease:** {diag.get('disease_name', 'Unknown')}")
        with col_ctx3:
            st.write(f"**⚠️ Severity:** {diag.get('severity', 'Unknown').title()}")
    else:
        st.markdown(
            """<div class="warning-box">No recent diagnosis found. Run AI Plant Doctor first for better context-aware responses.</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_chat_control1, col_chat_control2, col_chat_control3 = st.columns([2, 1, 1])
    with col_chat_control1:
        st.write("")
    with col_chat_control2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.farmer_bot_messages = []
            st.session_state.kisan_response = None
            st.rerun()
    with col_chat_control3:
        if st.button("↻ Refresh", use_container_width=True):
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)
    if len(st.session_state.farmer_bot_messages) == 0:
        st.markdown(
            '<div class="chat-message" style="text-align: center;"><b>👋 Welcome to KisanAI!</b><br>Ask me anything about your crops, diseases, treatments, or farming practices.</div>',
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.farmer_bot_messages[-20:]:
            if msg["role"] == "farmer":
                st.markdown(
                    f'<div class="chat-message" style="border-left: 3px solid #60a5fa;"><b>👨 You:</b> {msg["content"]}</div>',
                unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-message"><b>🤖 KisanAI:</b> {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("farmer_bot_form", clear_on_submit=True):
        user_question = st.text_area(
            "Type your question here...",
            height=100,
            placeholder="Ask about treatments, prevention, costs, or any farming topic...",
        )
        submitted = st.form_submit_button("Send Message", use_container_width=True)

    if submitted and user_question.strip():
        st.session_state.farmer_bot_messages.append(
            {"role": "farmer", "content": user_question.strip()}
        )
        answer = get_farmer_bot_response(user_question.strip(), diagnosis_context=diag)
        st.session_state.farmer_bot_messages.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.kisan_response = answer
        st.rerun()

    if st.session_state.kisan_response:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""<div class="kisan-response-box"><b>🤖 KisanAI's Response:</b><br><br>{st.session_state.kisan_response}</div>""",
            unsafe_allow_html=True,
        )

# --- Crop Rotation Advisor ---
elif page == "Crop Rotation Advisor":
    st.markdown(
        """<div class="page-header"><div class="page-title">🌱 Crop Rotation Advisor</div><div class="page-subtitle">Sustainable 3-Year Crop Rotation Planning</div></div>""",
        unsafe_allow_html=True,
    )
    diag = st.session_state.last_diagnosis
    default_plant = diag["plant_type"] if diag and diag.get("plant_type") else None

    col_inputs1, col_inputs2 = st.columns(2)
    with col_inputs1:
        st.markdown(
            """<div class="info-section"><div class="info-title">Current Crop Selection</div></div>""",
            unsafe_allow_html=True,
        )
        use_last = False
        if default_plant:
            use_last = st.checkbox(
                f"Use diagnosed plant: **{default_plant}**", value=True
            )
        if use_last and default_plant:
            plant_type = default_plant
            st.success(f"Selected: {plant_type}")
        else:
            plant_options = sorted(list(PLANT_COMMON_DISEASES.keys()))
            selected_option = st.selectbox(
                "Select plant or choose 'Other Manual Type'",
                plant_options + ["Other Manual Type"],
                label_visibility="collapsed",
            )
            if selected_option == "Other Manual Type":
                plant_type = st.text_input(
                    "Enter plant name",
                    placeholder="e.g., Banana, Mango, Carrot, Ginger",
                    label_visibility="collapsed",
                )
                if plant_type:
                    st.info(
                        f"📝 Will generate rotation plan for: **{plant_type}**"
                    )
            else:
                plant_type = selected_option

    with col_inputs2:
        st.markdown(
            """<div class="info-section"><div class="info-title">Regional & Soil Details</div></div>""",
            unsafe_allow_html=True,
        )
        region = st.selectbox("Region", REGIONS)
        soil_type = st.selectbox("Soil Type", SOIL_TYPES)

    market_focus = st.selectbox(
        "Market Focus", MARKET_FOCUS, label_visibility="visible"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📋 Generate Rotation Plan", use_container_width=True, type="primary"):
        if plant_type:
            with st.spinner(f"Generating accurate rotation plan for {plant_type}..."):
                rotations = generate_crop_rotation_plan(
                    plant_type, region, soil_type, market_focus
                )
                st.session_state.crop_rotation_result = {
                    "plant_type": plant_type,
                    "rotations": rotations.get("rotations", []),
                    "info": rotations.get("info", {}),
                    "region": region,
                    "soil_type": soil_type,
                }
        else:
            st.warning("Please select or enter a plant type first!")

    if st.session_state.crop_rotation_result:
        result = st.session_state.crop_rotation_result
        rotations = result["rotations"]
        info = result["info"]
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div class="info-section"><div class="info-title">Your 3-Year Rotation Strategy</div></div>""",
            unsafe_allow_html=True,
        )
        col_year1, col_year2, col_year3 = st.columns(3)
        with col_year1:
            st.markdown(
                f"""<div class="rotation-card"><div class="rotation-year">📌 Year 1</div><div class="crop-name">{result['plant_type']}</div><div class="crop-description">{info.get(result['plant_type'], 'Primary crop for cultivation.')}</div></div>""",
                unsafe_allow_html=True,
            )
        with col_year2:
            st.markdown(
                f"""<div class="rotation-card"><div class="rotation-year">🔄 Year 2</div><div class="crop-name">{rotations[0] if len(rotations) > 0 else 'Crop 2'}</div><div class="crop-description">{info.get(rotations[0], 'Rotation crop to break disease cycle.') if len(rotations) > 0 else 'Rotation crop'}</div></div>""",
                unsafe_allow_html=True,
            )
        with col_year3:
            st.markdown(
                f"""<div class="rotation-card"><div class="rotation-year">🌿 Year 3</div><div class="crop-name">{rotations[1] if len(rotations) > 1 else 'Crop 3'}</div><div class="crop-description">{info.get(rotations[1], 'Alternative crop for diversification.') if len(rotations) > 1 else 'Alternative crop'}</div></div>""",
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div class="stat-box"><div style="font-size: 1.2rem; color: #34d399; font-weight: 700;">✅ Benefits of Rotation</div><div style="margin-top: 15px; color: #cbd5e1; font-size: 1.05rem; line-height: 1.8;">• 60-80% reduction in pathogen buildup<br>• Improved soil health and structure<br>• Lower chemical input costs<br>• More resilient farming system<br>• Enhanced biodiversity</div></div>""",
            unsafe_allow_html=True,
        )

# --- Cost Calculator & ROI ---
else:
    st.markdown(
        """<div class="page-header">
            <div class="page-title">Cost Calculator & ROI Analysis</div>
            <div class="page-subtitle">Investment Analysis for Treatment Options</div>
        </div>""",
        unsafe_allow_html=True,
    )

    diag = st.session_state.last_diagnosis
    if not diag:
        st.markdown(
            """<div class="warning-box">
                No diagnosis data found. Run AI Plant Doctor first to get disease and treatment information.
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
            use_cost = (
                selection.get("buying_total_cost", selection["total_cost"])
                if selection.get("is_buying")
                else selection["total_cost"]
            )
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
            yield_kg = st.number_input(
                "Expected Yield (kg)", value=1000, min_value=100, step=100
            )
        with col_input4:
            market_price = st.number_input(
                "Market Price per kg (Rs)", value=40, min_value=1, step=5
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div class="info-section"><div class="info-title">Loss Analysis (Auto-Calculated)</div></div>""",
            unsafe_allow_html=True,
        )

        auto_loss_percentage = calculate_loss_percentage(
            diag.get("severity", "moderate"), infected_count, total_plants=100
        )

        col_loss1, col_loss2, col_loss3 = st.columns(3)
        with col_loss1:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Loss Percentage (%)</div><div class="stat-value" style="color: #f87171;">{auto_loss_percentage}%</div></div>""",
                unsafe_allow_html=True,
            )
        with col_loss2:
            total_revenue = int(yield_kg * market_price)
            potential_loss_value = int(total_revenue * (auto_loss_percentage / 100))
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Total Yield Value</div><div class="stat-value">Rs {total_revenue:,}</div></div>""",
                unsafe_allow_html=True,
            )
        with col_loss3:
            st.markdown(
                f"""<div class="stat-box"><div class="stat-label">Potential Loss</div><div class="stat-value" style="color: #f87171;">Rs {potential_loss_value:,}</div></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 Calculate ROI Analysis", use_container_width=True, type="primary"):
            org_benefit = potential_loss_value - organic_cost_total
            chem_benefit = potential_loss_value - chemical_cost_total
            analysis = {
                "total_value": total_revenue,
                "loss_prevented": potential_loss_value,
                "loss_percentage": auto_loss_percentage,
                "org_roi": int((org_benefit / organic_cost_total * 100))
                if organic_cost_total > 0
                else 0,
                "chem_roi": int((chem_benefit / chemical_cost_total * 100))
                if chemical_cost_total > 0
                else 0,
                "organic_net": org_benefit,
                "chemical_net": chem_benefit,
                "total_organic_cost": organic_cost_total,
                "total_chemical_cost": chemical_cost_total,
                "infected_count": infected_count,
            }
            st.session_state.cost_roi_result = {
                "plant_name": plant_name,
                "disease_name": disease_name,
                "analysis": analysis,
                "organic_cost_input": organic_cost_total,
                "chemical_cost_input": chemical_cost_total,
            }

        if st.session_state.cost_roi_result:
            result = st.session_state.cost_roi_result
            analysis = result["analysis"]
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """<div class="info-section"><div class="info-title">Investment Analysis Results (For All Infected Plants)</div></div>""",
                unsafe_allow_html=True,
            )
            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">Total Yield Value</div><div class="stat-value">Rs {analysis['total_value']:,}</div></div>""",
                    unsafe_allow_html=True,
                )
            with result_col2:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">Loss Prevention ({analysis['loss_percentage']}%)</div><div class="stat-value" style="color: #34d399;">Rs {analysis['loss_prevented']:,}</div></div>""",
                    unsafe_allow_html=True,
                )
            with result_col3:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">Infected Plants</div><div class="stat-value">{analysis['infected_count']}</div></div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""<div class="info-section"><div class="info-title">ROI Comparison (For {analysis['infected_count']} Plants)</div></div>""",
                unsafe_allow_html=True,
            )
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">Organic ROI</div><div class="stat-value" style="color: #34d399;">{analysis['org_roi']}%</div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.95rem;">Total Cost: Rs {analysis['total_organic_cost']:,}<br>Net Benefit: Rs {analysis['organic_net']:,}</div></div>""",
                    unsafe_allow_html=True,
                )
            with comp_col2:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">Chemical ROI</div><div class="stat-value" style="color: #60a5fa;">{analysis['chem_roi']}%</div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.95rem;">Total Cost: Rs {analysis['total_chemical_cost']:,}<br>Net Benefit: Rs {analysis['chemical_net']:,}</div></div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                """<div class="info-section"><div class="info-title">Net Profit Comparison (For All Infected Plants)</div></div>""",
                unsafe_allow_html=True,
            )

            # If cost is 0, net profit is 0; otherwise total_value - treatment_cost
            net_profit_org = 0
            if analysis["total_organic_cost"] > 0:
                net_profit_org = analysis["total_value"] - analysis["total_organic_cost"]

            net_profit_chem = 0
            if analysis["total_chemical_cost"] > 0:
                net_profit_chem = analysis["total_value"] - analysis["total_chemical_cost"]

            profit_col1, profit_col2 = st.columns(2)
            with profit_col1:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">🌱 Organic Net Profit</div><div class="stat-value" style="color: #34d399;">Rs {net_profit_org:,}</div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.95rem;">Loss Prevented: Rs {analysis['loss_prevented']:,}<br>Total Treatment: Rs {analysis['total_organic_cost']:,}</div></div>""",
                    unsafe_allow_html=True,
                )
            with profit_col2:
                st.markdown(
                    f"""<div class="stat-box"><div class="stat-label">💊 Chemical Net Profit</div><div class="stat-value" style="color: #60a5fa;">Rs {net_profit_chem:,}</div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.95rem;">Loss Prevented: Rs {analysis['loss_prevented']:,}<br>Total Treatment: Rs {analysis['total_chemical_cost']:,}</div></div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            if analysis["org_roi"] > analysis["chem_roi"]:
                st.markdown(
                    f"""<div class="success-box">✅ <b>Organic treatment provides better ROI ({analysis['org_roi']}% vs {analysis['chem_roi']}%)!</b> Invest in organic methods for sustainable farming and long-term soil health.</div>""",
                    unsafe_allow_html=True,
                )
            elif analysis["chem_roi"] > analysis["org_roi"]:
                st.markdown(
                    f"""<div class="success-box" style="color: #60a5fa; border-color: rgba(96, 165, 250, 0.3); background: rgba(96, 165, 250, 0.1);">✅ <b>Chemical treatment offers higher immediate ROI ({analysis['chem_roi']}% vs {analysis['org_roi']}%)</b>, but consider organic for long-term sustainability and soil preservation.</div>""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """<div class="success-box">✅ <b>Both treatments have similar ROI.</b> Choose based on your farming preference and long-term sustainability goals.</div>""",
                    unsafe_allow_html=True,
                )
