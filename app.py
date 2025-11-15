import streamlit as st
from PIL import Image
import io
import google.generativeai as genai

# ---------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Plant Doctor", page_icon="🌿", layout="wide")
st.title("🌿 AI Plant Doctor – Universal Plant Disease Detector")
st.write("Upload a plant leaf image to detect diseases using Google Gemini Vision AI.")

# ---------------------------
# GEMINI SETUP (PUT YOUR KEY)
# ---------------------------
genai.configure(api_key="AIzaSyCum7bIDBLFAynHfwOv2DLJEUoym89eI5k")

# Stable & Supported Model on v1beta
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# ---------------------------
# IMAGE UPLOADER
# ---------------------------
uploaded_file = st.file_uploader("Upload a plant leaf image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=350, caption="Uploaded Leaf Image")

    st.subheader("🔍 AI Diagnosis")

    # Convert image to bytes (PNG always works)
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_bytes = img_buffer.getvalue()

    # ---------------------------
    # PROMPT
    # ---------------------------
    prompt = """
    You are a plant disease expert.
    Analyze the leaf image and provide the following:

    1. Plant Name
    2. Disease Name (or say "Healthy")
    3. Severity Level (Low / Medium / High)
    4. Likely Cause
    5. Step-by-step Treatment
    6. Natural/Organic Remedies
    7. Prevention Tips

    Provide the answer in clean bullet points.
    "
