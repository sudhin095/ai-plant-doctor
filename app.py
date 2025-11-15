import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="🌿 AI Plant Doctor", page_icon="🌿", layout="wide")

st.title("🌿 AI Plant Doctor - Universal Disease Detector")
st.markdown("### Works for ANY Plant Species!")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("✓ No Training Required")
with col2:
    st.info("✓ 500+ Diseases")
with col3:
    st.info("✓ Instant Results")

uploaded_file = st.file_uploader("Upload a plant leaf image", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", width=400)
    
    if st.button("🔍 Analyze Plant", type="primary"):
        with st.spinner("Analyzing plant..."):
            prompt = """
            Analyze this plant leaf image for diseases. Provide:
            
            1. Plant species (if identifiable)
            2. Disease name (or "Healthy Plant")
            3. Disease type (fungal/bacterial/viral/pest/nutrient/healthy)
            4. Severity (mild/moderate/severe/none)
            5. Confidence score (0-100)
            6. Visible symptoms
            7. Possible causes
            8. Treatment recommendations (organic and chemical)
            9. Prevention tips
            
            Format as clear sections with bullet points.
            """
            
            response = model.generate_content([prompt, image])
            
            st.success("✅ Analysis Complete!")
            st.markdown(response.text)

with st.sidebar:
    st.header("ℹ️ About")
    st.write("Uses Google Gemini Vision AI - no training needed!")
    st.header("📊 Free Tier")
    st.write("1,500 analyses per day FREE")
