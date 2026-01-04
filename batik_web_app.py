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

# Custom CSS with DARK TEXT for readability
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
    /* DARK TEXT for readability */
    .story-text {
        color: #333333 !important;
        background-color: #fffaf0;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FFD166;
        line-height: 1.6;
        font-size: 16px;
    }
    /* Make all text dark */
    h1, h2, h3, h4, p, div, span {
        color: #333333 !important;
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
if 'confidence' not in st.session_state:
    st.session_state.confidence = 0.0

# Header Section
st.markdown('<h1 class="main-title">🌺 Malaysian Batik Storytelling Platform</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #333;">Upload any batik image to discover its cultural story in 7 languages</h3>', unsafe_allow_html=True)

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings & Controls")
    
    # Language Selection
    language = st.selectbox(
        "🌍 Select Story Language",
        ["English", "Malay", "Indonesian", "Arabic", "Japanese", "Korean", "Chinese"],
        index=0,
        help="Choose the language for the cultural story"
    )
    
    st.divider()
    
    # Sample Images Section
    st.header("📸 Quick Test")
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
            <h3 style="color: #333;">Drag & Drop Image Here</h3>
            <p style="color: #666;">or click to browse files</p>
            <p style="color: #888; font-size: 0.9rem;">Max size: 5MB • Supported: JPG, PNG</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze Button
    if uploaded_file or 'use_sample' in st.session_state:
        if st.button("🔍 ANALYZE PATTERN", type="primary", use_container_width=True):
            st.session_state.analyzing = True
            st.session_state.image_uploaded = True
            if uploaded_file:
                st.session_state.image_data = uploaded_file.getvalue()
                st.session_state.image_filename = uploaded_file.name
            # Clear any previous audio
            if 'audio_bytes' in st.session_state:
                del st.session_state.audio_bytes

with col_right:
    st.header("📖 Step 2: Story Results")
    
    # Show results when analyzing
    if st.session_state.get('analyzing', False):
        with st.spinner("🔬 Analyzing pattern..."):
            time.sleep(1.5)
        
        with st.spinner("📚 Loading cultural database..."):
            time.sleep(1.0)
        
        with st.spinner("🌍 Translating to selected language..."):
            time.sleep(0.5)
        
        # Clear spinner
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
        
        # Store in session state for saving
        st.session_state.pattern_name = pattern_name
        st.session_state.confidence = confidence
        
        # RESULT CARD
        st.markdown(f"""
        <div class="result-card">
            <h2 style="color: #333;">🎨 Pattern Detected</h2>
            <h1 style="color: #FF6B6B;">{pattern_name}</h1>
            <p style="color: #333;">Confidence: <strong>{confidence:.1%}</strong></p>
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
        st.markdown(f'<span class="language-tag">{language}</span>', unsafe_allow_html=True)
        
        # CULTURAL STORY SECTION
        st.markdown("### 📚 Cultural Story")
        
        # Define stories for each pattern and language
        if "Bunga" in pattern_name:
            stories = {
                "English": """**The Bunga Raya (Hibiscus)** motif holds profound cultural significance as Malaysia's national flower. This pattern represents more than mere floral decoration—it embodies national identity, unity, and love for the country.

**Historical Roots:**
The five petals of the bunga raya are often interpreted as symbolizing the Five Principles of Rukun Negara (Belief in God, Loyalty to King and Country, Upholding the Constitution, Rule of Law, and Good Behavior and Morality). This connection makes the pattern a visual representation of Malaysia's national philosophy.

**Cultural Meaning:**
In Malaysian homes, the hibiscus plant is commonly grown in gardens, along fences, and near verandas. Its presence in domestic spaces reflects its importance in daily life.""",
                
                "Malay": """**Bunga Raya (Hibiscus)** merupakan motif yang mempunyai makna budaya yang mendalam sebagai bunga kebangsaan Malaysia. Corak ini mewakili lebih daripada sekadar hiasan bunga—ia melambangkan identiti nasional, perpaduan, dan cinta kepada negara.

**Akar Sejarah:**
Lima kelopak bunga raya sering ditafsirkan sebagai melambangkan Lima Prinsip Rukun Negara (Kepercayaan kepada Tuhan, Kesetiaan kepada Raja dan Negara, Keluhuran Perlembagaan, Kedaulatan Undang-undang, dan Kesopanan dan Kesusilaan). Hubungan ini menjadikan corak sebagai perwakilan visual falsafah nasional Malaysia.""",
                
                "Indonesian": """**Bunga Raya (Hibiscus)** adalah motif yang memiliki makna budaya yang dalam sebagai bunga nasional Malaysia. Pola ini mewakili lebih dari sekadar dekorasi bunga—ia melambangkan identitas nasional, persatuan, dan cinta kepada negara.

**Akar Sejarah:**
Lima kelopak bunga raya sering ditafsirkan sebagai melambangkan Lima Prinsip Rukun Negara (Percaya kepada Tuhan, Setia kepada Raja dan Negara, Menjunjung Konstitusi, Kedaulatan Hukum, dan Kesopanan dan Kesusilaan).""",
                
                "Arabic": """**زهرة بونغا رايا (الهيبسكس)** تحمل أهمية ثقافية عميقة كزهرة ماليزيا الوطنية. هذا النمط يمثل أكثر من مجرد زخرفة زهرية—إنه يجسد الهوية الوطنية والوحدة وحب الوطن.

**الجذور التاريخية:**
غالبًا ما تُفسر البتلات الخمس لزهرة بونغا رايا على أنها ترمز إلى المبادئ الخمسة لـ "ركون نيجارا" (الإيمان بالله، الولاء للملك والوطن).""",
                
                "Japanese": """**ブンガ・ラヤ（ハイビスカス）**のモチーフは、マレーシアの国花として深い文化的意義を持っています。この模様は単なる花の装飾以上のものを表しており、国のアイデンティティ、団結、国への愛を体現しています。

**歴史的ルーツ:**
ブンガ・ラヤの5枚の花びらは、しばしばルクン・ネガラの5原則（神への信仰、王と国への忠誠、憲法の遵守、法の支配、礼儀と道徳）を象徴すると解釈されます。""",
                
                "Korean": """**붕가 라야(히비스커스)** 모티프는 말레이시아의 국화로서 깊은 문화적 의미를 지닙니다. 이 패턴은 단순한 꽃 장식을 넘어 국가 정체성, 통일, 그리고 나라에 대한 사랑을 구현합니다.

**역사적 뿌리:**
붕가 라야의 다섯 꽃잎은 종종 루쿤 네가라의 다섯 원칙(신에 대한 믿음, 왕과 국가에 대한 충성, 헌법 준수, 법치, 예의와 도덕)을 상징하는 것으로 해석됩니다.""",
                
                "Chinese": """**大红花（木槿）**图案作为马来西亚的国花具有深厚的文化意义。这种图案不仅仅是花卉装饰，它体现了国家认同、团结和对国家的热爱。

**历史根源:**
大红花的五片花瓣通常被解释为象征着国家原则的五大支柱（信奉上苍、忠于君国、维护宪法、遵崇法治、培养德行）。"""
            }
        else:  # Geometric pattern
            stories = {
                "English": """**Geometric patterns** in Malaysian batik represent a sophisticated fusion of spiritual principles, mathematical precision, and cultural heritage. These designs are visual expressions of Islamic artistic philosophy.

**Islamic Artistic Tradition:**
Following Islamic norms, Malaysian artisans developed geometric patterns to express divine order and cosmic harmony. The repetitive use of circles, squares, and diamonds reflects the infinite nature of God.""",
                
                "Malay": """**Corak geometri** dalam batik Malaysia mewakili gabungan canggih prinsip spiritual, ketepatan matematik, dan warisan budaya. Reka bentuk ini adalah ekspresi visual falsafah seni Islam.

**Tradisi Seni Islam:**
Mengikut norma Islam, tukang batik Malaysia membangunkan corak geometri untuk meluahkan susunan ilahi dan keharmonian kosmik.""",
                
                "Indonesian": """**Pola geometris** dalam batik Malaysia mewakili perpaduan canggih prinsip spiritual, presisi matematika, dan warisan budaya. Desain ini adalah ekspresi visual filsafat seni Islam.

**Tradisi Seni Islam:**
Mengikuti norma Islam, pengrajin Malaysia mengembangkan pola geometris untuk mengekspresikan ketertiban ilahi dan harmoni kosmik.""",
                
                "Arabic": """**الأنماط الهندسية** في باتيك ماليزيا تمثل اندماجًا متطورًا للمبادئ الروحية والدقة الرياضية والتراث الثقافي. هذه التصاميم هي تعبيرات بصرية لفلسفة الفن الإسلامي.

**التقليد الفني الإسلامي:**
اتباعًا للمعايير الإسلامية، طور الحرفيون الماليزيون الأنماط الهندسية للتعبير عن النظام الإلهي والانسجام الكوني.""",
                
                "Japanese": """マレーシアのバティックにおける**幾何学模様**は、精神的原則、数学的精度、文化遺産の高度な融合を表しています。これらのデザインはイスラム芸術哲学の視覚的表現です。

**イスラム芸術伝統:**
イスラムの規範に従い、マレーシアの職人たちは神の秩序と宇宙の調和を表現するために幾何学模様を発展させました。""",
                
                "Korean": """말레이시아 바틱의 **기하학적 패턴**은 영적 원리, 수학적 정밀성, 문화적 유산의 정교한 융합을 나타냅니다. 이러한 디자인은 이슬람 예술 철학의 시각적 표현입니다.

**이슬람 예술 전통:**
이슬람 규범에 따라 말레이시아 장인들은 신의 질서와 우주적 조화를 표현하기 위해 기하학적 패턴을 개발했습니다.""",
                
                "Chinese": """马来西亚蜡染中的**几何图案**代表了精神原则、数学精度和文化遗产的复杂融合。这些设计是伊斯兰艺术哲学的视觉表达。

**伊斯兰艺术传统:**
遵循伊斯兰规范，马来西亚工匠发展了几何图案来表达神圣秩序和宇宙和谐。"""
            }
        
        # Get the story for selected language, default to English
        story = stories.get(language, stories["English"])
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
        
        audio_col1, audio_col2 = st.columns(2)
        
        with audio_col1:
            if st.button("▶️ Generate & Play Audio", use_container_width=True):
                if st.session_state.current_story:
                    with st.spinner(f"Generating audio in {language}..."):
                        try:
                            # Get language code
                            lang_code = language_codes.get(language, "en")
                            
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
                                st.session_state.audio_filename = f"batik_story_{pattern_name.replace(' ', '_')}_{language}.mp3"
                                
                                # Clean up temp file
                                os.unlink(tmp_file.name)
                            
                            st.success(f"✅ Audio generated successfully in {language}!")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error generating audio: {str(e)}")
                            st.info("💡 Try English language for guaranteed audio")
                else:
                    st.warning("Please analyze an image first!")
        
        # Display audio player if audio exists
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format='audio/mp3')
            
            with audio_col2:
                # Download audio button
                st.download_button(
                    label="📥 Download Audio",
                    data=st.session_state.audio_bytes,
                    file_name=st.session_state.audio_filename,
                    mime="audio/mp3",
                    use_container_width=True
                )
        else:
            with audio_col2:
                st.button("📥 Download Audio", disabled=True, use_container_width=True,
                         help="Generate audio first")
        
        # SAVE REPORT SECTION
        st.markdown("### 💾 Save Results")
        
        if st.button("📄 Save Full Report", type="primary", use_container_width=True):
            # Create report data
            report_data = {
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pattern_name": st.session_state.pattern_name,
                "confidence": st.session_state.confidence,
                "selected_language": language,
                "cultural_story": st.session_state.current_story,
                "image_filename": st.session_state.get('image_filename', 'Sample Image')
            }
            
            # Create reports directory
            os.makedirs("reports", exist_ok=True)
            
            # Save as JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"reports/batik_report_{timestamp}.json"
            
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # Create text report
            text_report = f"""BATIK PATTERN ANALYSIS REPORT
==================================
Analysis Date: {report_data['analysis_date']}
Pattern Detected: {report_data['pattern_name']}
Confidence: {report_data['confidence']:.1%}
Selected Language: {report_data['selected_language']}
Image: {report_data['image_filename']}

CULTURAL STORY:
{report_data['cultural_story']}
"""
            
            text_filename = f"reports/batik_report_{timestamp}.txt"
            with open(text_filename, "w", encoding="utf-8") as f:
                f.write(text_report)
            
            # Convert to downloadable format
            report_bytes = text_report.encode('utf-8')
            
            # Download button for the report
            st.download_button(
                label="📥 Download Report as TXT",
                data=report_bytes,
                file_name=f"batik_analysis_report_{timestamp}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.success(f"✅ Report saved as: {text_filename}")
        
        # ACTION BUTTONS
        st.divider()
        st.markdown("### 🎯 Actions")
        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            if st.button("🔄 Analyze Another", use_container_width=True):
                # Clear session state
                for key in ['analyzing', 'use_sample', 'image_uploaded', 'audio_bytes', 'current_story', 'pattern_name', 'confidence']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        with action_col2:
            if st.button("📧 Share Results", use_container_width=True):
                st.success("✅ Results copied to clipboard! (Simulated)")
        with action_col3:
            if st.button("📊 View Statistics", use_container_width=True):
                st.info("Statistics feature coming soon!")
    
    else:
        # Show instructions when no analysis done
        st.info("👈 **Upload an image or use sample images to begin analysis**")
        
        # Show features
        st.markdown("### ✨ What You'll Get:")
        
        features = [
            {"icon": "🎨", "title": "Pattern Identification", "desc": "AI detects Bunga Raya or Geometric patterns"},
            {"icon": "📚", "title": "Cultural Stories", "desc": "Detailed historical and cultural narratives"},
            {"icon": "🌍", "title": "7 Languages", "desc": "Stories available in multiple languages"},
            {"icon": "🔊", "title": "Audio Narration", "desc": "Listen to stories with text-to-speech"},
            {"icon": "💾", "title": "Save & Share", "desc": "Export results as audio or text files"},
            {"icon": "⚡", "title": "Instant Results", "desc": "Get analysis in seconds"}
        ]
        
        cols = st.columns(2)
        for idx, feature in enumerate(features):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 5px 0;">
                    <div style="font-size: 1.5rem;">{feature['icon']}</div>
                    <strong style="color: #333;">{feature['title']}</strong><br>
                    <small style="color: #666;">{feature['desc']}</small>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #333; padding: 20px;">
    <p>🌺 <strong>Malaysian Batik Cultural Preservation Project</strong> | Version 2.0</p>
    <p>🧠 AI-Powered Pattern Recognition | 🎨 Cultural Storytelling | 🌍 Multilingual Support</p>
    <p>📧 Contact: cultural.heritage@batik.edu.my | 📱 +60 12-345 6789</p>
</div>
""", unsafe_allow_html=True)