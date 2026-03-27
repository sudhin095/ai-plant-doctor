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
import cv2

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
    "Tomato": {"rotations": ["Beans", "Cabbage", "Cucumber"], "info": {"Tomato": "...", "Beans": "...", "Cabbage": "...", "Cucumber": "..."}},
    "Rose": {"rotations": ["Marigold", "Chrysanthemum", "Herbs"], "info": {"Rose": "...", "Marigold": "...", "Chrysanthemum": "...", "Herbs": "..."}},
    "Apple": {"rotations": ["Legume Cover Crops", "Grasses", "Berries"], "info": {"Apple": "...", "Legume Cover Crops": "...", "Grasses": "...", "Berries": "..."}},
    "Lettuce": {"rotations": ["Spinach", "Broccoli", "Cauliflower"], "info": {"Lettuce": "...", "Spinach": "...", "Broccoli": "...", "Cauliflower": "..."}},
    "Grape": {"rotations": ["Legume Cover Crops", "Cereals", "Vegetables"], "info": {"Grape": "...", "Legume Cover Crops": "...", "Cereals": "...", "Vegetables": "..."}},
    "Pepper": {"rotations": ["Onion", "Garlic", "Spinach"], "info": {"Pepper": "...", "Onion": "...", "Garlic": "...", "Spinach": "..."}},
    "Cucumber": {"rotations": ["Maize", "Okra", "Legumes"], "info": {"Cucumber": "...", "Maize": "...", "Okra": "...", "Legumes": "..."}},
    "Strawberry": {"rotations": ["Garlic", "Onion", "Leafy Greens"], "info": {"Strawberry": "...", "Garlic": "...", "Onion": "...", "Leafy Greens": "..."}},
    "Corn": {"rotations": ["Soybean", "Pulses", "Oilseeds"], "info": {"Corn": "...", "Soybean": "...", "Pulses": "...", "Oilseeds": "..."}},
    "Potato": {"rotations": ["Peas", "Mustard", "Cereals"], "info": {"Potato": "...", "Peas": "...", "Mustard": "...", "Cereals": "..."}},
}

REGIONS = ["North India", "South India", "East India", "West India", "Central India"]
SOIL_TYPES = ["Black Soil", "Red Soil", "Laterite Soil", "Alluvial Soil", "Clay Soil"]
MARKET_FOCUS = ["Stable essentials", "High-value cash crops", "Low input / low risk"]

# ============ PLANT DISEASE CLASSES & KNOWLEDGE BASE (kept exactly as original) ============
PLANT_DISEASE_CLASSES = { ... }  # (same as original)
DISEASE_KNOWLEDGE_BASE = { ... }  # (same as original)

# ============ GLOBAL STYLES ============
st.markdown("""<style> ... (all original CSS unchanged) </style>""", unsafe_allow_html=True)

# ============ GEMINI CONFIG ============
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    st.error("GEMINI_API_KEY not found in environment variables!")
    st.stop()

# ============ PROMPTS & HELPER FUNCTIONS (unchanged) ============
# ... (EXPERT_PROMPT_TEMPLATE, PLANT_COMMON_DISEASES, all helper functions: preprocess_image_for_detection, get_treatment_info, etc.) ...

