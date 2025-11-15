import streamlit as st
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

# Load pretrained model (example .h5 file from PlantVillage)
model = load_model("plant_disease_model.h5")

class_names = [
    "Apple Scab", "Apple Black Rot", "Healthy", "Potato Early Blight",
    "Potato Late Blight", "Tomato Leaf Mold", "Tomato Septoria Leaf Spot"
    # Add all your classes here
]

st.title("🌿 AI Plant Doctor (Free Version)")

uploaded_file = st.file_uploader("Upload a plant leaf image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Leaf Image", width=300)

    st.write("🔍 Detecting disease...")
    img = image.resize((128, 128))  # Resize as per model input
    img_array = np.expand_dims(np.array(img)/255.0, axis=0)

    prediction = model.predict(img_array)
    class_idx = np.argmax(prediction)
    st.success(f"Detected: {class_names[class_idx]}")

    # Optional: add remedies / prevention tips
    remedies = {
        "Apple Scab": "Remove infected leaves, apply fungicide.",
        "Healthy": "No action needed.",
        "Potato Early Blight": "Use crop rotation, remove affected leaves."
    }
    st.write(remedies.get(class_names[class_idx], "No tips available."))
