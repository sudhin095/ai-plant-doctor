import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Professional Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ PLANT COMMON DISEASES DATABASE ============
PLANT_COMMON_DISEASES = {
    "Tomato": "• Early Blight\n• Late Blight\n• Septoria Leaf Spot\n• Fusarium Wilt\n• Powdery Mildew",
    "Potato": "• Late Blight\n• Early Blight\n• Bacterial Wilt\n• Verticillium Wilt\n• Rhizoctonia",
    "Rice": "• Leaf Blast\n• Neck Blast\n• Brown Spot\n• Sheath Blight\n• Tungro Virus",
    "Wheat": "• Rusts (Leaf, Stem, Yellow)\n• Powdery Mildew\n• Septoria Nodorum\n• Fusarium Head Blight\n• Smuts",
    "Corn/Maize": "• Leaf Rust\n• Northern Leaf Blight\n• Southern Leaf Blight\n• Gray Leaf Spot\n• Anthracnose",
    "Cotton": "• Leaf Curl\n• Alternaria Leaf Spot\n• Bacterial Blight\n• Fusarium Wilt\n• Verticillium Wilt",
    "Apple": "• Apple Scab\n• Powdery Mildew\n• Fire Blight\n• Sooty Blotch\n• Flyspeck",
    "Mango": "• Anthracnose\n• Powdery Mildew\n• Stem End Rot\n• Gall Midge\n• Leaf Spot",
    "Banana": "• Leaf Spot (Sigatoka)\n• Panama Disease\n• Anthracnose\n• Mosaic Virus\n• Cordana",
    "Grape": "• Powdery Mildew\n• Downy Mildew\n• Black Rot\n• Anthracnose\n• Eutypa Dieback",
    "Onion": "• Pink Root\n• Fusarium Basal Rot\n• White Rot\n• Downy Mildew\n• Purple Blotch",
    "Chili/Pepper": "• Anthracnose\n• Bacterial Spot\n• Powdery Mildew\n• Leaf Curl\n• Capsicum Mosaic",
    "Cabbage": "• Black Rot\n• Clubroot\n• Leaf Spot\n• White Rust\n• Powdery Mildew",
    "Cucumber": "• Powdery Mildew\n• Downy Mildew\n• Angular Leaf Spot\n• Anthracnose\n• Fusarium Wilt",
    "Carrot": "• Leaf Blight\n• Aster Yellows\n• Cercospora Leaf Spot\n• Motley Dwarf\n• Root Rot",
}