# ============ MAIN APP STARTS HERE ============
st.markdown("""<div class="header-container"><div class="header-title">🌿 AI Plant Doctor - Smart Edition</div></div>""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown('<div class="feature-card">✅ Plant-Specific</div>', unsafe_allow_html=True)
with col2: st.markdown('<div class="feature-card">🎯 Disease Detection</div>', unsafe_allow_html=True)
with col3: st.markdown('<div class="feature-card">🔬 Expert</div>', unsafe_allow_html=True)
with col4: st.markdown('<div class="feature-card">🚀 95%+ Accurate</div>', unsafe_allow_html=True)

with st.sidebar:
    page = st.radio("📂 Pages", ["AI Plant Doctor", "KisanAI Assistant", "Crop Rotation Advisor", "Cost Calculator & ROI"])
    # ... (sidebar settings unchanged) ...

# Session state
if "last_diagnosis" not in st.session_state: st.session_state.last_diagnosis = None
if "farmer_bot_messages" not in st.session_state: st.session_state.farmer_bot_messages = []
if "crop_rotation_result" not in st.session_state: st.session_state.crop_rotation_result = None
if "cost_roi_result" not in st.session_state: st.session_state.cost_roi_result = None
if "kisan_response" not in st.session_state: st.session_state.kisan_response = None

if page == "AI Plant Doctor":
    # Plant selection & image upload (unchanged)
    col_plant, col_upload = st.columns([1, 2])
    with col_plant:
        st.subheader("Select Plant Type")
        plant_options = ["Select a plant..."] + sorted(list(PLANT_COMMON_DISEASES.keys())) + ["Other (Manual Entry)"]
        selected_plant = st.selectbox("What plant do you have?", plant_options, label_visibility="collapsed")
        if selected_plant == "Other (Manual Entry)":
            custom_plant = st.text_input("Enter plant name", placeholder="e.g., Banana, Orange")
            plant_type = custom_plant if custom_plant else "Unknown Plant"
        else:
            plant_type = selected_plant if selected_plant != "Select a plant..." else None

    with col_upload:
        st.subheader("Upload Leaf Images")
        uploaded_files = st.file_uploader("Select images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, label_visibility="collapsed")

    if uploaded_files and len(uploaded_files) > 0 and plant_type and plant_type != "Select a plant...":
        # ... (image display and Analyze button - unchanged) ...
        if analyze_btn:
            # ... (full analysis logic - Gemini or Hybrid - unchanged) ...

            if result:
                # Display full diagnosis result (symptoms, treatments, etc.) - unchanged
                # ... (all the disease-header, metrics, symptoms, organic/chemical lists, prevention, notes) ...

                # ====================== YOUR REQUESTED FEATURE (ADDED HERE) ======================
                st.markdown("---")
                st.subheader("🛠️ Finalize Your Treatment Plan")
                st.markdown("""<div class="info-section"><div class="info-title">Select treatment & number of plants → cost will be auto-calculated</div></div>""", unsafe_allow_html=True)

                infected_count = st.number_input("Number of infected plants/trees", value=10, min_value=1, step=1)

                # Extract clean treatment names
                organic_options = ["None"] + [t.split(" - ")[0].strip() if " - " in str(t) else str(t).split(":")[0].strip() for t in result.get("organic_treatments", [])]
                chemical_options = ["None"] + [t.split(" - ")[0].strip() if " - " in str(t) else str(t).split(":")[0].strip() for t in result.get("chemical_treatments", [])]

                col_org, col_chem = st.columns(2)
                with col_org:
                    selected_organic = st.selectbox("🌱 Organic Treatment", organic_options)
                with col_chem:
                    selected_chemical = st.selectbox("⚗️ Chemical Treatment", chemical_options)

                if st.button("💰 Auto-Calculate Total Cost & Save for ROI", type="primary", use_container_width=True):
                    org_total = 0
                    chem_total = 0

                    if selected_organic != "None":
                        info = get_treatment_info("organic", selected_organic)
                        org_total = int(info.get("cost", 300) * (infected_count / 100.0))

                    if selected_chemical != "None":
                        info = get_treatment_info("chemical", selected_chemical)
                        chem_total = int(info.get("cost", 250) * (infected_count / 100.0))

                    # As per your rule: if one is chosen, the other becomes 0
                    if selected_organic != "None":
                        chem_total = 0
                    if selected_chemical != "None":
                        org_total = 0

                    # Save to session state
                    if st.session_state.last_diagnosis:
                        st.session_state.last_diagnosis["infected_count"] = infected_count
                        st.session_state.last_diagnosis["organic_cost"] = org_total
                        st.session_state.last_diagnosis["chemical_cost"] = chem_total
                        st.session_state.last_diagnosis["selected_organic"] = selected_organic if selected_organic != "None" else None
                        st.session_state.last_diagnosis["selected_chemical"] = selected_chemical if selected_chemical != "None" else None

                    st.success(f"""
                    ✅ Costs saved successfully!

                    **Organic Total Cost:** Rs {org_total:,}
                    **Chemical Total Cost:** Rs {chem_total:,}
                    (for {infected_count} plants)

                    These values are now **automatically filled** in the Cost Calculator & ROI page.
                    """)
                    st.rerun()

                # Save basic diagnosis (if not already saved)
                if "last_diagnosis" not in st.session_state or not st.session_state.last_diagnosis:
                    st.session_state.last_diagnosis = {
                        "plant_type": plant_type,
                        "disease_name": result.get("disease_name", "Unknown"),
                        "severity": result.get("severity", "moderate"),
                        "confidence": result.get("confidence", 80),
                        "organic_cost": 0,
                        "chemical_cost": 0,
                        "infected_count": 10,
                        "result": result
                    }

elif page == "KisanAI Assistant":
    # ... (unchanged) ...

elif page == "Crop Rotation Advisor":
    # ... (unchanged) ...

else:  # Cost Calculator & ROI
    st.markdown("""<div class="page-header"><div class="page-title">💰 Cost Calculator & ROI Analysis</div></div>""", unsafe_allow_html=True)
    diag = st.session_state.last_diagnosis
    if not diag:
        st.warning("No diagnosis found. Please run AI Plant Doctor first.")
    else:
        # Auto-filled values from the treatment selector you added
        organic_cost_total = diag.get("organic_cost", 0)
        chemical_cost_total = diag.get("chemical_cost", 0)
        infected_count = diag.get("infected_count", 10)

        # Rest of the Cost Calculator page (exactly as original but with auto-filled values)
        st.markdown("""<div class="info-section"><div class="info-title">Diagnosis Information</div></div>""", unsafe_allow_html=True)
        # ... (metrics columns unchanged) ...

        st.markdown("""<div class="info-section"><div class="info-title">Treatment Costs & Yield Data</div></div>""", unsafe_allow_html=True)
        col_input1, col_input2, col_input3, col_input4 = st.columns(4)
        with col_input1:
            organic_cost_total = st.number_input("Organic Treatment Cost (Rs) - All Plants", value=organic_cost_total, min_value=0, step=100)
        with col_input2:
            chemical_cost_total = st.number_input("Chemical Treatment Cost (Rs) - All Plants", value=chemical_cost_total, min_value=0, step=100)
        # ... yield and price inputs ...

        # ... rest of ROI calculation and display (unchanged) ...

</DOCUMENT>
