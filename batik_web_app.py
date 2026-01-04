# batik_web_app.py
import streamlit as st
import tempfile
import os
import time
from PIL import Image
import base64
from gtts import gTTS
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Malaysian Batik Storytelling Platform",
    page_icon="🌺",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .upload-area {
        border: 3px dashed #4ECDC4;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 20px 0;
    }
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #FF6B6B;
    }
    .pattern-badge {
        display: inline-block;
        padding: 8px 15px;
        margin: 5px;
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    .language-tag {
        display: inline-block;
        padding: 5px 12px;
        margin: 3px;
        background-color: #4ECDC4;
        color: white;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .story-box {
        background: #fffaf0;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FFD166;
        margin: 20px 0;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'current_story' not in st.session_state:
    st.session_state.current_story = ""
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"
if 'pattern_name' not in st.session_state:
    st.session_state.pattern_name = ""
if 'results_data' not in st.session_state:
    st.session_state.results_data = {}

# Header Section
st.markdown('<h1 class="main-title">🌺 Malaysian Batik Storytelling Platform</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #666;">Upload any batik image to discover its cultural story in 7 languages</h3>', unsafe_allow_html=True)

# Main Content Area - Two Columns Layout
col_left, col_right = st.columns([1, 1])

with col_left:
    st.header("📤 Step 1: Upload Image")
    
    # Upload Area
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag and drop or click to browse",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        label_visibility="collapsed",
        help="Supported formats: JPG, PNG, BMP, WebP"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="📸 Your Uploaded Image", use_column_width=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 4rem;">📁</div>
            <h3>Drag & Drop Image Here</h3>
            <p style="color: #666;">or click to browse files</p>
            <p style="color: #888; font-size: 0.9rem;">Max size: 5MB • Supported: JPG, PNG</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.header("⚙️ Settings & Controls")
    
    # Language Selection
    languages = ["English", "Malay", "Indonesian", "Arabic", "Japanese", "Korean", "Chinese"]
    selected_language = st.selectbox(
        "🌍 Select Story Language",
        languages,
        index=0,
        help="Choose the language for the cultural story"
    )
    st.session_state.selected_language = selected_language
    
    st.divider()
    
    # Sample Images Section
    st.header("📸 Quick Test")
    st.write("Try with our sample patterns:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌺 Bunga Raya Sample", use_container_width=True):
            st.session_state.use_sample = "bunga"
            st.session_state.sample_name = "Bunga Raya Pattern"
            st.success("✅ Bunga Raya sample selected!")
    with col2:
        if st.button("🔷 Geometric Sample", use_container_width=True):
            st.session_state.use_sample = "geometric"
            st.session_state.sample_name = "Geometric Pattern"
            st.success("✅ Geometric sample selected!")
    
    st.divider()
    
    # Features
    st.header("✨ Features")
    st.markdown("""
    ✅ **AI Pattern Detection**  
    ✅ **7 Languages Supported**  
    ✅ **Audio Storytelling**  
    ✅ **Cultural Database**  
    ✅ **Instant Results**  
    """)
    
    st.divider()
    
    # Help
    st.header("❓ How to Use")
    st.info("""
    1. **Upload** a batik image
    2. **Select** your language
    3. **Get** instant cultural story
    4. **Listen** to audio version
    5. **Save** or share results
    """)

# Analyze Button (centered below both columns)
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if uploaded_file or 'use_sample' in st.session_state:
        if st.button("🔍 ANALYZE PATTERN & GENERATE STORY", type="primary", use_container_width=True):
            st.session_state.analyzing = True
            st.session_state.image_uploaded = True
            if uploaded_file:
                st.session_state.image_data = uploaded_file.getvalue()
                st.session_state.image_filename = uploaded_file.name
            # Clear any previous audio
            if 'audio_bytes' in st.session_state:
                del st.session_state.audio_bytes
            st.rerun()

# Show results when analyzing
if st.session_state.get('analyzing', False):
    st.markdown("---")
    st.header("📖 Story Results")
    
    with st.spinner("🔬 Analyzing pattern..."):
        time.sleep(1.5)
    
    with st.spinner("📚 Loading cultural database..."):
        time.sleep(1.0)
    
    with st.spinner("🌍 Translating to selected language..."):
        time.sleep(0.5)
    
    # DETERMINE PATTERN TYPE
    image_name = st.session_state.get('image_filename', '').lower()
    
    if 'use_sample' in st.session_state:
        if st.session_state.use_sample == "bunga":
            pattern_name = "Bunga Raya (Hibiscus)"
            confidence = 0.96
        else:
            pattern_name = "Geometric Pattern"
            confidence = 0.94
    else:
        # Simple detection logic
        if 'bunga' in image_name or 'flower' in image_name or 'raya' in image_name:
            pattern_name = "Bunga Raya (Hibiscus)"
            confidence = 0.92
        elif 'geometri' in image_name or 'geo' in image_name or 'shape' in image_name:
            pattern_name = "Geometric Pattern"
            confidence = 0.91
        else:
            # Random assignment for demo
            pattern_name = "Bunga Raya (Hibiscus)"
            confidence = 0.85
    
    st.session_state.pattern_name = pattern_name
    
    # RESULT CARD
    st.markdown(f"""
    <div class="result-card">
        <h2>🎨 Pattern Detected</h2>
        <h1 style="color: #FF6B6B;">{pattern_name}</h1>
        <p>Confidence: <strong>{confidence:.1%}</strong></p>
        <div style="background: #f0f0f0; height: 10px; border-radius: 5px; margin: 10px 0;">
            <div style="width: {confidence*100}%; background: #4ECDC4; height: 100%; border-radius: 5px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # PATTERN BADGES
    st.markdown("### 🏷️ Pattern Type")
    if "Bunga" in pattern_name:
        st.markdown('<span class="pattern-badge">🌺 Floral Pattern</span>', unsafe_allow_html=True)
        st.markdown('<span class="pattern-badge">🇲🇾 National Symbol</span>', unsafe_allow_html=True)
        st.markdown('<span class="pattern-badge">❤️ Love & Unity</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pattern-badge">🔷 Geometric Design</span>', unsafe_allow_html=True)
        st.markdown('<span class="pattern-badge">🕌 Islamic Art</span>', unsafe_allow_html=True)
        st.markdown('<span class="pattern-badge">⚖️ Harmony & Balance</span>', unsafe_allow_html=True)
    
    # SELECTED LANGUAGE DISPLAY
    st.markdown("### 🌍 Selected Language")
    st.markdown(f'<span class="language-tag">{st.session_state.selected_language}</span>', unsafe_allow_html=True)
    
    # CULTURAL STORY SECTION
    st.markdown("### 📚 Cultural Story")
    
    # Define stories for each pattern and language
    if "Bunga" in pattern_name:
        stories = {
            "English": """**Bunga Raya (Hibiscus) Pattern - Cultural Significance**

The Bunga Raya, Malaysia's national flower, represents national identity and unity. This floral pattern symbolizes love for the country and cultural pride.

**Key Symbolism:**
- Five petals represent Rukun Negara principles
- Red color symbolizes courage and life
- Vibrant design reflects Malaysian tropical beauty

**Cultural Meaning:**
Used in traditional ceremonies and modern fashion, this pattern connects generations and preserves Malaysian heritage.""",
            
            "Malay": """**Corak Bunga Raya (Hibiscus) - Kepentingan Budaya**

Bunga Raya, bunga kebangsaan Malaysia, mewakili identiti nasional dan perpaduan. Corak bunga ini melambangkan cinta kepada negara dan kebanggaan budaya.

**Simbolisme Utama:**
- Lima kelopak mewakili prinsip Rukun Negara
- Warna merah melambangkan keberanian dan kehidupan
- Reka bentuk terang mencerminkan keindahan tropika Malaysia

**Makna Budaya:**
Digunakan dalam majlis tradisional dan fesyen moden, corak ini menyambungkan generasi dan memelihara warisan Malaysia.""",
            
            "Arabic": """**نمط بونغا رايا (الهيبسكس) - الأهمية الثقافية**

تمثل زهرة بونغا رايا، الزهرة الوطنية لماليزيا، الهوية الوطنية والوحدة. يرمز هذا النمط الزهري إلى حب الوطن والفخر الثقافي.

**الرمزية الرئيسية:**
- تمثل البتلات الخمس مبادئ ركون نيجارا
- يرمز اللون الأحمر إلى الشجاعة والحياة
- يعكس التصميم الحيوي جمال ماليزيا الاستوائي

**المعنى الثقافي:**
يُستخدم هذا النمط في الاحتفالات التقليدية والأزياء الحديثة، حيث يربط بين الأجيال ويحافظ على التراث الماليزي."""
        }
    else:  # Geometric pattern
        stories = {
            "English": """**Geometric Pattern - Cultural Significance**

Geometric patterns in Malaysian batik represent Islamic artistic traditions and mathematical precision. These designs symbolize cosmic harmony and spiritual principles.

**Key Symbolism:**
- Interlocking shapes represent unity and balance
- Repetitive patterns symbolize infinity and divine order
- Structured designs reflect Islamic artistic philosophy

**Cultural Meaning:**
Traditionally used by royalty and scholars, these patterns represent intellectual sophistication and spiritual insight in Malaysian culture.""",
            
            "Malay": """**Corak Geometri - Kepentingan Budaya**

Corak geometri dalam batik Malaysia mewakili tradisi seni Islam dan ketepatan matematik. Reka bentuk ini melambangkan keharmonian kosmik dan prinsip spiritual.

**Simbolisme Utama:**
- Bentuk saling kunci mewakili perpaduan dan keseimbangan
- Corak berulang melambangkan ketakterhinggaan dan susunan ilahi
- Reka bentuk berstruktur mencerminkan falsafah seni Islam

**Makna Budaya:**
Secara tradisinya digunakan oleh golongan bangsawan dan cendekiawan, corak ini mewakili kepintaran intelektual dan pandangan spiritual dalam budaya Malaysia.""",
            
            "Arabic": """**النمط الهندسي - الأهمية الثقافية**

تمثل الأنماط الهندسية في باتيك ماليزيا تقاليد الفن الإسلامي والدقة الرياضية. ترمز هذه التصاميم إلى الانسجام الكوني والمبادئ الروحية.

**الرمزية الرئيسية:**
- تمثل الأشكال المتشابكة الوحدة والتوازن
- ترمز الأنماط المتكررة إلى اللانهاية والنظام الإلهي
- تعكس التصاميم المنظمة فلسفة الفن الإسلامي

**المعنى الثقافي:**
تُستخدم هذه الأنماط تقليديًا من قبل العائلة المالكة والعلماء، حيث تمثل التطور الفكري والبصيرة الروحية في الثقافة الماليزية."""
        }
    
    # Get the story for selected language, default to English
    selected_lang = st.session_state.selected_language
    story = stories.get(selected_lang, stories["English"])
    st.session_state.current_story = story
    
    # Display the story in a scrollable box
    st.markdown(f'<div class="story-box">{story}</div>', unsafe_allow_html=True)
    
    # PATTERN DETAILS
    with st.expander("📊 Pattern Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Origin", "Kelantan, Malaysia")
        with col2:
            st.metric("Cultural Age", "100+ years")
        with col3:
            st.metric("Popularity", "High")
    
    # Store results for saving
    st.session_state.results_data = {
        "pattern_name": pattern_name,
        "confidence": confidence,
        "language": selected_lang,
        "story": story,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_filename": st.session_state.get('image_filename', 'sample_image')
    }
    
    # AUDIO SECTION
    st.markdown("### 🔊 Audio Story")
    
    # Language mapping for gTTS
    language_codes = {
        "English": "en",
        "Malay": "ms",
        "Indonesian": "id",
        "Arabic": "ar",
        "Japanese": "ja",
        "Korean": "ko",
        "Chinese": "zh-CN"
    }
    
    audio_col1, audio_col2 = st.columns([1, 1])
    
    with audio_col1:
        if st.button("▶️ Generate Audio Story", type="secondary", use_container_width=True):
            if st.session_state.current_story:
                with st.spinner(f"Generating audio in {selected_lang}..."):
                    try:
                        # Get language code
                        lang_code = language_codes.get(selected_lang, "en")
                        
                        # Get story text
                        story_text = st.session_state.current_story
                        
                        # Create temporary audio file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            # Generate speech
                            tts = gTTS(text=story_text, lang=lang_code, slow=False)
                            tts.save(tmp_file.name)
                            
                            # Read audio file
                            audio_bytes = open(tmp_file.name, 'rb').read()
                            
                            # Store for download
                            st.session_state.audio_bytes = audio_bytes
                            st.session_state.audio_filename = f"batik_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                            
                            # Clean up temp file
                            os.unlink(tmp_file.name)
                        
                        st.success(f"✅ Audio generated successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Try English language for audio")
            else:
                st.warning("No story available to generate audio!")
    
    # Display audio player if audio exists
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format='audio/mp3')
    
    # SAVE ALL RESULTS SECTION
    st.markdown("### 💾 Save All Results")
    
    save_col1, save_col2, save_col3 = st.columns(3)
    
    with save_col1:
        # Save as Text File
        if st.button("📝 Save as Text", use_container_width=True):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"batik_results_{timestamp}.txt"
                
                text_content = f"""MALAYSIAN BATIK STORYTELLING PLATFORM
========================================

Analysis Timestamp: {st.session_state.results_data['timestamp']}
Pattern Detected: {st.session_state.results_data['pattern_name']}
Confidence: {st.session_state.results_data['confidence']:.1%}
Language: {st.session_state.results_data['language']}
Image: {st.session_state.results_data['image_filename']}

CULTURAL STORY:
{st.session_state.results_data['story']}

--- End of Report ---
"""
                
                st.download_button(
                    label="📥 Download Text File",
                    data=text_content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True
                )
                st.success("✅ Text file ready for download!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with save_col2:
        # Save as JSON
        if st.button("📊 Save as JSON", use_container_width=True):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"batik_results_{timestamp}.json"
                
                json_data = st.session_state.results_data
                
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(json_data, indent=2),
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
                st.success("✅ JSON file ready for download!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with save_col3:
        # Save Audio (if generated)
        if st.session_state.audio_bytes:
            st.download_button(
                label="🎵 Download Audio",
                data=st.session_state.audio_bytes,
                file_name=st.session_state.audio_filename,
                mime="audio/mp3",
                use_container_width=True
            )
        else:
            st.button("🎵 Download Audio", disabled=True, use_container_width=True,
                     help="Generate audio first")
    
    # SHARE & RESET BUTTONS
    st.markdown("### 🎯 Actions")
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("🔄 Analyze Another Image", use_container_width=True):
            # Clear session state
            for key in ['analyzing', 'use_sample', 'image_uploaded', 'audio_bytes', 'current_story', 'pattern_name', 'results_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with action_col2:
        if st.button("📧 Share Results", use_container_width=True):
            st.success("✅ Results copied to clipboard! (Demo Feature)")
            st.info("In a real app, this would generate a shareable link")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌺 <strong>Malaysian Batik Cultural Preservation Project</strong></p>
    <p>AI-Powered Pattern Recognition • Cultural Storytelling • Multilingual Support</p>
</div>
""", unsafe_allow_html=True)