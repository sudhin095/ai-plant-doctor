import streamlit as st
from PIL import Image
import io
from google import genai

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Plant Doctor", page_icon="🌿", layout="wide")
st.title("🌿 AI Plant Doctor – Universal Plant Disease Detector")
st.write("Upload a plant leaf image to detect diseases using Google Gemini Vision AI.")

# ---------------------------
# GEMINI CLIENT SETUP
# ---------------------------
client = genai.Client(api_key="YOUR_API_KEY_HERE")   # <-- your key

# ---------------------------
# IMAGE UPLOADER
# ---------------------------
uploaded_file = st.file_uploader("Upload a plant leaf image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=350, caption="Uploaded Leaf Image")

    st.subheader("🔍 AI Diagnosis")

    # Convert image → bytes
    img_bytes_io = io.BytesIO()
    image.save(img_bytes_io, format="PNG")
    img_bytes = img_bytes_io.getvalue()

    # ---------------------------
    # PROMPT
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

    Format neatly.
    """

    # ---------------------------
    # SEND TO GEMINI (NEW API)
    # ---------------------------
    with st.spinner("Diagnosing the leaf..."):
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                {"role": "user", "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_bytes}}
                ]}
            ]
        )

    st.success("Diagnosis Complete!")
    st.write(response.text)