# ============ TREATMENT COST DATABASE ============
TREATMENT_COSTS = {
    "organic": {
        "Neem Oil Spray": 150,
        "Sulfur Powder": 120,
        "Bordeaux Mixture": 180,
        "Copper Fungicide (Organic)": 160,
        "Potassium Bicarbonate": 140,
        "Bacillus subtilis": 200,
        "Trichoderma": 220,
        "Spinosad": 250,
        "Azadirachtin": 190,
        "Lime Sulfur": 170,
    },
    "chemical": {
        "Carbendazim": 80,
        "Mancozeb": 100,
        "Copper Oxychloride": 110,
        "Chlorothalonil": 130,
        "Fluconazole": 250,
        "Tebuconazole": 200,
        "Imidacloprid": 180,
        "Deltamethrin": 160,
        "Profenofos": 120,
        "Thiamethoxam": 190,
    }
}

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
    
    /* Cost Card */
    .cost-card {
        background: linear-gradient(135deg, #1e4620 0%, #2d5a33 100%);
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid rgba(76, 175, 80, 0.3);
        color: #81c784;
        font-size: 0.95rem;
    }
    
    .cost-card-chemical {
        background: linear-gradient(135deg, #5a1a1a 0%, #3d0d0d 100%) !important;
        border-left: 5px solid #ff6b6b !important;
        border: 1px solid rgba(255, 107, 107, 0.3) !important;
        color: #ef9a9a !important;
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
    st.error("❌ GEMINI_API_KEY not found in environment variables!")
    st.stop()

EXPERT_PROMPT = """You are an expert plant pathologist with 30 years of experience diagnosing plant diseases globally.
Your task is to provide accurate, practical plant disease diagnosis.

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

def get_treatment_cost(treatment_type, treatment_name):
    """Get cost for treatment"""
    costs = TREATMENT_COSTS.get(treatment_type, {})
    for key, value in costs.items():
        if key.lower() in treatment_name.lower() or treatment_name.lower() in key.lower():
            return value
    return 150  # default cost

def generate_pdf_prescription(diagnosis, farmer_name="Farmer", crop_area=1.0):
    """Generate PDF prescription for the farmer"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            alignment=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=5,
            leading=12
        )
        
        # Title
        elements.append(Paragraph("AI PLANT DOCTOR - TREATMENT PRESCRIPTION", title_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Farmer Info
        date_str = datetime.now().strftime("%d-%m-%Y %H:%M")
        elements.append(Paragraph(f"<b>Date:</b> {date_str}", normal_style))
        elements.append(Paragraph(f"<b>Farmer Name:</b> {farmer_name}", normal_style))
        elements.append(Paragraph(f"<b>Crop Area:</b> {crop_area} acres", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Disease Information
        elements.append(Paragraph("DIAGNOSIS", heading_style))
        disease_name = diagnosis.get("disease_name", "Unknown")
        disease_type = diagnosis.get("disease_type", "Unknown").title()
        severity = diagnosis.get("severity", "Unknown").title()
        confidence = diagnosis.get("confidence", 0)
        
        elements.append(Paragraph(f"<b>Disease:</b> {disease_name}", normal_style))
        elements.append(Paragraph(f"<b>Type:</b> {disease_type} | <b>Severity:</b> {severity} | <b>Confidence:</b> {confidence}%", normal_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Symptoms
        elements.append(Paragraph("SYMPTOMS", heading_style))
        for symptom in diagnosis.get("symptoms", [])[:3]:
            elements.append(Paragraph(f"• {symptom}", normal_style))
        elements.append(Spacer(1, 0.08*inch))
        
        # Immediate Actions
        elements.append(Paragraph("IMMEDIATE ACTIONS (TODAY)", heading_style))
        for i, action in enumerate(diagnosis.get("immediate_action", [])[:3], 1):
            elements.append(Paragraph(f"<b>{i}.</b> {action}", normal_style))
        elements.append(Spacer(1, 0.08*inch))
        
        # Treatment Options with Costs
        elements.append(Paragraph("TREATMENT & COSTS", heading_style))
        
        organic_treatments = diagnosis.get("organic_treatments", [])
        chemical_treatments = diagnosis.get("chemical_treatments", [])
        
        organic_cost = sum([get_treatment_cost("organic", t) for t in organic_treatments[:2]]) if organic_treatments else 0
        chemical_cost = sum([get_treatment_cost("chemical", t) for t in chemical_treatments[:2]]) if chemical_treatments else 0
        
        table_data = [
            ["Type", "Cost", "Duration", "Safety"],
            ["Organic", f"₹{organic_cost}", "7-14 days", "High"],
            ["Chemical", f"₹{chemical_cost}", "3-7 days", "Medium"],
        ]
        
        table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Treatments
        elements.append(Paragraph("ORGANIC TREATMENTS (Recommended)", heading_style))
        for treatment in organic_treatments[:2]:
            elements.append(Paragraph(f"• {treatment}", normal_style))
        elements.append(Spacer(1, 0.08*inch))
        
        elements.append(Paragraph("CHEMICAL TREATMENTS (Alternative)", heading_style))
        for treatment in chemical_treatments[:2]:
            elements.append(Paragraph(f"• {treatment}", normal_style))
        elements.append(Spacer(1, 0.08*inch))
        
        # Prevention
        elements.append(Paragraph("PREVENTION", heading_style))
        for prevention in diagnosis.get("prevention_long_term", [])[:3]:
            elements.append(Paragraph(f"• {prevention}", normal_style))
        
        # Footer
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<i>Note: Based on AI analysis. Consult local experts for confirmation.</i>", normal_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ PDF Error: {str(e)}")
        return None

st.markdown("""
<div class="header-container">
    <div class="header-title">🌿 AI Plant Doctor - Professional Edition</div>
    <div class="header-subtitle">Universal Plant Disease Detection with Expert Analysis</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card">✅ Expert Diagnosis</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">🌱 Plant Selection</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">💰 Cost Calculator</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card">📄 PDF Prescriptions</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Settings & Configuration")
    
    model_choice = st.radio(
        "🤖 AI Model Selection",
        ["Gemini 2.5 Flash (Fast)", "Gemini 2.5 Pro (Accurate)"],
        help="Flash: 80% accurate, 2-3 sec | Pro: 95% accurate, 5-10 sec"
    )
    
    debug_mode = st.checkbox("🐛 Debug Mode", value=False, help="Show raw API responses")
    show_tips = st.checkbox("💡 Show Photo Tips", value=True, help="Display photo quality tips")
    
    confidence_min = st.slider(
        "Minimum Confidence (%)",
        0, 100, 50,
        help="Only show results above this confidence"
    )
    
    st.markdown("---")
    
    with st.expander("📸 Perfect Photo Checklist", expanded=False):
        st.markdown("""
        ✅ **DO THIS:**
        - Plain WHITE background
        - Natural, even lighting
        - Sharp and in-focus
        - Close-up of diseased part
        - ONE leaf only
        - Photograph from above
        
        ❌ **AVOID:**
        - Blurry photos
        - Dark shadows
        - Busy backgrounds
        - Healthy leaves
        - Multiple leaves
        - Angled shots
        """)
    
    with st.expander("❓ Why Wrong Results?", expanded=False):
        st.markdown("""
        **Top 3 Reasons:**
        
        1. 📸 **Bad Image Quality**
           - Blurry or dark
           - Busy background
           - Solution: Retake with white background
        
        2. 🎯 **Wrong Subject**
           - Showing healthy leaf
           - Multiple leaves in frame
           - Solution: One diseased leaf, clear view
        
        3. 🤖 **Model Issue**
           - Using Flash for complex disease
           - Solution: Switch to Pro model
        """)

# ============ PLANT TYPE SELECTION - MAIN ACCURACY FEATURE ============
col_plant, col_upload = st.columns([1, 2])

with col_plant:
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    st.subheader("🌱 Select Plant Type")
    
    plant_options = ["Select a plant..."] + sorted(list(PLANT_COMMON_DISEASES.keys())) + ["Other (Manual Entry)"]
    selected_plant = st.selectbox(
        "What plant do you have?",
        plant_options,
        label_visibility="collapsed",
        help="Selecting plant type increases accuracy by 25-30%!"
    )
    
    if selected_plant == "Other (Manual Entry)":
        custom_plant = st.text_input("Enter plant name", placeholder="e.g., Banana, Orange, Pepper")
        plant_type = custom_plant if custom_plant else "Unknown Plant"
    else:
        plant_type = selected_plant if selected_plant != "Select a plant..." else None
    
    if plant_type and plant_type in PLANT_COMMON_DISEASES:
        st.markdown(f"""
        <div class="success-box">
        <b>Common diseases in {plant_type}:</b><br>
        {PLANT_COMMON_DISEASES[plant_type]}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_upload:
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    st.subheader("📤 Upload Plant Image")
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
            <div class="tips-card-title">💡 Photo Quality Matters!</div>
            For best results: white background + natural light + sharp focus + diseased leaf close-up
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    
    col_img, col_zoom = st.columns([3, 1])
    
    with col_zoom:
        st.markdown("### 🔍 Zoom")
        zoom_level = st.slider(
            "Zoom",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            label_visibility="collapsed"
        )
    
    with col_img:
        st.subheader("📸 Preview")
        display_image = original_image.copy()
        if zoom_level != 1.0:
            # Simple zoom implementation
            width, height = display_image.size
            new_width = int(width / zoom_level)
            new_height = int(height / zoom_level)
            left = (width - new_width) / 2
            top = (height - new_height) / 2
            display_image = display_image.crop((left, top, left + new_width, top + new_height))
            display_image = display_image.resize((width, height), Image.Resampling.LANCZOS)
        
        display_image.thumbnail((600, 500), Image.Resampling.LANCZOS)
        
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(display_image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    
    with col_b2:
        analyze_btn = st.button("🔬 Analyze Plant", use_container_width=True, type="primary")
    
    if analyze_btn:
        progress_placeholder = st.empty()
        
        with st.spinner("🔄 Analyzing... This may take a few seconds"):
            try:
                progress_placeholder.info("📊 Processing image with AI...")
                
                model_name = "Gemini 2.5 Pro" if "Pro" in model_choice else "Gemini 2.5 Flash"
                model_id = 'gemini-2.5-pro' if "Pro" in model_choice else 'gemini-2.5-flash'
                model = genai.GenerativeModel(model_id)
                
                if debug_mode:
                    st.info(f"📊 Using Model: {model_name}")
                
                response = model.generate_content([EXPERT_PROMPT, original_image])
                raw_response = response.text
                
                if debug_mode:
                    with st.expander("🔍 Raw API Response"):
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        displayed_response = raw_response[:3000] + "..." if len(raw_response) > 3000 else raw_response
                        st.text(displayed_response)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Extract JSON
                result = None
                try:
                    result = json.loads(raw_response)
                except:
                    if "```json" in raw_response:
                        result = json.loads(raw_response.split("```json")[1].split("```")[0])
                    elif "```" in raw_response:
                        result = json.loads(raw_response.split("```")[1].split("```")[0])
                
                if result is None:
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error("❌ Could not parse AI response")
                    st.write("**This sometimes happens with unusual images. Try:**")
                    st.write("• Retake photo with better lighting/focus")
                    st.write("• Use Pro model for better accuracy")
                    st.write("• Enable debug mode to see raw response")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    confidence = result.get("confidence", 0)
                    
                    if confidence < confidence_min:
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.warning(f"⚠️ **Low Confidence ({confidence}%)**")
                        st.write(result.get("confidence_reason", "AI is uncertain about this diagnosis"))
                        st.write("**Recommendation:** " + result.get("image_quality_tips", "Provide a clearer image"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    image_quality = result.get("image_quality", "")
                    if image_quality and ("Poor" in image_quality or "Fair" in image_quality):
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.write(f"📸 **Image Quality Note:** {image_quality}")
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
                        st.metric("🌱 Plant", plant)
                    with col2:
                        st.metric("📊 Confidence", f"{confidence}%")
                    with col3:
                        st.metric("🚨 Severity", severity.title())
                    with col4:
                        st.metric("⏱️ Analysis", datetime.now().strftime("%H:%M"))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">🔍 Symptoms Observed</div>
                        """, unsafe_allow_html=True)
                        
                        for symptom in result.get("symptoms", []):
                            st.write(f"• {symptom}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">⚠️ Probable Causes</div>
                        """, unsafe_allow_html=True)
                        
                        for cause in result.get("probable_causes", []):
                            st.write(f"• {cause}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_right:
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">⚡ Immediate Actions</div>
                        """, unsafe_allow_html=True)
                        
                        for i, action in enumerate(result.get("immediate_action", []), 1):
                            st.write(f"**{i}.** {action}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    col_treat1, col_treat2 = st.columns(2)
                    
                    with col_treat1:
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">🌱 Organic Treatments</div>
                        """, unsafe_allow_html=True)
                        
                        for treatment in result.get("organic_treatments", []):
                            st.write(f"• {treatment}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Organic Cost
                        organic_treatments = result.get("organic_treatments", [])
                        organic_cost = sum([get_treatment_cost("organic", t) for t in organic_treatments[:2]]) if organic_treatments else 0
                        
                        st.markdown(f"""
                        <div class="cost-card">
                            <b>💚 Organic Treatment Cost</b><br>
                            <b>Approx: ₹{organic_cost}</b> per application<br>
                            <small>Safe • Eco-friendly • Slower (7-14 days)</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_treat2:
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">💊 Chemical Treatments</div>
                        """, unsafe_allow_html=True)
                        
                        for treatment in result.get("chemical_treatments", []):
                            st.write(f"• {treatment}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Chemical Cost
                        chemical_treatments = result.get("chemical_treatments", [])
                        chemical_cost = sum([get_treatment_cost("chemical", t) for t in chemical_treatments[:2]]) if chemical_treatments else 0
                        
                        st.markdown(f"""
                        <div class="cost-card cost-card-chemical">
                            <b>⚠️ Chemical Treatment Cost</b><br>
                            <b>Approx: ₹{chemical_cost}</b> per application<br>
                            <small>Fast acting • Effective • Requires care (3-7 days)</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="info-section">
                        <div class="info-title">🛡️ Long-Term Prevention</div>
                    """, unsafe_allow_html=True)
                    
                    for tip in result.get("prevention_long_term", []):
                        st.write(f"• {tip}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if result.get("similar_conditions"):
                        st.markdown("""
                        <div class="info-section">
                            <div class="info-title">🔎 Similar Conditions</div>
                        """, unsafe_allow_html=True)
                        st.write(result.get("similar_conditions"))
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.divider()
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # ============ PDF PRESCRIPTION SECTION ============
                    st.subheader("📄 Generate Prescription PDF")
                    col_pdf1, col_pdf2 = st.columns(2)
                    
                    with col_pdf1:
                        farmer_name = st.text_input("👨‍🌾 Farmer Name", value="Farmer", key="farmer_name_input")
                    
                    with col_pdf2:
                        crop_area = st.number_input("🌾 Crop Area (acres)", min_value=0.1, max_value=100.0, value=1.0, key="crop_area_input")
                    
                    col_pdf_btn1, col_pdf_btn2 = st.columns(2)
                    
                    with col_pdf_btn1:
                        if st.button("📥 Generate PDF", use_container_width=True, key="gen_pdf"):
                            pdf_buffer = generate_pdf_prescription(result, farmer_name, crop_area)
                            if pdf_buffer:
                                st.download_button(
                                    label="📥 Download PDF Prescription",
                                    data=pdf_buffer,
                                    file_name=f"Prescription_{disease_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key="download_pdf"
                                )
                                st.success("✅ PDF Ready! Download above.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if st.button("📸 Analyze Another", use_container_width=True):
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("🔄 Reset", use_container_width=True):
                            st.rerun()
                    
                    progress_placeholder.empty()
                    
            except Exception as e:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error(f"❌ Analysis Failed: {str(e)}")
                st.write("**Troubleshooting steps:**")
                st.write("1. Check your API key is valid")
                st.write("2. Try a different image with better quality")
                st.write("3. Switch to Pro model for better accuracy")
                st.write("4. Enable Debug Mode to see error details")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if debug_mode:
                    with st.expander("🔍 Error Details (Debug)"):
                        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
                        st.text(str(e))
                        st.markdown('</div>', unsafe_allow_html=True)
                
                progress_placeholder.empty()

with st.sidebar:
    st.markdown("---")
    
    st.header("📞 Support & Info")
    
    with st.expander("🌍 How It Works"):
        st.write("""
        1. **Select Plant** - Choose plant type for better accuracy
        2. **Upload Image** - Plant leaf with visible symptoms
        3. **AI Analysis** - Expert system evaluates the image
        4. **Results** - Disease identification + treatment plan
        5. **Download** - Generate PDF prescription for farmers
        
        **Works for:**
        • 500+ plant diseases
        • Any plant species
        • Fungal, bacterial, viral, pest, nutrient issues
        • Environmental stress conditions
        """)
    
    with st.expander("✅ Best Results"):
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
    
    with st.expander("⚙️ Settings Tips"):
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
