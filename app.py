import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw
import os
import json
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="🌿 AI Plant Doctor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR PREMIUM DESIGN
# ============================================================================

st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Styles */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
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
        color: #e0e7ff;
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
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    /* Upload Section */
    .upload-container {
        background: white;
        padding: 30px;
        border-
