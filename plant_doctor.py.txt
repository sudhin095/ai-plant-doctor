import streamlit as st
from PIL import Image
import google.generativeai as genai
import io

# ---------------------------
# CONFIGURE THE STREAMLIT PAGE
# ---------------------------
st.set_page_config(page_title="AI Plant Doctor", page_icon="🌿", layout="wide")
st.title("🌿 AI Plant Doctor – Universal Plant Disease Detector")
st.write("Upload a plant leaf image to detect diseases using Google Gemini Vision AI.")

# ---------------------------
# CONFIGURE GEMINI API
# ---------------------------
GEMINI_API_KEY = "AIzaSyAGalJ5dy6xxDxLPcvlvzB5KxpVdVEzcRc"  # <-- paste your key here
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# ---------------------------
# IMAGE UPLOADER
# ---------------------------
uploaded_file = st.file_uploader("Upload a plant leaf image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=350, caption="Uploaded Leaf Image")

    st.subheader("🔍 AI Diagnosis")

    # Convert image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    # ---------------------------
    # PROMPT FOR GEMINI
    # ---------------------------
    prompt = """
    You are an expert plant disease identification AI.
    Analyze the leaf image and provide:

    1. Plant Name
    2. Disease Name (or say Healthy)
    3. Severity (Low / Medium / High)
    4. Likely Cause
    5. Step-by-step Treatment
    6. Organic/Natural Remedies
    7. Prevention Tips

    Give a clean and readable explanation.
    """

    # ---------------------------
    # SEND TO GEMINI VISION
    # ---------------------------
    with st.spinner("Diagnosing the leaf..."):
        response = model.generate_content([prompt, img_bytes])

    st.success("Diagnosis Complete!")
    st.write(response.text)
