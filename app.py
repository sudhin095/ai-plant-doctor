import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
from datetime import datetime
import re

st.set_page_config(
    page_title="🌿 AI Plant Doctor - Smart Edition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ANIMATED LEAF BACKGROUND ---
# This HTML/CSS creates the falling leaves animation.
st.markdown("""
<div id="leaf-container">
    <div class="leaf">🌿</div>
    <div class="leaf">🍃</div>
    <div class="leaf">🌿</div>
    <div class="leaf">🍃</div>
    <div class="leaf">🌿</div>
    <div class="leaf">🍃</div>
    <div class="leaf">🌿</div>
    <div class="leaf">🍃</div>
    <div class="leaf">🌿</div>
    <div class="leaf">🍃</div>
</div>
""", unsafe_allow_html=True)


# --- UPDATED STYLES (GREEN THEME & ANIMATIONS) ---
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* --- Leaf Animation --- */
    #leaf-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1; /* Place behind all content */
        overflow: hidden;
        pointer-events: none; /* Allow clicks to pass through */
    }

    .leaf {
        position: absolute;
        top: -100px; /* Start off-screen */
        font-size: 2rem;
        color: #4caf50;
        opacity: 0.6;
        
        /* Two animations: one for falling, one for swaying */
        animation-name: fall, sway;
        animation-duration: 12s, 3s;
        animation-timing-function: linear, ease-in-out;
        animation-iteration-count: infinite, infinite;
        animation-play-state: running, running;
    }

    /* Randomize animation delays and positions */
    .leaf:nth-of-type(1) { left: 10%; animation-delay: 0s, 0s; font-size: 1.5rem; }
    .leaf:nth-of-type(2) { left: 20%; animation-delay: -2s, -1s; color: #66bb6a; }
    .leaf:nth-of-type(3) { left: 30%; animation-delay: -5s, -0.5s; font-size: 1.8rem; }
    .leaf:nth-of-type(4) { left: 40%; animation-delay: -8s, -2s; color: #81c784; }
    .leaf:nth-of-type(5) { left: 50%; animation-delay: -10s, -1.5s; font-size: 1.6rem; }
    .leaf:nth-of-type(6) { left: 60%; animation-delay: -12s, -3s; color: #66bb6a; }
    .leaf:nth-of-type(7) { left: 70%; animation-delay: -15s, -2.5s; font-size: 1.7rem; }
    .leaf:nth-of-type(8) { left: 80%; animation-delay: -18s, -1s; color: #81c784; }
    .leaf:nth-of-type(9) { left: 90%; animation-delay: -20s, -0.5s; font-size: 1.5rem; }
    .leaf:nth-of-type(10) { left: 5%; animation-delay: -22s, -2s; color: #4caf50; }

    /* Keyframe for falling */
    @keyframes fall {
        0% {
            top: -10%;
            transform: rotate(0deg);
        }
        100% {
            top: 110%;
            transform: rotate(180deg);
        }
    }

    /* Keyframe for swaying side-to-side */
    @keyframes sway {
        0% {
            transform: translateX(0px) rotate(0deg);
        }
        50% {
            transform: translateX(40px) rotate(20deg);
        }
        100% {
            transform: translateX(0px) rotate(0deg);
        }
    }
    
    /* --- General Fade-in Animation --- */
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Apply animation to main elements */
    .header-container, .feature-card, .upload-container, .result-container {
        animation: slideUp 0.6s ease-out forwards;
    }

    /* Stagger feature cards for a nice effect */
    .feature-card:nth-of-type(1) { animation-delay: 0.1s; }
    .feature-card:nth-of-type(2) { animation-delay: 0.2s; }
    .feature-card:nth-of-type(3) { animation-delay: 0.3s; }
    .feature-card:nth-of-type(4) { animation-delay: 0.4s; }
    
    
    /* --- GREEN THEME STYLES --- */

    /* Main background */
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #2a403d 0%, #1e302c 100%);
        color: #e8f5e9; /* Light green text */
    }
    
    /* Text color */
    p, span, div, label {
        color: #e8f5e9;
    }
    
    /* Header Styles */
    .header-container {
        background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
        padding: 40px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(102, 187, 106, 0.3);
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
        color: #c8e6c9; /* Light green */
        text-align: center;
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        transition: transform 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6);
    }
    
    /* Upload Container */
    .upload-container {
        background: rgba(46, 125, 50, 0.1); /* Translucent green */
        padding: 30px;
        border-radius: 15px;
        border: 2px dashed #81c784; /* Lighter green dash */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        margin: 20px 0;
    }
    
    /* Result Container */
    .result-container {
        background: rgba(46, 125, 50, 0.1); /* Translucent green */
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin: 20px 0;
        border: 1px solid rgba(102, 187, 106, 0.2);
    }
    
    /* Disease Header */
    .disease-header {
        background: linear-gradient(135deg, #ff8a65 0%, #f4511e 100%); /* Contrasting color for alert */
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(244, 81, 30, 0.5);
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
        background: rgba(67, 160, 71, 0.1); /* Translucent dark green */
        border-left:
