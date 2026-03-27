import os
import json
from datetime import datetime

import streamlit as st
import google.generativeai as genai

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================== GLOBAL STYLES ==================
st.markdown(
    """
<style>
    * { margin: 0; padding: 0; }
    .stApp { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); color: #e4e6eb; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
    p, span, div, label { color: #e4e6eb; font-size: 1.05rem; }
    .header-container { background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%); padding: 30px 20px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); border: 1px solid rgba(102, 126, 234, 0.3); }
    .header-title { font-size: 2.5rem; font-weight: 700; color: #ffffff; text-align: center; margin-bottom: 5px; letter-spacing: 1px; }
    .header-subtitle { font-size: 1.1rem; color: #b0c4ff; text-align: center; }
    .result-container { background: linear-gradient(135deg, #1e2330 0%, #2a3040 100%); border-radius: 15px; padding: 25px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); margin: 15px 0; border: 1px solid rgba(102, 126, 234, 0.2); }
    .disease-header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(245, 87, 108, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); }
    .disease-name { font-size: 2.2rem; font-weight: 700; margin-bottom: 10px; }
    .disease-meta { font-size: 1rem; opacity: 0.95; display: flex; gap: 16px; flex-wrap: wrap; }
    .info-section { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 5px solid #667eea; padding: 18px; border-radius: 8px; margin: 12px 0; border: 1px solid rgba(102, 126, 234, 0.2); }
    .info-title { font-size: 1.25rem; font-weight: 700; color: #b0c4ff; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
    .cost-info { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 5px solid #667eea; padding: 10px 14px; border-radius: 6px; margin: 8px 0; font-size: 0.95rem; color: #b0c4ff; font-weight: 600; }
    .treatment-item { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border-left: 5px solid #667eea; padding: 14px; border-radius: 6px; margin: 10px 0; font-size: 0.95rem; color: #b0c4ff; }
    .treatment-name { font-weight: 700; color: #ffffff; margin-bottom: 5px; }
    .treatment-quantity { color: #81c784; font-weight: 600; margin: 4px 0; }
    .treatment-dilution { color: #ffcc80; font-size: 0.9rem; margin: 4px 0; }
    .severity-badge { display: inline-block; padding: 8px 14px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }
    .severity-healthy { background-color: #1b5e20; color: #4caf50; }
    .severity-mild { background-color: #004d73; color: #4dd0e1; }
    .severity-moderate { background-color: #633d00; color: #ffc107; }
    .severity-severe { background-color: #5a1a1a; color: #ff6b6b; }
    .type-badge { display: inline-block; padding: 6px 12px; border-radius: 15px; font-weight: 600; font-size: 0.9rem; margin: 4px 4px 4px 0; }
    .type-fungal { background-color: #4a148c; color: #ce93d8; }
    .type-bacterial { background-color: #0d47a1; color: #64b5f6; }
    .type-viral { background-color: #5c0b0b; color: #ef9a9a; }
    .type-pest { background-color: #4d2600; color: #ffcc80; }
    .type-nutrient { background-color: #0d3a1a; color: #81c784; }
    .type-healthy { background-color: #0d3a1a; color: #81c784; }
    .warning-box { background: linear-gradient(135deg, #4d2600 0%, #3d2000 100%); border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin: 10px 0; color: #ffcc80; font-size: 1rem; }
    .success-box { background: linear-gradient(135deg, #1b5e20 0%, #0d3a1a 100%); border: 1px solid #4caf50; border-radius: 8px; padding: 15px; margin: 10px 0; color: #81c784; font-size: 1rem; }
    [data-testid="stSidebar"] { background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%); }
    [data-testid="metric-container"] { background: linear-gradient(135deg, #2a3040 0%, #353d50 100%); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 8px; }
    .page-header { background: linear-gradient(135deg, #1a2a47 0%, #2d4a7a 100%); padding: 24px 18px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); border: 1px solid rgba(102, 126, 234, 0.3); }
    .page-title { font-size: 2rem; font-weight: 700; color: #ffffff; text-align: center; letter-spacing: 1px; }
    .page-subtitle { font-size: 1rem; color: #b0c4ff; text-align: center; margin-top: 8px; }
    .stat-box { background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border: 2px solid #667eea; border-radius: 12px; padding: 16px; margin: 8px 0; text-align: center; }
    .stat-value { font-size: 1.4rem; font-weight: 700; color: #667eea; margin: 6px 0; }
    .stat-label { font-size: 0.95rem; color: #b0c4ff; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; padding: 10px 24px !important; font-weight: 600 !important; font-size: 1.05rem !important; border-radius: 8px !important; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important; }
    h2, h3, h4 { font-size: 1.3rem !important; color: #b0c4ff !important; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0f1419; }
    ::-webkit-scrollbar-thumb { background: #667eea; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #764ba2; }
</style>
""",
    unsafe_allow_html=True,
)

