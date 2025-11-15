import streamlit as st
from PIL import Image
import io
import google.generativeai as genai
import tempfile

# ---------------------------
# STREAMLIT PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Plant Doctor", page_icon="🌿", layout="wide")
st.title("🌿 AI Plant Doctor – Universal Plant Disease Detector")
st.write("Upload a plant leaf image to detect diseases using Google Gemini Vision AI.")

# ---------------------------
# GEMINI CONFIG
# ---------------------------
genai.configure(api_key="YOUR_API_KEY_HERE")

model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------
# IMAGE UPLOADER
# ---------------------------
uploaded_file = st.file_uploader("Upload a plant leaf image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=350, caption="Uploaded Leaf Image")

    st.subheader("🔍 AI Diagnosis")

    # ---------------------------
    # SAVE IMAGE TO A TEMP FILE
    # ---------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image.save(tmp.name, format="PNG")
        temp_path = tmp.name

    # ---------------------------
    # UPLOAD IMAGE (OLD SDK FORMAT)
    # ---------------------------
    with st.spinner("Uploading image..."):
        uploaded = genai.upload_file(path=temp_path)

    # ---------------------------
    # PROMPT
    # ---------------------------
    prompt = """
    You are a plant disease expert. Analyze the leaf image and provide:
    - Plant Name
    - Disease Name or 'Healthy'
    - Severity
    - Likely Cause
    - Treatment
    - Organic Remedies
    - Prevention Tips
    """

    # ---------------------------
    # SEND TO GEMINI - PASS FILE REFERENCE
    # ---------------------------
    with st.spinner("Diagnosing the leaf..."):
        response = model.generate_content([prompt, uploaded])

    st.success("Diagnosis Complete!")
    st.write(response.text)
