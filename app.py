# 🌱 AI Educational Assistant + Plant Recognition
# app_plants.py - Updated version with plant identification

import streamlit as st
import json
import random
import re
from collections import defaultdict

# Page configuration
st.set_page_config(
    page_title="AI Educational & Plant Recognition Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {padding: 2rem;}
    .free-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 15px 25px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
    .success-box {background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;}
    .info-box {background: #d1ecf1; padding: 15px; border-radius: 8px; border-left: 4px solid #17a2b8;}
    .plant-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'plant_data' not in st.session_state:
    st.session_state.plant_data = None

# Sample plant database
PLANT_DATABASE = {
    "Tomato": {
        "scientific_name": "Solanum lycopersicum",
        "family": "Solanaceae",
        "description": "A widely cultivated plant with edible red fruits used in cooking and as a source of vitamins.",
        "uses": ["Cooking", "Nutrition", "Medicine"],
        "care": ["Full sunlight (6-8 hours daily)", "Well-drained soil", "Regular watering"],
        "growth_time": "60-85 days"
    },
    "Spinach": {
        "scientific_name": "Spinacia oleracea",
        "family": "Amaranthaceae",
        "description": "A leafy green vegetable rich in iron and nutrients, commonly used in salads and cooking.",
        "uses": ["Salads", "Cooking", "Nutrition"],
        "care": ["Partial shade", "Moist soil", "Cool climate"],
        "growth_time": "40-50 days"
    },
    "Basil": {
        "scientific_name": "Ocimum basilicum",
        "family": "Lamiaceae",
        "description": "An aromatic herb with strong fragrance used in cooking, especially in Italian cuisine.",
        "uses": ["Cooking", "Garnish", "Aromatherapy"],
        "care": ["Sunlight (6-8 hours)", "Well-drained soil", "Warm temperature"],
        "growth_time": "30-40 days"
    },
    "Mint": {
        "scientific_name": "Mentha piperita",
        "family": "Lamiaceae",
        "description": "A refreshing herb with cooling properties used in beverages, desserts, and medicinal preparations.",
        "uses": ["Beverages", "Desserts", "Medicine"],
        "care": ["Partial shade", "Moist soil", "Hardy perennial"],
        "growth_time": "10-12 days to first harvest"
    },
    "Cucumber": {
        "scientific_name": "Cucumis sativus",
        "family": "Cucurbitaceae",
        "description": "A creeping vine with long green fruits, commonly eaten fresh in salads or pickled.",
        "uses": ["Salads", "Pickling", "Nutrition"],
        "care": ["Full sunlight", "Warm temperature", "Trellis support"],
        "growth_time": "50-70 days"
    },
    "Rose": {
        "scientific_name": "Rosa spp.",
        "family": "Rosaceae",
        "description": "A flowering plant known for its beautiful blooms, used in gardens and as cut flowers.",
        "uses": ["Ornamental", "Cut flowers", "Fragrance"],
        "care": ["Full sunlight (6+ hours)", "Well-drained soil", "Regular pruning"],
        "growth_time": "First bloom: 12-16 weeks"
    },
    "Sunflower": {
        "scientific_name": "Helianthus annuus",
        "family": "Asteraceae",
        "description": "A tall plant with large yellow flowers that track the sun, producing seeds and oil.",
        "uses": ["Ornamental", "Seeds", "Oil production"],
        "care": ["Full sunlight", "Well-drained soil", "Support for tall varieties"],
        "growth_time": "70-100 days"
    },
    "Lavender": {
        "scientific_name": "Lavandula angustifolia",
        "family": "Lamiaceae",
        "description": "A fragrant flowering plant used in aromatherapy, perfumes, and culinary applications.",
        "uses": ["Aromatherapy", "Culinary", "Ornamental"],
        "care": ["Full sunlight", "Well-drained soil", "Low maintenance"],
        "growth_time": "12-16 weeks"
    }
}

# Header
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652126.png", width=80)
with col2:
    st.title("🌱 AI Educational & Plant Assistant")
    st.markdown("*Summarize • Quiz • Learn • Identify Plants*")

st.markdown('<div class="free-badge">🌿 Educational Tool + Plant Recognition • Completely FREE 🌿</div>', unsafe_allow_html=True)

st.divider()

# Main tabs - UPDATED with Plant Recognition
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📥 Input", "🌿 Plant ID", "📝 Summary", "❓ Quiz", "🧠 Mind Map"])

# ============ TAB 1: INPUT (EDUCATIONAL CONTENT) ============
with tab1:
    st.header("📥 Input Educational Content")
    
    input_method = st.radio(
        "Choose input type:",
        ["📄 Text Input"],
        horizontal=True
    )

    st.subheader("Paste Educational Content")
    text_input = st.text_area(
        "Enter your text (minimum 50 words):",
        height=250,
        placeholder="Paste lecture notes, articles, research papers, or any educational content here..."
    )
    
    if st.button("✅ Process Text", use_container_width=True, type="primary"):
        if text_input:
            word_count = len(text_input.split())
            if word_count >= 50:
                st.session_state.processed_data = {
                    'content': text_input,
                    'source': f"Text Input ({word_count} words)",
                    'type': 'text'
                }
                st.success(f"✅ Text processed! ({word_count} words)")
            else:
                st.error(f"❌ Text too short. Need at least 50 words, you have {word_count}")
        else:
            st.error("❌ Please enter some text")

    # Processing options
    if st.session_state.processed_data:
        st.divider()
        st.subheader("⚙️ Customization Options")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            summary_points = st.slider("Summary bullet points:", 3, 10, 5)
        with col2:
            num_questions = st.slider("Quiz questions:", 3, 8, 5)
        with col3:
            difficulty = st.selectbox("Question difficulty:", ["Easy", "Medium", "Hard", "Mixed"])
        
        if st.button("🚀 Generate Summary, Quiz & Mind Map", use_container_width=True, type="primary"):
            with st.spinner("🧠 Processing with AI models..."):
                try:
                    content = st.session_state.processed_data['content']
                    
                    # Summarization
                    st.info("📝 Generating summary...")
                    
                    try:
                        from transformers import pipeline
                        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
                        
                        sentences = re.split(r'(?<=[.!?])\s+', content)
                        chunks = []
                        current_chunk = ""
                        
                        for sentence in sentences:
                            if len(current_chunk) + len(sentence) < 1024:
                                current_chunk += " " + sentence
                            else:
                                if current_chunk.strip():
                                    chunks.append(current_chunk.strip())
                                current_chunk = sentence
                        
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        
                        summaries = []
                        for chunk in chunks:
                            if len(chunk.split()) >= 50:
                                try:
                                    summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
                                    summaries.append(summary[0]['summary_text'])
                                except:
                                    pass
                        
                        bullets = []
                        for summary in summaries:
                            summary = summary.replace('\n', ' ')
                            sents = re.split(r'[.!?]+', summary)
                            for sent in sents:
                                sent = sent.strip()
                                if len(sent) > 10:
                                    sent = sent[0].upper() + sent[1:] if sent else sent
                                    if sent not in bullets:
                                        bullets.append(f"• {sent}")
                    except:
                        bullets = ["• Unable to load summarization model. Using sample content instead."]
                    
                    # Quiz generation
                    st.info("❓ Generating quiz questions...")
                    
                    try:
                        import spacy
                        nlp = spacy.load("en_core_web_sm")
                        doc = nlp(content)
                        
                        entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
                        entities = list(set(entities))
                    except:
                        entities = []
                    
                    quiz = []
                    sample_questions = [
                        f"What is the significance of '{{}}'?",
                        f"Which concept refers to '{{}}'?",
                        f"'{{}' is associated with:",
                        f"What does '{}' mean?",
                        f"Which statement best describes '{{}}'?",
                    ]
                    
                    for i, entity in enumerate(entities[:num_questions]):
                        if not entity or len(entity) < 2:
                            continue
                        
                        question = random.choice(sample_questions).format(entity)
                        other_entities = [e for e in entities if e != entity]
                        distractors = random.sample(other_entities, min(3, len(other_entities)))
                        
                        while len(distractors) < 3:
                            distractors.append(f"Option {len(distractors) + 1}")
                        
                        options = [entity] + distractors
                        random.shuffle(options)
                        correct_idx = options.index(entity)
                        
                        quiz.append({
                            "id": i + 1,
                            "question": question,
                            "options": options,
                            "correct_option": correct_idx,
                            "difficulty": difficulty.lower(),
                            "explanation": f"The correct answer is: {entity}"
                        })
                    
                    # Mind map
                    st.info("🧠 Creating mind map...")
                    
                    concepts = defaultdict(list)
                    try:
                        for ent in doc.ents:
                            if ent.label_ == "PERSON":
                                concepts["👤 People"].append(ent.text)
                            elif ent.label_ == "ORG":
                                concepts["🏢 Organizations"].append(ent.text)
                            elif ent.label_ in ["DATE", "TIME"]:
                                concepts["📅 Timeline"].append(ent.text)
                            elif ent.label_ in ["GPE", "LOC"]:
                                concepts["📍 Locations"].append(ent.text)
                            else:
                                concepts["💡 Concepts"].append(ent.text)
                    except:
                        pass
                    
                    for key in concepts:
                        concepts[key] = list(set(concepts[key]))[:10]
                    
                    mind_map = {
                        "name": "Main Topic",
                        "children": [
                            {
                                "name": category,
                                "children": [{"name": item, "children": []} for item in items]
                            }
                            for category, items in concepts.items() if items
                        ]
                    }
                    
                    st.session_state.processed_data.update({
                        'summary': bullets[:summary_points],
                        'quiz': quiz,
                        'mindmap': mind_map
                    })
                    
                    st.success("✅ Generation complete!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============ TAB 2: PLANT IDENTIFICATION (NEW!) ============
with tab2:
    st.header("🌿 Plant Identification")
    
    st.subheader("Identify Plants from Your Photos")
    
    # Image upload
    uploaded_image = st.file_uploader(
        "Upload a photo of a plant:",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Upload a clear photo of a plant to identify it"
    )
    
    if uploaded_image is not None:
        # Display image
        st.image(uploaded_image, caption="Uploaded plant photo", use_column_width=True)
        
        # Manual plant selection (since we can't do real image recognition without cloud APIs)
        st.info("""
        📌 **Note:** Real plant identification requires cloud image processing APIs.
        
        For now, please select the plant from the list below to get information about it.
        You can also describe what you see in the photo.
        """)
    
    # Plant selection
    st.subheader("Plant Information Database")
    
    selected_plant = st.selectbox(
        "Select a plant or search:",
        list(PLANT_DATABASE.keys()),
        help="Choose a plant to learn more about it"
    )
    
    if selected_plant:
        plant_info = PLANT_DATABASE[selected_plant]
        
        # Display plant card
        st.markdown(f"""
        <div class="plant-card">
            <h3>🌱 {selected_plant}</h3>
            <p><strong>Scientific Name:</strong> {plant_info['scientific_name']}</p>
            <p><strong>Family:</strong> {plant_info['family']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for plant info
        plant_col1, plant_col2, plant_col3 = st.tabs(["📖 Description", "🌱 Care Guide", "💡 Uses"])
        
        with plant_col1:
            st.write(f"**Description:** {plant_info['description']}")
            st.write(f"**Growth Time:** {plant_info['growth_time']}")
        
        with plant_col2:
            st.write("**Care Instructions:**")
            for care in plant_info['care']:
                st.write(f"• {care}")
        
        with plant_col3:
            st.write("**Common Uses:**")
            for use in plant_info['uses']:
                st.write(f"• {use}")
        
        # Store plant data
        st.session_state.plant_data = {
            'plant_name': selected_plant,
            'info': plant_info
        }
        
        # Generate learning content about the plant
        if st.button("📚 Generate Learning Content About This Plant", use_container_width=True, type="primary"):
            with st.spinner("Creating educational content..."):
                plant_content = f"""
                {selected_plant} is a plant belonging to the {plant_info['family']} family, with the scientific name {plant_info['scientific_name']}.
                
                Description: {plant_info['description']}
                
                The growth cycle typically takes about {plant_info['growth_time']} from planting to maturity or first harvest.
                
                Care requirements include the following: {', '.join(plant_info['care'])}.
                
                Common uses of {selected_plant} include: {', '.join(plant_info['uses'])}.
                
                For optimal growth, ensure proper sunlight, watering, and soil conditions as mentioned in the care guide.
                """
                
                st.session_state.processed_data = {
                    'content': plant_content,
                    'source': f"Plant Information: {selected_plant}",
                    'type': 'plant'
                }
                
                st.success("✅ Plant learning content generated!")
                st.info("Go to Summary tab to see the content processed!")

# ============ TAB 3: SUMMARY ============
with tab3:
    if st.session_state.processed_data and 'summary' in st.session_state.processed_data:
        data = st.session_state.processed_data
        
        st.header("📋 Summary & Insights")
        st.subheader(f"📌 Source: {data['source']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            word_count = len(data['content'].split())
            st.metric("📊 Content Words", f"{word_count:,}")
        with col2:
            st.metric("✅ Summary Points", len(data['summary']))
        with col3:
            st.metric("❓ Quiz Questions", len(data.get('quiz', [])))
        
        st.divider()
        
        st.subheader("🎯 Key Points")
        for i, point in enumerate(data['summary'], 1):
            st.markdown(f"**{i}.** {point}")
        
        summary_text = "\n".join([f"{i}. {p}" for i, p in enumerate(data['summary'], 1)])
        st.download_button(
            label="📥 Download Summary (.txt)",
            data=summary_text,
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("👈 Go to **Input** tab or **Plant ID** tab and process content first")

# ============ TAB 4: QUIZ ============
with tab4:
    if st.session_state.processed_data and 'quiz' in st.session_state.processed_data:
        quiz_data = st.session_state.processed_data['quiz']
        
        if not quiz_data:
            st.warning("⚠️ Could not generate quiz. Please try with more content.")
        else:
            st.header("❓ Interactive Quiz")
            
            score = 0
            total = len(quiz_data)
            
            for idx, question in enumerate(quiz_data, 1):
                st.subheader(f"Question {idx}/{total}")
                st.write(f"**{question['question']}**")
                
                difficulty_emoji = {
                    'easy': '🟢',
                    'medium': '🟡',
                    'hard': '🔴',
                    'mixed': '⚪'
                }
                st.caption(f"{difficulty_emoji.get(question.get('difficulty', 'medium'), '⚪')} {question.get('difficulty', 'medium').title()}")
                
                selected = st.radio(
                    "Select your answer:",
                    options=question['options'],
                    key=f"q_{idx}",
                    horizontal=False
                )
                
                correct_idx = question.get('correct_option', 0)
                is_correct = selected == question['options'][correct_idx]
                
                if is_correct:
                    st.success(f"✅ **Correct!** {question.get('explanation', '')}")
                    score += 1
                else:
                    st.error(f"❌ **Incorrect!** Correct answer: {question['options'][correct_idx]}")
                    st.info(f"💡 {question.get('explanation', '')}")
                
                st.divider()
            
            st.subheader("📊 Quiz Results")
            percentage = (score / total * 100) if total > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your Score", f"{score}/{total}")
            with col2:
                st.metric("Percentage", f"{percentage:.1f}%")
            with col3:
                st.metric("Correct Answers", score)
            
            st.divider()
            if percentage >= 80:
                st.success("🌟 **Excellent!** You've mastered this content!")
            elif percentage >= 60:
                st.info("👍 **Good job!** Review the missed questions.")
            else:
                st.warning("📚 **Keep studying!** Try again after reviewing the content.")
    else:
        st.info("👈 Go to **Input** or **Plant ID** tab and process content first")

# ============ TAB 5: MIND MAP ============
with tab5:
    if st.session_state.processed_data and 'mindmap' in st.session_state.processed_data:
        mindmap = st.session_state.processed_data['mindmap']
        
        st.header("🧠 Concept Mind Map")
        
        def display_mindmap(node, level=0):
            indent = "  " * level
            if level == 0:
                st.markdown(f"### 📌 {node.get('name', 'Root')}")
            else:
                st.markdown(f"{indent}**{node.get('name', 'Concept')}**")
            
            if 'children' in node and node['children']:
                for child in node['children']:
                    display_mindmap(child, level + 1)
        
        display_mindmap(mindmap)
        
        st.divider()
        
        st.download_button(
            label="📥 Download Mind Map (JSON)",
            data=json.dumps(mindmap, indent=2),
            file_name="mindmap.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("👈 Go to **Input** or **Plant ID** tab and process content first")

# ============ SIDEBAR ============
with st.sidebar:
    st.header("ℹ️ About This App")
    
    st.markdown("""
    ### 🌱 AI Educational & Plant Assistant v3.0
    
    **Features:**
    - 📝 AI-powered summarization
    - ❓ Auto-generated quizzes
    - 🧠 Interactive mind maps
    - 🌿 Plant identification & info
    
    **Technology:**
    - Streamlit (UI)
    - Transformers (BART, spaCy)
    - Plant database (8+ plants)
    
    **Cost:** ✅ Completely FREE
    """)
    
    st.divider()
    
    st.subheader("🚀 How to Use")
    st.markdown("""
    **For Educational Content:**
    1. Go to **Input** tab
    2. Paste text
    3. Click "Generate"
    4. View summary, quiz, mind map
    
    **For Plant Information:**
    1. Go to **Plant ID** tab
    2. Upload plant photo (optional)
    3. Select plant from list
    4. Learn about care & uses
    """)
    
    st.divider()
    
    st.subheader("🌿 Available Plants")
    for plant in list(PLANT_DATABASE.keys())[:4]:
        st.write(f"• {plant}")
    st.write(f"• ... and {len(PLANT_DATABASE)-4} more!")
    
    st.divider()
    
    st.subheader("☁️ Cloud Powered")
    st.markdown("""
    ✅ No installation
    ✅ No downloads
    ✅ No API keys
    ✅ 100% FREE
    
    Made with ❤️ for learners
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌱 AI Educational & Plant Recognition Assistant | ☁️ Powered by Streamlit Cloud | 100% FREE & Open Source</p>
    <p style="font-size: 12px;">No data is stored. All processing is temporary.</p>
</div>
""", unsafe_allow_html=True)