# ================== GEMINI CONFIG ==================
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

EXPERT_PROMPT_TEMPLATE = """
You are an elite plant pathologist with 40 years of specialized experience diagnosing diseases in {plant_type}.
You are an expert specifically in {plant_type} diseases and health issues.

SPECIALIZED ANALYSIS FOR: {plant_type}
Common diseases in {plant_type}: {common_diseases}

User observation:
{user_observation}

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
  "chemical_treatments": ["Chemical 1: Safe for {plant_type} with dilution", "Chemical 2: Alternative safe for {plant_type}", "Safety: Important precautions for {plant_type}"],
  "prevention_long_term": ["Prevention strategy 1 for {plant_type}", "Prevention strategy 2 for {plant_type}", "Resistant varieties: If available for {plant_type}"],
  "plant_specific_notes": "Important notes specific to {plant_type} care and disease management",
  "similar_conditions": "Other {plant_type} conditions that look similar"
}}
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

# ================== TREATMENT COSTS & QUANTITIES DB ==================
TREATMENT_COSTS = {
    "organic": {
        "Cow Urine Extract": {
            "cost": 80,
            "quantity": "2–3 liters per 100 plants",
            "dilution": "1:5 with water",
        },
        "Sulfur Dust": {
            "cost": 120,
            "quantity": "500 g per 100 plants",
            "dilution": "Direct dust - 5–10 g per plant",
        },
        "Sulfur Powder": {
            "cost": 150,
            "quantity": "200 g per 100 plants",
            "dilution": "3% suspension - about 20 ml per plant",
        },
        "Lime Sulfur": {
            "cost": 180,
            "quantity": "1 liter per 100 plants",
            "dilution": "1:10 with water",
        },
        "Neem Oil Spray": {
            "cost": 200,
            "quantity": "500 ml per 100 plants",
            "dilution": "3% solution - 5 ml per liter",
        },
        "Bordeaux Mixture": {
            "cost": 250,
            "quantity": "300 g per 100 plants",
            "dilution": "1% solution - 10 g per liter",
        },
        "Karanja Oil": {
            "cost": 220,
            "quantity": "400 ml per 100 plants",
            "dilution": "2.5% solution - 2.5 ml per liter",
        },
        "Copper Fungicide (Organic)": {
            "cost": 280,
            "quantity": "250 g per 100 plants",
            "dilution": "0.5% solution - 5 g per liter",
        },
        "Potassium Bicarbonate": {
            "cost": 300,
            "quantity": "150 g per 100 plants",
            "dilution": "1% solution - 10 g per liter",
        },
        "Bacillus subtilis": {
            "cost": 350,
            "quantity": "100 g per 100 plants",
            "dilution": "0.1% solution - 1 g per liter",
        },
        "Azadirachtin": {
            "cost": 380,
            "quantity": "200 ml per 100 plants",
            "dilution": "0.3% solution - 3 ml per liter",
        },
        "Trichoderma": {
            "cost": 400,
            "quantity": "500 g per 100 plants",
            "dilution": "0.5% solution - 5 g per liter",
        },
        "Spinosad": {
            "cost": 480,
            "quantity": "100 ml per 100 plants",
            "dilution": "0.02% solution - 0.2 ml per liter",
        },
    },
    "chemical": {
        "Carbendazim (Bavistin)": {
            "cost": 80,
            "quantity": "100 g per 100 plants",
            "dilution": "0.1% solution - 1 g per liter",
        },
        "Copper Oxychloride": {
            "cost": 100,
            "quantity": "200 g per 100 plants",
            "dilution": "0.25% solution - 2.5 g per liter",
        },
        "Mancozeb (Indofil)": {
            "cost": 140,
            "quantity": "150 g per 100 plants",
            "dilution": "0.2% solution - 2 g per liter",
        },
        "Profenofos (Meothrin)": {
            "cost": 150,
            "quantity": "100 ml per 100 plants",
            "dilution": "0.05% solution - 0.5 ml per liter",
        },
        "Chlorothalonil": {
            "cost": 180,
            "quantity": "120 g per 100 plants",
            "dilution": "0.15% solution - 1.5 g per liter",
        },
        "Deltamethrin (Decis)": {
            "cost": 200,
            "quantity": "50 ml per 100 plants",
            "dilution": "0.005% solution - 0.05 ml per liter",
        },
        "Imidacloprid (Confidor)": {
            "cost": 240,
            "quantity": "80 ml per 100 plants",
            "dilution": "0.008% solution - 0.08 ml per liter",
        },
        "Fluconazole (Contaf)": {
            "cost": 350,
            "quantity": "150 ml per 100 plants",
            "dilution": "0.06% solution - 0.6 ml per liter",
        },
        "Tebuconazole (Folicur)": {
            "cost": 320,
            "quantity": "120 ml per 100 plants",
            "dilution": "0.05% solution - 0.5 ml per liter",
        },
        "Thiamethoxam (Actara)": {
            "cost": 290,
            "quantity": "100 g per 100 plants",
            "dilution": "0.04% solution - 0.4 g per liter",
        },
        "Azoxystrobin (Amistar)": {
            "cost": 400,
            "quantity": "80 ml per 100 plants",
            "dilution": "0.02% solution - 0.2 ml per liter",
        },
        "Hexaconazole (Contaf Plus)": {
            "cost": 350,
            "quantity": "100 ml per 100 plants",
            "dilution": "0.04% solution - 0.4 ml per liter",
        },
        "Phosphorous Acid": {
            "cost": 250,
            "quantity": "200 ml per 100 plants",
            "dilution": "0.3% solution - 3 ml per liter",
        },
    },
}

# ================== HELPERS ==================
def extract_json_robust(text: str):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass

    cleaned = text
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1).split("```", 1)[1]
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[2].split("```", 1)[0]

    try:
        return json.loads(cleaned.strip())
    except Exception:
        pass

    import re as _re

    match = _re.search(r"\{[\s\S]*\}", text)
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
    if not isinstance(data, dict):
        return False, "Response is not a dictionary"
    missing = [f for f in required_fields if f not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, "Valid"


def get_type_badge_class(disease_type: str) -> str:
    t = (disease_type or "").lower()
    if "fungal" in t:
        return "type-fungal"
    if "bacterial" in t:
        return "type-bacterial"
    if "viral" in t:
        return "type-viral"
    if "pest" in t:
        return "type-pest"
    if "nutrient" in t:
        return "type-nutrient"
    return "type-healthy"


def get_severity_badge_class(severity: str) -> str:
    s = (severity or "").lower()
    if "healthy" in s or "none" in s:
        return "severity-healthy"
    if "mild" in s:
        return "severity-mild"
    if "moderate" in s:
        return "severity-moderate"
    if "severe" in s:
        return "severity-severe"
    return "severity-moderate"


def get_treatment_info(treatment_type: str, treatment_name: str):
    costs = TREATMENT_COSTS.get(treatment_type, {})
    tname = (treatment_name or "").lower()
    for key, value in costs.items():
        if key.lower() == tname:
            if isinstance(value, dict):
                return value
            return {
                "cost": value,
                "quantity": "As per package",
                "dilution": "Follow label instructions",
            }
    for key, value in costs.items():
        if key.lower() in tname or tname in key.lower():
            if isinstance(value, dict):
                return value
            return {
                "cost": value,
                "quantity": "As per package",
                "dilution": "Follow label instructions",
            }
    # Fallback
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


def calculate_loss_percentage(disease_severity: str, infected_count: int, total_plants: int = 100) -> int:
    severity_loss_map = {
        "healthy": 0,
        "mild": 15,
        "moderate": 40,
        "severe": 70,
    }
    s = (disease_severity or "").lower()
    base_loss = severity_loss_map.get(s, 40)
    if total_plants <= 0:
        infected_ratio = 1.0
    else:
        infected_ratio = min(infected_count / total_plants, 1.0)
    from math import pow

    calculated = int(base_loss * pow(infected_ratio, 0.7))
    return max(min(calculated, 85), base_loss // 2)


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
                "No organic treatments were suggested. You can still enter custom costs on the Cost Calculator page."
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
                "No chemical treatments were suggested. You can still enter custom costs on the Cost Calculator page."
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
                This cost will be auto-filled on the Cost Calculator & ROI page. 
                The other treatment type will be set to Rs 0.
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
            """<div class="info-section"><div class="info-title">Immediate Actions</div>""",
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
        # IMPORTANT: No total cost per plant or total cost for infected plants here
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
        # IMPORTANT: No total cost per plant or total cost for infected plants here
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """<div class="info-section"><div class="info-title">Long-term Prevention</div>""",
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

    # Cost selection UI at the end of AI Plant Doctor page
    render_treatment_selection_ui(
        plant_type=plant_type,
        disease_name=disease_name,
        organic_treatments=organic_treatments,
        chemical_treatments=chemical_treatments,
        default_infected_count=infected_count,
    )

    return organic_total_block, chemical_total_block


# ================== SESSION STATE INIT ==================
if "last_diagnosis" not in st.session_state:
    st.session_state.last_diagnosis = None
if "treatment_selection" not in st.session_state:
    st.session_state.treatment_selection = None
if "confidence_min" not in st.session_state:
    st.session_state.confidence_min = 65

# ================== SIDEBAR NAV ==================
with st.sidebar:
    st.markdown(
        "<h2 style='text-align:center;'>🌿 AI Plant Doctor</h2>",
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigate",
        ["AI Plant Doctor", "Cost Calculator & ROI"],
        index=0,
    )
    st.markdown("---")
    st.markdown(
        "Use **AI Plant Doctor** to get diagnosis and treatment suggestions, "
        "then scroll to the bottom of that page to select infected plants and one treatment. "
        "After that, open **Cost Calculator & ROI**.",
    )

# ================== PAGE: AI Plant Doctor ==================
if page == "AI Plant Doctor":
    st.markdown(
        """
        <div class="header-container">
            <div class="header-title">🌿 AI Plant Doctor</div>
            <div class="header-subtitle">
                Diagnose plant diseases, get precise organic & chemical treatments with quantities,
                and wire them into your cost & ROI calculator.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_main, col_side = st.columns([2, 1])
    with col_main:
        plant_type = st.selectbox(
            "Select your plant",
            list(PLANT_COMMON_DISEASES.keys()),
            index=0,
        )
        infected_count = st.number_input(
            "Approximate number of infected plants (for diagnosis context)",
            min_value=1,
            step=1,
            value=20,
        )
        observation = st.text_area(
            "Describe what you see on leaves, stems, fruits (spots, color, pattern, spread, etc.)",
            height=140,
        )

    with col_side:
        st.markdown(
            """<div class="info-section"><div class="info-title">Tips</div>""",
            unsafe_allow_html=True,
        )
        st.write(
            "- Mention where symptoms started (lower leaves / upper canopy).\n"
            "- Describe color (yellow, brown, black, white growth).\n"
            "- Note weather: humid, rainy, hot, cool.\n"
            "- Mention any chemicals or sprays already used."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        confidence_min = st.slider(
            "Minimum acceptable AI confidence",
            min_value=50,
            max_value=95,
            value=st.session_state.confidence_min,
            step=5,
        )
        st.session_state.confidence_min = confidence_min

    run_btn = st.button("🔍 Analyze Disease")
    if run_btn:
        if not GEMINI_AVAILABLE:
            st.error("GEMINI_API_KEY not configured. Please set it in your environment.")
        else:
            with st.spinner("Analyzing disease with Gemini..."):
                try:
                    model = genai.GenerativeModel("gemini-1.5-pro")
                    prompt = EXPERT_PROMPT_TEMPLATE.format(
                        plant_type=plant_type,
                        common_diseases=PLANT_COMMON_DISEASES[plant_type],
                        user_observation=observation or "No description provided",
                    )
                    response = model.generate_content(prompt)
                    raw_text = response.text if hasattr(response, "text") else str(
                        response
                    )
                    result = extract_json_robust(raw_text)

                    if not result:
                        st.error("Could not parse AI response into JSON. Please try again.")
                    else:
                        is_valid, msg = validate_json_result(result)
                        if not is_valid:
                            st.warning(f"AI response is incomplete: {msg}")

                        confidence = result.get("confidence", 0)
                        if confidence < st.session_state.confidence_min:
                            st.markdown(
                                f"<div class='warning-box'>AI confidence is {confidence}%, "
                                f"which is below your threshold of {st.session_state.confidence_min}%. "
                                f"Please double-check in the field.</div>",
                                unsafe_allow_html=True,
                            )

                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        organic_sum, chemical_sum = render_diagnosis_and_treatments(
                            result=result,
                            plant_type=plant_type,
                            infected_count=infected_count,
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
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    elif st.session_state.last_diagnosis:
        st.markdown(
            """<div class="success-box">
                Showing results from your last diagnosis. You can switch between pages without losing this output.
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

# ================== PAGE: Cost Calculator & ROI ==================
else:
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title">📊 Treatment Cost Calculator & ROI</div>
            <div class="page-subtitle">
                Uses your last AI diagnosis + selected treatment to auto-fill treatment costs.
                The opposite treatment type is automatically set to 0.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    diag = st.session_state.last_diagnosis
    if not diag:
        st.markdown(
            """<div class="warning-box">
                Please run the AI Plant Doctor first to generate a diagnosis and treatments.
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        plant_name = diag.get("plant_type", "Unknown")
        disease_name = diag.get("disease_name", "Unknown")

        selection = st.session_state.treatment_selection
        if selection and isinstance(selection.get("infected_plants"), int):
            infected_count = selection["infected_plants"]
        else:
            infected_count = diag.get("infected_count", 50)

        col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
        with col_d1:
            st.markdown(
                f"""<div class="stat-box">
                        <div class="stat-label">Plant</div>
                        <div class="stat-value">{plant_name}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
        with col_d2:
            st.markdown(
                f"""<div class="stat-box">
                        <div class="stat-label">Disease</div>
                        <div class="stat-value">{disease_name[:12]}...</div>
                    </div>""",
                unsafe_allow_html=True,
            )
        with col_d3:
            st.markdown(
                f"""<div class="stat-box">
                        <div class="stat-label">Severity</div>
                        <div class="stat-value">{diag.get('severity', 'Unknown').title()}</div>
                    </div>""",
                unsafe_allow_html=True,
            )
        with col_d4:
            st.markdown(
                f"""<div class="stat-box">
                        <div class="stat-label">Confidence</div>
                        <div class="stat-value">{diag.get('confidence', 0)}%</div>
                    </div>""",
                unsafe_allow_html=True,
            )
        with col_d5:
            st.markdown(
                f"""<div class="stat-box">
                        <div class="stat-label">Infected Plants</div>
                        <div class="stat-value">{infected_count}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div class="info-section"><div class="info-title">Treatment Costs & Yield Data</div></div>""",
            unsafe_allow_html=True,
        )

        if selection and isinstance(selection.get("total_cost"), int):
            if selection["treatment_type"] == "organic":
                organic_default = selection["total_cost"]
                chemical_default = 0
            else:
                organic_default = 0
                chemical_default = selection["total_cost"]
        else:
            organic_default = int(diag.get("organic_cost", 300) * infected_count)
            chemical_default = int(diag.get("chemical_cost", 200) * infected_count)

        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        with col_i1:
            organic_cost_total = st.number_input(
                "Organic Treatment Cost (Rs) - All Plants",
                value=organic_default,
                min_value=0,
                step=100,
                help=f"Total cost for treating {infected_count} plants",
            )
        with col_i2:
            chemical_cost_total = st.number_input(
                "Chemical Treatment Cost (Rs) - All Plants",
                value=chemical_default,
                min_value=0,
                step=100,
                help=f"Total cost for treating {infected_count} plants",
            )
        with col_i3:
            total_plants = st.number_input(
                "Total plants in field",
                min_value=infected_count,
                value=max(infected_count * 2, infected_count),
                step=10,
            )
        with col_i4:
            price_per_kg = st.number_input(
                "Market price (Rs per kg)",
                min_value=1,
                value=30,
                step=1,
            )

        col_y1, col_y2, col_y3 = st.columns(3)
        with col_y1:
            yield_per_plant = st.number_input(
                "Healthy yield per plant (kg)",
                min_value=0.1,
                value=1.5,
                step=0.1,
            )
        with col_y2:
            severity_loss_pct = calculate_loss_percentage(
                diag.get("severity", "moderate"), infected_count, total_plants
            )
            loss_pct = st.slider(
                "Estimated yield loss without treatment (%)",
                min_value=0,
                max_value=90,
                value=int(severity_loss_pct),
                step=5,
            )
        with col_y3:
            residual_loss = st.slider(
                "Remaining loss after treatment (%)",
                min_value=0,
                max_value=50,
                value=10,
                step=5,
                help="Expected yield loss even after successful treatment",
            )

        if st.button("📈 Calculate ROI"):
            healthy_yield_total = total_plants * yield_per_plant
            yield_without_treatment = healthy_yield_total * (1 - loss_pct / 100)
            yield_with_treatment = healthy_yield_total * (1 - residual_loss / 100)

            revenue_without = yield_without_treatment * price_per_kg
            revenue_with_organic = yield_with_treatment * price_per_kg - organic_cost_total
            revenue_with_chemical = yield_with_treatment * price_per_kg - chemical_cost_total

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown(
                    """<div class="info-section"><div class="info-title">No Treatment</div>""",
                    unsafe_allow_html=True,
                )
                st.write(f"Estimated yield: {yield_without_treatment:.1f} kg")
                st.write(f"Estimated revenue: Rs {revenue_without:,.0f}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_r2:
                st.markdown(
                    """<div class="info-section"><div class="info-title">With Organic Treatment</div>""",
                    unsafe_allow_html=True,
                )
                st.write(f"Estimated yield: {yield_with_treatment:.1f} kg")
                st.write(f"Treatment cost: Rs {organic_cost_total:,.0f}")
                st.write(f"Net revenue: Rs {revenue_with_organic:,.0f}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_r3:
                st.markdown(
                    """<div class="info-section"><div class="info-title">With Chemical Treatment</div>""",
                    unsafe_allow_html=True,
                )
                st.write(f"Estimated yield: {yield_with_treatment:.1f} kg")
                st.write(f"Treatment cost: Rs {chemical_cost_total:,.0f}")
                st.write(f"Net revenue: Rs {revenue_with_chemical:,.0f}")
                st.markdown("</div>", unsafe_allow_html=True)
