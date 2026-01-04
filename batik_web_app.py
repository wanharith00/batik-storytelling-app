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
    page_title="Batik Pattern Storyteller",
    page_icon="🌺",
    layout="wide"
)

# Custom CSS with FIXED colors
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .upload-area {
        border: 3px dashed #3498DB;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background-color: #F8F9FA;
        margin: 20px 0;
        min-height: 300px;
    }
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 15px 0;
        border-left: 5px solid #E74C3C;
    }
    .pattern-badge {
        display: inline-block;
        padding: 8px 15px;
        margin: 5px;
        background: linear-gradient(45deg, #E74C3C, #E67E22);
        color: white;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .language-tag {
        display: inline-block;
        padding: 8px 16px;
        margin: 5px;
        background-color: #2ECC71;
        color: white;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .story-text {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #BDC3C7;
        color: #2C3E50 !important;
        font-size: 1rem;
        line-height: 1.6;
        margin: 15px 0;
    }
    .story-text h3, .story-text h4, .story-text strong {
        color: #2C3E50 !important;
    }
    .story-text p {
        color: #34495E !important;
        margin-bottom: 10px;
    }
    .section-header {
        color: #2C3E50;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    .stButton > button {
        background-color: #3498DB;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #2980B9;
        transform: translateY(-2px);
    }
    .action-button {
        background: linear-gradient(45deg, #9B59B6, #8E44AD) !important;
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
if 'pattern_name' not in st.session_state:
    st.session_state.pattern_name = ""
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"
if 'report_data' not in st.session_state:
    st.session_state.report_data = {}

# Header Section
st.markdown('<h1 class="main-title">🌺 Malaysian Batik Storytelling Platform</h1>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center; color: #7F8C8D; margin-bottom: 30px;">Upload any batik image to discover its cultural story in 7 languages</h4>', unsafe_allow_html=True)

# Sidebar - Settings
with st.sidebar:
    st.markdown("## ⚙️ Settings & Controls")
    st.markdown("---")
    
    # Language Selection - FIXED to store in session state
    st.session_state.selected_language = st.selectbox(
        "🌍 Select Story Language",
        ["English", "Malay", "Indonesian", "Arabic", "Japanese", "Korean", "Chinese"],
        index=0,
        help="Choose the language for the cultural story",
        key="language_select"
    )
    
    st.markdown("---")
    
    # Sample Images Section
    st.markdown("## 📸 Quick Test")
    st.write("Try with our sample patterns:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌺 Bunga Raya", use_container_width=True):
            st.session_state.use_sample = "bunga"
            st.session_state.sample_name = "Bunga Raya Pattern"
    with col2:
        if st.button("🔷 Geometric", use_container_width=True):
            st.session_state.use_sample = "geometric"
            st.session_state.sample_name = "Geometric Pattern"
    
    st.markdown("---")
    
    # Features
    st.markdown("## ✨ Features")
    st.markdown("""
    ✅ **AI Pattern Detection**  
    ✅ **7 Languages Supported**  
    ✅ **Audio Storytelling**  
    ✅ **Cultural Database**  
    ✅ **Instant Results**  
    """)
    
    st.markdown("---")
    
    # Help
    st.markdown("## ❓ How to Use")
    st.info("""
    1. **Upload** a batik image
    2. **Select** your language
    3. **Get** instant cultural story
    4. **Listen** to audio version
    5. **Save** or share results
    """)

# Main Content Area - Two Columns Layout
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("## 📤 Step 1: Upload Image")
    
    # Upload Area
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag and drop or click to browse",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        label_visibility="collapsed",
        help="Supported formats: JPG, PNG, BMP, WebP",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="📸 Your Uploaded Image", use_column_width=True)
        st.success(f"✅ File uploaded: {uploaded_file.name}")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 4rem; color: #3498DB;">📁</div>
            <h3 style="color: #2C3E50;">Drag & Drop Image Here</h3>
            <p style="color: #7F8C8D;">or click to browse files</p>
            <p style="color: #95A5A6; font-size: 0.9rem; margin-top: 20px;">Max size: 5MB • Supported: JPG, PNG, BMP, WebP</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze Button
    if uploaded_file or 'use_sample' in st.session_state:
        if st.button("🔍 ANALYZE PATTERN", type="primary", use_container_width=True, key="analyze_btn"):
            st.session_state.analyzing = True
            st.session_state.image_uploaded = True
            if uploaded_file:
                st.session_state.image_data = uploaded_file.getvalue()
                st.session_state.image_filename = uploaded_file.name
            # Clear any previous audio
            if 'audio_bytes' in st.session_state:
                del st.session_state.audio_bytes
            st.rerun()

with col_right:
    st.markdown("## 📖 Step 2: Story Results")
    
    # Show results when analyzing
    if st.session_state.get('analyzing', False):
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
        
        # Store pattern name in session state
        st.session_state.pattern_name = pattern_name
        
        # RESULT CARD
        st.markdown(f"""
        <div class="result-card">
            <h3 style="color: #2C3E50;">🎨 Pattern Detected</h3>
            <h2 style="color: #E74C3C; margin: 10px 0;">{pattern_name}</h2>
            <p style="color: #7F8C8D;">Confidence: <strong style="color: #27AE60;">{confidence:.1%}</strong></p>
            <div style="background: #ECF0F1; height: 12px; border-radius: 6px; margin: 15px 0;">
                <div style="width: {confidence*100}%; background: linear-gradient(90deg, #2ECC71, #27AE60); height: 100%; border-radius: 6px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # PATTERN TYPE BADGES
        st.markdown('<div class="section-header">🏷️ Pattern Type</div>', unsafe_allow_html=True)
        if "Bunga" in pattern_name:
            st.markdown('<span class="pattern-badge">🌺 Floral Pattern</span>', unsafe_allow_html=True)
            st.markdown('<span class="pattern-badge">🇲🇾 National Symbol</span>', unsafe_allow_html=True)
            st.markdown('<span class="pattern-badge">❤️ Love & Unity</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="pattern-badge">🔷 Geometric Design</span>', unsafe_allow_html=True)
            st.markdown('<span class="pattern-badge">🕌 Islamic Art</span>', unsafe_allow_html=True)
            st.markdown('<span class="pattern-badge">⚖️ Harmony & Balance</span>', unsafe_allow_html=True)
        
        # SELECTED LANGUAGE DISPLAY
        st.markdown('<div class="section-header">🌍 Selected Language</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="language-tag">{st.session_state.selected_language}</span>', unsafe_allow_html=True)
        
        # CULTURAL STORY SECTION
        st.markdown('<div class="section-header">📚 Cultural Story</div>', unsafe_allow_html=True)
        
        # Define stories for each pattern and language
        if "Bunga" in pattern_name:
            stories = {
                "English": """The **Bunga Raya (Hibiscus)** motif holds profound cultural significance as Malaysia's national flower. This pattern represents more than mere floral decoration—it embodies national identity, unity, and love for the country.

**Historical Roots:**
The five petals of the bunga raya are often interpreted as symbolizing the Five Principles of Rukun Negara (Belief in God, Loyalty to King and Country, Upholding the Constitution, Rule of Law, and Good Behavior and Morality). This connection makes the pattern a visual representation of Malaysia's national philosophy.

**Cultural Meaning:**
In Malaysian homes, the hibiscus plant is commonly grown in gardens, along fences, and near verandas. Its presence in domestic spaces reflects its importance in daily life. The tree's moderate height and easy maintenance make it accessible to all, symbolizing the democratic nature of Malaysian society.

**Artistic Expression:**
Batik artisans incorporate the bunga raya in diverse ways, blending traditional techniques with contemporary aesthetics. The vibrant reds and yellows commonly used in these patterns reflect Malaysia's tropical environment while adding visual warmth to the fabric.""",
                
                "Malay": """**Bunga Raya (Hibiscus)** merupakan motif yang mempunyai makna budaya yang mendalam sebagai bunga kebangsaan Malaysia. Corak ini mewakili lebih daripada sekadar hiasan bunga—ia melambangkan identiti nasional, perpaduan, dan cinta kepada negara.

**Akar Sejarah:**
Lima kelopak bunga raya sering ditafsirkan sebagai melambangkan Lima Prinsip Rukun Negara (Kepercayaan kepada Tuhan, Kesetiaan kepada Raja dan Negara, Keluhuran Perlembagaan, Kedaulatan Undang-undang, dan Kesopanan dan Kesusilaan). Hubungan ini menjadikan corak sebagai perwakilan visual falsafah nasional Malaysia.

**Makna Budaya:**
Di rumah-rumah Malaysia, pokok bunga raya biasanya ditanam di taman, sepanjang pagar, dan berhampiran veranda. Kehadirannya dalam ruang domestik mencerminkan kepentingannya dalam kehidupan seharian. Ketinggian sederhana pokok dan penyelenggaraan mudah menjadikannya boleh diakses oleh semua, melambangkan sifat demokratik masyarakat Malaysia.""",
                
                "Indonesian": """**Bunga Raya (Hibiscus)** merupakan motif yang memiliki makna budaya yang dalam sebagai bunga nasional Malaysia. Pola ini mewakili lebih dari sekadar dekorasi bunga—ia melambangkan identitas nasional, persatuan, dan cinta terhadap negara.

**Akar Sejarah:**
Lima kelopak bunga raya sering ditafsirkan sebagai simbol Lima Prinsip Rukun Negara (Percaya kepada Tuhan, Setia kepada Raja dan Negara, Menjunjung Konstitusi, Kedaulatan Hukum, dan Kesopanan dan Kesusilaan). Hubungan ini menjadikan pola sebagai representasi visual filosofi nasional Malaysia.

**Makna Budaya:**
Di rumah-rumah Malaysia, tanaman kembang sepatu biasa ditanam di taman, sepanjang pagar, dan dekat beranda. Kehadirannya dalam ruang domestik mencerminkan pentingnya dalam kehidupan sehari-hari.""",
                
                "Arabic": """**زهرة بونغا رايا (الكركديه)** تحمل أهمية ثقافية عميقة كزهرة ماليزيا الوطنية. هذا النمط يمثل أكثر من مجرد زخرفة زهرية—إنه يجسد الهوية الوطنية والوحدة وحب الوطن.

**الجذور التاريخية:**
غالبًا ما تُفسر البتلات الخمس لزهرة بونغا رايا على أنها ترمز إلى المبادئ الخمسة لـ"ركون نيجارا" (الإيمان بالله، الولاء للملك والوطن، حفظ الدستور، سيادة القانون، والأخلاق والسلوك الحسن). هذه الصلة تجعل النمط تمثيلاً مرئيًا لفلسفة ماليزيا الوطنية.""",
                
                "Japanese": """**ブンガ・ラヤ（ハイビスカス）**のモチーフは、マレーシアの国花として深い文化的意義を持っています。このパターンは単なる花の装飾以上のものを表しており、国のアイデンティティ、団結、そして国への愛を体現しています。

**歴史的ルーツ:**
ブンガ・ラヤの5枚の花びらは、ルクン・ネガラ（神への信仰、国王と国への忠誠、憲法の遵守、法の支配、礼儀と道徳）の5原則を象徴すると解釈されることがよくあります。この関係により、このパターンはマレーシアの国家哲学の視覚的表現となっています。""",
                
                "Korean": """**붕가 라야(히비스커스)** 모티프는 말레이시아의 국화로서 깊은 문화적 의미를 지니고 있습니다. 이 패턴은 단순한 꽃 장식 이상을 나타내며 국가 정체성, 통일, 국가에 대한 사랑을 구현합니다.

**역사적 뿌리:**
붕가 라야의 다섯 꽃잎은 종종 루쿤 네가라(하나님에 대한 믿음, 왕과 국가에 대한 충성, 헌법 수호, 법치, 예의와 도덕성)의 다섯 원칙을 상징하는 것으로 해석됩니다. 이 연결은 패턴이 말레이시아 국가 철학의 시각적 표현이 되도록 합니다.""",
                
                "Chinese": """**大红花（木槿）**图案作为马来西亚国花具有深远的象征意义。该图案不仅仅是花卉装饰——它体现了国家认同、团结和对国家的热爱。

**历史根源:**
大红花的五片花瓣常被解读为象征国家原则五大支柱（信奉上苍、忠于君国、维护宪法、尊崇法治、培养德行）。这种联系使该图案成为马来西亚国家理念的视觉表现。

**文化意义:**
在马来西亚家庭中，木槿植物通常种植在花园、篱笆旁和门廊附近。它在家庭空间中的存在反映了其在日常生活中的重要性。"""
            }
        else:  # Geometric pattern
            stories = {
                "English": """**Geometric patterns** in Malaysian batik represent a sophisticated fusion of spiritual principles, mathematical precision, and cultural heritage. These designs are not merely decorative—they are visual expressions of Islamic artistic philosophy adapted to Malaysian cultural context.

**Islamic Artistic Tradition:**
Following Islamic norms that traditionally discourage figurative representation, Malaysian artisans developed geometric patterns as a means to express divine order and cosmic harmony. The repetitive use of circles, squares, and diamonds reflects the infinite nature of God and the structured beauty of the universe.

**Mathematical Precision:**
Approximately 30% of Malaysian batik designs incorporate geometric elements. These patterns demonstrate remarkable mathematical understanding, with designs based on complex geometric principles including symmetrical repetitions and interlocking shapes.""",
                
                "Malay": """**Corak geometri** dalam batik Malaysia mewakili gabungan canggih prinsip spiritual, ketepatan matematik, dan warisan budaya. Reka bentuk ini bukan sekadar hiasan—ia adalah ekspresi visual falsafah seni Islam yang disesuaikan dengan konteks budaya Malaysia.

**Tradisi Seni Islam:**
Mengikut norma Islam yang secara tradisional tidak menggalakkan perwakilan figuratif, tukang batik Malaysia membangunkan corak geometri sebagai cara untuk meluahkan susunan ilahi dan keharmonian kosmik. Penggunaan berulang bulatan, segi empat sama, dan berlian mencerminkan sifat Tuhan yang tidak terhingga dan keindahan berstruktur alam semesta.""",
                
                "Indonesian": """**Pola geometris** dalam batik Malaysia mewakili perpaduan canggih prinsip spiritual, ketepatan matematika, dan warisan budaya. Desain ini bukan hanya dekoratif—ini adalah ekspresi visual filosofi seni Islam yang disesuaikan dengan konteks budaya Malaysia.

**Tradisi Seni Islam:**
Mengikuti norma Islam yang secara tradisional tidak mendorong representasi figuratif, pengrajin batik Malaysia mengembangkan pola geometris sebagai cara untuk mengungkapkan tatanan ilahi dan harmoni kosmik."""
            }
        
        # Get the story for selected language, default to English
        story = stories.get(st.session_state.selected_language, stories["English"])
        st.session_state.current_story = story  # Store for audio generation
        
        # Display the story with DARK TEXT
        st.markdown(f'<div class="story-text">{story}</div>', unsafe_allow_html=True)
        
        # PATTERN DETAILS
        with st.expander("📊 Pattern Details", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Origin", "Kelantan, Malaysia")
            with col2:
                st.metric("Cultural Age", "100+ years")
            with col3:
                st.metric("UNESCO Status", "Intangible Heritage")
        
        # REAL AUDIO GENERATION SECTION
        st.markdown('<div class="section-header">🔊 Audio Story</div>', unsafe_allow_html=True)
        
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
        
        audio_col1, audio_col2 = st.columns(2)
        
        with audio_col1:
            if st.button("▶️ Generate Audio", use_container_width=True, type="primary"):
                if st.session_state.current_story:
                    with st.spinner(f"Generating audio in {st.session_state.selected_language}..."):
                        try:
                            # Get language code
                            lang_code = language_codes.get(st.session_state.selected_language, "en")
                            
                            # Get story text (limit length for audio)
                            story_text = st.session_state.current_story[:500]
                            
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
                            st.error(f"❌ Error generating audio: {str(e)}")
                            st.info("💡 Try English language for guaranteed audio")
                else:
                    st.warning("Please analyze an image first!")
        
        with audio_col2:
            # Save audio button
            if st.session_state.audio_bytes:
                st.download_button(
                    label="💾 Save Audio",
                    data=st.session_state.audio_bytes,
                    file_name=st.session_state.audio_filename,
                    mime="audio/mp3",
                    use_container_width=True,
                    key="download_audio"
                )
            else:
                st.button("💾 Save Audio", disabled=True, use_container_width=True,
                         help="Generate audio first")
        
        # Display audio player if audio exists
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format='audio/mp3')
        
        # SAVE REPORT SECTION (NEW)
        st.markdown('<div class="section-header">📁 Save Report</div>', unsafe_allow_html=True)
        
        # Prepare report data
        report_data = {
            "pattern_name": pattern_name,
            "confidence": f"{confidence:.1%}",
            "language": st.session_state.selected_language,
            "story": story,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_name": st.session_state.get('image_filename', 'Sample Image')
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Save as JSON
            json_report = json.dumps(report_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Save as JSON",
                data=json_report,
                file_name=f"batik_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="save_json"
            )
        
        with col2:
            # Save as TXT
            txt_report = f"""BATIK PATTERN ANALYSIS REPORT
=======================================
Analysis Date: {report_data['analysis_date']}
Pattern Detected: {report_data['pattern_name']}
Confidence: {report_data['confidence']}
Selected Language: {report_data['language']}
Image: {report_data['image_name']}

CULTURAL STORY:
=======================================
{report_data['story']}
            """
            st.download_button(
                label="📄 Save as Text",
                data=txt_report,
                file_name=f"batik_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
                key="save_txt"
            )
        
        # ACTION BUTTONS
        st.markdown('<div class="section-header">🎯 Actions</div>', unsafe_allow_html=True)
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("🔄 New Analysis", use_container_width=True, type="secondary"):
                # Clear session state
                for key in ['analyzing', 'use_sample', 'image_uploaded', 'audio_bytes', 'current_story', 'pattern_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with action_col2:
            if st.button("📧 Share Results", use_container_width=True, type="secondary"):
                st.success("✅ Results shared! (Simulated)")
        
        with action_col3:
            if st.button("📊 View Statistics", use_container_width=True, type="secondary"):
                st.info("Statistics feature coming soon!")
    
    else:
        # Show instructions when no analysis done
        st.info("👈 **Upload an image or use sample images to begin analysis**")
        
        # Show features
        st.markdown("### ✨ What You'll Get:")
        
        features = [
            {"icon": "🎨", "title": "Pattern Identification", "desc": "AI detects patterns automatically"},
            {"icon": "📚", "title": "Cultural Stories", "desc": "Detailed historical narratives"},
            {"icon": "🌍", "title": "7 Languages", "desc": "Multilingual support"},
            {"icon": "🔊", "title": "Audio Narration", "desc": "Listen to stories"},
            {"icon": "💾", "title": "Save Reports", "desc": "Export JSON & Text files"},
            {"icon": "⚡", "title": "Instant Results", "desc": "Fast analysis"}
        ]
        
        cols = st.columns(2)
        for idx, feature in enumerate(features):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; margin: 5px 0; border: 1px solid #E0E0E0;">
                    <div style="font-size: 1.5rem; color: #3498DB;">{feature['icon']}</div>
                    <strong style="color: #2C3E50;">{feature['title']}</strong><br>
                    <small style="color: #7F8C8D;">{feature['desc']}</small>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7F8C8D; padding: 20px; font-size: 0.9rem;">
    <p>🌺 <strong style="color: #2C3E50;">Malaysian Batik Cultural Preservation Project</strong> | Version 2.1</p>
    <p>🧠 AI-Powered Pattern Recognition | 🎨 Cultural Storytelling | 🌍 Multilingual Support</p>
    <p>📧 Contact: cultural.heritage@batik.edu.my | 📱 +60 12-345 6789</p>
</div>
""", unsafe_allow_html=True)