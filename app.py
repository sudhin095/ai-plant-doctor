import streamlit as st
from PIL import Image
import io
import google.generativeai as genai

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Plant Doctor", page_icon="🌿", layout="wide")
st.title("🌿 AI Plant Doctor – Universal Plant Disease Detector")
st.write("Upload a plant leaf image to detect diseases using Google Gemini Vision AI.")

# ---------------------------
# GEMINI SETUP
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

    # Convert image to bytes
    img_bytes_io = io.BytesIO()
    image.save(img_bytes_io, format="PNG")
    img_bytes = img_bytes_io.getvalue()

    prompt = """
    You are a plant disease expert.
    Analyze the leaf image and provide:

    - Plant Name
    - Disease Name (or say 'Healthy')
    - Severity Level
    - Likely Cause
    - Treatment Steps
    - Organic Remedies
    - Prevention Tips

    Give a short and clear structured answer.
    """

    with st.spinner("Diagnosing the leaf..."):
        response = model.generate_content(
            [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_bytes
                            }
                        }
                    ]
                }
            ]
        )

    st.success("Diagnosis Complete!")
    st.write(response.text)
