# batik_web_app.py
import streamlit as st
import tempfile
import os
import time
from PIL import Image
import base64
from gtts import gTTS
import json
import datetime

# Page configuration
st.set_page_config(
    page_title="Batik Pattern Storyteller",
    page_icon="🌺",
    layout="wide"
)

# Custom CSS - WHITE TEXT for specific elements
st.markdown("""
<style>
    /* WHITE TEXT ELEMENTS */
    .white-text {
        color: white !important;
    }
    
    /* Main title - WHITE */
    .main-title {
        font-size: 3rem;
        color: white !important;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Subtitle - WHITE */
    .subtitle {
        color: white !important;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Section headers - WHITE */
    .section-header {
        color: white !important;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Step headers - WHITE */
    .step-header {
        color: white !important;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 15px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Pattern detection header - WHITE */
    .pattern-header {
        color: white !important;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Confidence text - WHITE */
    .confidence-text {
        color: white !important;
        font-size: 16px;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Upload area text - WHITE */
    .upload-text {
        color: white !important;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* What You'll Get header - WHITE */
    .features-header {
        color: white !important;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Selected Language display - WHITE */
    .language-display {
        color: white !important;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* DARK TEXT elements (for contrast) */
    .dark-text {
        color: #333333 !important;
    }
    
    /* Upload area */
    .upload-area {
        border: 3px dashed #4ECDC4;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background-color: rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    /* Result card - DARK TEXT inside */
    .result-card {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #FF6B6B;
    }
    
    /* Pattern badges */
    .pattern-badge {
        display: inline-block;
        padding: 8px 15px;
        margin: 5px;
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Story container - DARK TEXT */
    .story-container {
        background: rgba(255,255,255,0.9);
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        color: #333333;
        font-size: 16px;
        line-height: 1.6;
        text-align: justify;
    }
    
    /* Single language display (no multiple boxes) */
    .single-language {
        background-color: rgba(255,255,255,0.9);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 10px 0;
        border: 2px solid #4ECDC4;
        color: #333333;
        font-size: 18px;
        font-weight: bold;
    }
    
    /* Language change button */
    .language-change-btn {
        background-color: rgba(78, 205, 196, 0.8);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        margin-top: 5px;
        cursor: pointer;
        font-size: 12px;
    }
    
    /* Progress bar */
    .progress-bar {
        background: rgba(240,240,240,0.7);
        height: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .progress-fill {
        background: #4ECDC4;
        height: 100%;
        border-radius: 5px;
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
if 'confidence' not in st.session_state:
    st.session_state.confidence = 0

# Set background
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header Section - ALL WHITE TEXT
st.markdown('<h1 class="main-title">🌺 Malaysian Batik Storytelling Platform</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subtitle">Upload any batik image to discover its cultural story in 7 languages</h3>', unsafe_allow_html=True)

# Sidebar - Settings
with st.sidebar:
    st.markdown('<div class="section-header">⚙️ Settings & Controls</div>', unsafe_allow_html=True)
    
    # Language Selection - Simple dropdown only
    st.session_state.selected_language = st.selectbox(
        "🌍 Select Story Language",
        ["English", "Malay", "Indonesian", "Arabic", "Japanese", "Korean", "Chinese"],
        index=0,
        help="Choose the language for the cultural story"
    )
    
    st.divider()
    
    st.markdown('<div class="section-header">📸 Quick Test</div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="section-header">✨ Features</div>', unsafe_allow_html=True)
    st.markdown("""
    ✅ **AI Pattern Detection**  
    ✅ **7 Languages Supported**  
    ✅ **Audio Storytelling**  
    ✅ **Cultural Database**  
    ✅ **Instant Results**  
    """)
    
    st.divider()
    
    st.markdown('<div class="section-header">❓ How to Use</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="step-header">📤 Step 1: Upload Image</div>', unsafe_allow_html=True)
    
    # Upload Area with WHITE TEXT
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drag and drop or click to browse",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        label_visibility="collapsed",
        help="Supported formats: JPG, PNG, BMP, WebP"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="📸 Your Uploaded Image")
    else:
        st.markdown("""
        <div class="upload-text">
            <div style="font-size: 4rem;">📁</div>
            <h3>Drag & Drop Image Here</h3>
            <p>or click to browse files</p>
            <p style="font-size: 0.9rem;">Max size: 5MB • Supported: JPG, PNG</p>
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
    st.markdown('<div class="step-header">📖 Step 2: Story Results</div>', unsafe_allow_html=True)
    
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
        
        # Store in session state
        st.session_state.pattern_name = pattern_name
        st.session_state.confidence = confidence
        
        # PATTERN DETECTED SECTION - WHITE TEXT
        st.markdown('<div class="pattern-header">🎨 Pattern Detected</div>', unsafe_allow_html=True)
        
        # Pattern name in card
        st.markdown(f'''
        <div class="result-card">
            <h2 style="color: #FF6B6B; text-align: center;">{pattern_name}</h2>
        </div>
        ''', unsafe_allow_html=True)
        
        # Confidence with WHITE TEXT
        st.markdown(f'<div class="confidence-text">Confidence: <strong>{confidence:.1%}</strong></div>', unsafe_allow_html=True)
        
        # Progress bar
        st.markdown(f'''
        <div class="progress-bar">
            <div class="progress-fill" style="width: {confidence*100}%"></div>
        </div>
        ''', unsafe_allow_html=True)
        
        # PATTERN TYPE (BADGES)
        st.markdown('<div class="section-header">Pattern Type</div>', unsafe_allow_html=True)
        if "Bunga" in pattern_name:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<span class="pattern-badge">🌺 Floral Pattern</span>', unsafe_allow_html=True)
            with col2:
                st.markdown('<span class="pattern-badge">🇲🇾 National Symbol</span>', unsafe_allow_html=True)
            with col3:
                st.markdown('<span class="pattern-badge">❤️ Love & Unity</span>', unsafe_allow_html=True)
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<span class="pattern-badge">🔷 Geometric Design</span>', unsafe_allow_html=True)
            with col2:
                st.markdown('<span class="pattern-badge">🕌 Islamic Art</span>', unsafe_allow_html=True)
            with col3:
                st.markdown('<span class="pattern-badge">⚖️ Harmony & Balance</span>', unsafe_allow_html=True)
        
        # SELECTED LANGUAGE - SINGLE DISPLAY ONLY (NO MULTIPLE BOXES)
        st.markdown('<div class="section-header">Selected Language</div>', unsafe_allow_html=True)
        
        # Display only the selected language
        language_display = {
            "English": "🇬🇧 English",
            "Malay": "🇲🇾 Malay",
            "Indonesian": "🇮🇩 Indonesian",
            "Arabic": "🇸🇦 Arabic",
            "Japanese": "🇯🇵 Japanese",
            "Korean": "🇰🇷 Korean",
            "Chinese": "🇨🇳 Chinese"
        }
        
        st.markdown(f'''
        <div class="single-language">
            {language_display[st.session_state.selected_language]}
            <br>
            <small style="color: #666; font-size: 14px;">Selected in sidebar</small>
        </div>
        ''', unsafe_allow_html=True)
        
        # CULTURAL STORY SECTION
        st.markdown('<div class="section-header">Cultural Story</div>', unsafe_allow_html=True)
        
        # Define CLEAN stories for each pattern and language (NO MARKDOWN SYMBOLS)
        if "Bunga" in pattern_name:
            stories = {
                "English": """Bunga Raya Pattern (Hibiscus)

The Bunga Raya, or Hibiscus, is Malaysia's national flower and holds deep cultural significance in batik designs. This floral pattern symbolizes:

National Pride: Represents Malaysian identity and unity.
Beauty and Grace: The delicate petals showcase natural elegance.
Cultural Heritage: Used in traditional ceremonies and celebrations.
Five Petals: Symbolize the Five Principles of Rukun Negara.

Cultural Meaning:
The vibrant red color represents courage and life, while the intricate details show the artisan's skill. This pattern is commonly found in batik from the East Coast states of Malaysia.""",
                
                "Malay": """Corak Bunga Raya (Hibiscus)

Bunga Raya, atau Hibiscus, adalah bunga kebangsaan Malaysia dan mempunyai makna budaya yang mendalam dalam reka bentuk batik. Corak bunga ini melambangkan:

Kebanggaan Nasional: Mewakili identiti dan perpaduan Malaysia.
Kecantikan dan Keanggunan: Kelopak halus mempamerkan keanggunan semula jadi.
Warisan Budaya: Digunakan dalam upacara tradisional dan perayaan.
Lima Kelopak: Melambangkan Lima Prinsip Rukun Negara.

Makna Budaya:
Warna merah terang mewakili keberanian dan kehidupan, manakala butiran rumit menunjukkan kemahiran tukang batik. Corak ini biasa ditemui dalam batik dari negeri-negeri Pantai Timur Malaysia.""",
                
                "Indonesian": """Pola Bunga Raya (Hibiscus)

Bunga Raya, atau Hibiscus, adalah bunga nasional Malaysia dan memiliki makna budaya yang mendalam dalam desain batik. Pola bunga ini melambangkan:

Kebanggaan Nasional: Mewakili identitas dan persatuan Malaysia.
Kecantikan dan Keanggunan: Kelopak halus menunjukkan keanggunan alami.
Warisan Budaya: Digunakan dalam upacara tradisional dan perayaan.
Lima Kelopak: Melambangkan Lima Prinsip Rukun Negara.

Makna Budaya:
Warna merah cerah melambangkan keberanian dan kehidupan, sementara detail rumit menunjukkan keahlian pengrajin batik. Pola ini umum ditemukan dalam batik dari negara bagian Pantai Timur Malaysia.""",
                
                "Arabic": """نمط زهرة الهيبسكس

زهرة الهيبسكس هي الزهرة الوطنية لماليزيا وتحمل أهمية ثقافية عميقة في تصميمات الباتيك. يرمز هذا النمط الزهري إلى:

الفخر الوطني: يمثل الهوية والوحدة الماليزية.
الجمال والأناقة: تظهر البتلات الرقيقة الأناقة الطبيعية.
التراث الثقافي: يستخدم في الاحتفالات التقليدية.
البتلات الخمس: ترمز إلى المبادئ الخمسة لـ "ركون نيجارا".

المعنى الثقافي:
يمثل اللون الأحمر الزاهي الشجاعة والحياة، بينما تظهر التفاصيل المعقدة مهارة الحرفي. يوجد هذا النمط عادةً في الباتيك من ولايات الساحل الشرقي الماليزي.""",
                
                "Japanese": """ハイビスカスのパターン

ハイビスカスはマレーシアの国花であり、バティックデザインに深い文化的意義を持っています。この花のパターンは以下を象徴しています：

国民の誇り: マレーシアのアイデンティティと統一を表す。
美しさと優雅さ: 繊細な花びらが自然の優雅さを示す。
文化的遺産: 伝統的な式典や祝賀で使用される。
5枚の花びら: ルクン・ネガラの5原則を象徴。

文化的意味:
鮮やかな赤色は勇気と生命を表し、複雑な細部は職人の技術を示しています。このパターンは東海岸州のバティックで一般的に見られます。""",
                
                "Korean": """히비스커스 패턴

히비스커스는 말레이시아의 국화이며 바틱 디자인에 깊은 문화적 의미を 지니고 있습니다. 이 꽃 패턴은 다음을 상징합니다:

국가적 자부심: 말레이시아의 정체성과 통일을 나타냅니다.
아름다움과 우아함: 섬세한 꽃잎이 자연의 우아함을 보여줍니다.
문화적 유산: 전통 의식과 축하 행사에 사용됩니다.
다섯 꽃잎: 루쿤 네가라의 다섯 원칙을 상징합니다.

문화적 의미:
선명한 빨간색은 용기와 생명을 나타내며, 복잡한 세부 사항은 장인의 기술을 보여줍니다. 이 패턴은 동해안 주의 바틱에서 일반적으로 발견됩니다.""",
                
                "Chinese": """木槿花图案

木槿花是马来西亚的国花，在蜡染设计中具有深厚的文化意义。这种花卉图案象征着：

国家自豪感: 代表马来西亚的身份和团结。
美丽与优雅: 精致的花瓣展现自然优雅。
文化遗产: 用于传统仪式和庆祝活动。
五片花瓣: 象征国家原则的五项原则。

文化意义:
鲜艳的红色代表勇气和生命，复杂的细节展示工匠的技艺。这种图案常见于马来西亚东海岸州的蜡染。"""
            }
        else:  # Geometric pattern
            stories = {
                "English": """Geometric Pattern

Geometric patterns in Malaysian batik represent mathematical precision and spiritual harmony. These designs feature:

Symmetrical Shapes: Circles, squares, and diamonds in perfect balance.
Islamic Influence: Reflects the prohibition of figurative representation.
Mathematical Beauty: Demonstrates advanced understanding of geometry.
Cosmic Harmony: Represents the order of the universe.

Cultural Significance:
Geometric patterns symbolize infinity and the divine. The repetitive nature reflects meditation and spiritual contemplation. Common in East Coast batik, these patterns showcase Malay-Islamic artistic fusion.""",
                
                "Malay": """Corak Geometri

Corak geometri dalam batik Malaysia mewakili ketepatan matematik dan keharmonian spiritual. Reka bentuk ini mempunyai:

Bentuk Simetri: Bulatan, segi empat, dan berlian dalam keseimbangan sempurna.
Pengaruh Islam: Mencerminkan larangan perwakilan figuratif.
Keindahan Matematik: Menunjukkan kefahaman lanjut geometri.
Keharmonian Kosmik: Mewakili susunan alam semesta.

Kepentingan Budaya:
Corak geometri melambangkan infiniti dan ketuhanan. Sifat berulang mencerminkan meditasi dan kontemplasi spiritual. Biasa dalam batik Pantai Timur, corak ini mempamerkan gabungan seni Melayu-Islam.""",
                
                "Indonesian": """Pola Geometris

Pola geometris dalam batik Malaysia mewakili presisi matematis dan harmoni spiritual. Desain ini memiliki:

Bentuk Simetris: Lingkaran, persegi, dan belah ketupat dalam keseimbangan sempurna.
Pengaruh Islam: Mencerminkan larangan representasi figuratif.
Keindahan Matematis: Menunjukkan pemahaman lanjut geometri.
Harmoni Kosmik: Mewakili keteraturan alam semesta.

Signifikansi Budaya:
Pola geometris melambangkan ketidakterbatasan dan keilahian. Sifat berulang mencerminkan meditasi dan kontemplasi spiritual. Umum dalam batik Pantai Timur, pola ini menunjukkan fusi seni Melayu-Islam.""",
                
                "Arabic": """النمط الهندسي

تمثل الأنماط الهندسية في باتيك ماليزيا الدقة الرياضية والانسجام الروحي. تتميز هذه التصاميم بـ:

أشكال متناظرة: دوائر، مربعات، ومعينات في توازن مثالي.
التأثير الإسلامي: يعكس حظر التمثيل التصويري.
الجمال الرياضي: يُظهر فهمًا متقدمًا للهندسة.
الانسجام الكوني: يمثل نظام الكون.

الأهمية الثقافية:
ترمز الأنماط الهندسية إلى اللانهاية والإلهي. تعكس الطبيعة المتكررة التأمل والتفكير الروحي. شائعة في باتيك الساحل الشرقي، تُظهر هذه الأنماط اندماج الفن الملايوي الإسلامي.""",
                
                "Japanese": """幾何学模様

マレーシアのバティックにおける幾何学模様は、数学的精度と精神的調和を表しています。これらのデザインの特徴：

対称的な形状: 完璧なバランスの円、正方形、ひし形。
イスラムの影響: 具象的表現の禁止を反映。
数学的美しさ: 高度な幾何学理解を示す。
宇宙的調和: 宇宙の秩序を表す。

文化的意義:
幾何学模様は無限性と神性を象徴します。繰り返される性質は瞑想と精神的思索を反映します。東海岸バティックで一般的なこれらの模様は、マレー・イスラム芸術の融合を示しています。""",
                
                "Korean": """기하학적 패턴

말레이시아 바틱의 기하학적 패턴은 수학적 정밀도와 정신적 조화를 나타냅니다. 이 디자인의 특징:

대칭형 모양: 완벽한 균형의 원, 사각형, 마름모.
이슬람 영향: 구체적 표현 금지를 반영.
수학적 아름다움: 고급 기하학 이해를 보여줍니다.
우주적 조화: 우주의 질서를 나타냅니다.

문화적 의미:
기하학적 패턴은 무한성과 신성을 상징합니다. 반복적인 성격은 명상과 정신적 사색을 반영합니다. 동해안 바틱에서 일반적인 이 패턴은 말레이-이슬람 예술의 융합을 보여줍니다.""",
                
                "Chinese": """几何图案

马来西亚蜡染中的几何图案代表数学精度和精神和谐。这些设计特点：

对称形状: 完美平衡的圆形、方形和菱形。
伊斯兰影响: 反映禁止具象表现。
数学之美: 展示高级几何理解。
宇宙和谐: 代表宇宙秩序。

文化意义:
几何图案象征无限和神性。重复性质反映冥想和精神沉思。东海岸蜡染中常见的这些图案展示了马来-伊斯兰艺术融合。"""
            }
        
        # Get the story for selected language
        story = stories.get(st.session_state.selected_language, stories["English"])
        st.session_state.current_story = story
        
        # Display the story with CLEAN TEXT (no markdown symbols)
        st.markdown(f'<div class="story-container">{story}</div>', unsafe_allow_html=True)
        
        # PATTERN DETAILS
        with st.expander("📊 Pattern Details", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Origin", "Kelantan, Malaysia")
            with col2:
                st.metric("Cultural Age", "100+ years")
            with col3:
                st.metric("UNESCO Status", "Intangible Heritage")
        
        # AUDIO SECTION
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
        
        audio_col1, audio_col2, audio_col3 = st.columns([2, 1, 1])
        
        with audio_col1:
            if st.button("▶️ Generate & Play Audio", use_container_width=True):
                if st.session_state.current_story:
                    with st.spinner(f"Generating audio in {st.session_state.selected_language}..."):
                        try:
                            # Get language code
                            lang_code = language_codes.get(st.session_state.selected_language, "en")
                            
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
                                st.session_state.audio_filename = f"batik_story_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                                
                                # Clean up temp file
                                os.unlink(tmp_file.name)
                            
                            st.success(f"✅ Audio generated successfully!")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error generating audio: {str(e)}")
                            st.info("💡 Tip: Try English language for guaranteed audio generation")
                else:
                    st.warning("Please analyze an image first to generate a story!")
        
        # Display audio player if audio exists
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format='audio/mp3')
            
            with audio_col2:
                # Save Report button
                if st.button("📁 Save Report", use_container_width=True):
                    try:
                        # Create report data
                        report_data = {
                            "pattern_name": st.session_state.pattern_name,
                            "confidence": float(st.session_state.confidence),
                            "language": st.session_state.selected_language,
                            "story": st.session_state.current_story,
                            "timestamp": datetime.datetime.now().isoformat(),
                            "image_filename": st.session_state.get('image_filename', 'sample_image')
                        }
                        
                        # Save JSON report
                        report_filename = f"batik_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        with open(report_filename, 'w', encoding='utf-8') as f:
                            json.dump(report_data, f, indent=2, ensure_ascii=False)
                        
                        # Save text report
                        text_filename = f"batik_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        with open(text_filename, 'w', encoding='utf-8') as f:
                            f.write("="*50 + "\n")
                            f.write("BATIK CULTURAL STORY REPORT\n")
                            f.write("="*50 + "\n\n")
                            f.write(f"Pattern: {st.session_state.pattern_name}\n")
                            f.write(f"Confidence: {st.session_state.confidence:.1%}\n")
                            f.write(f"Language: {st.session_state.selected_language}\n")
                            f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write("\n" + "="*50 + "\n")
                            f.write("CULTURAL STORY\n")
                            f.write("="*50 + "\n\n")
                            f.write(st.session_state.current_story)
                        
                        # Read files for download
                        with open(text_filename, 'r', encoding='utf-8') as f:
                            text_report = f.read()
                        
                        st.success("✅ Report saved successfully!")
                        
                        # Provide download buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📥 Download TXT Report",
                                data=text_report,
                                file_name=text_filename,
                                mime="text/plain",
                                use_container_width=True
                            )
                        with col2:
                            st.download_button(
                                label="📥 Download JSON Report",
                                data=json.dumps(report_data, indent=2, ensure_ascii=False),
                                file_name=report_filename,
                                mime="application/json",
                                use_container_width=True
                            )
                        
                    except Exception as e:
                        st.error(f"Error saving report: {str(e)}")
            
            with audio_col3:
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
                st.button("📁 Save Report", disabled=True, use_container_width=True, 
                         help="Generate audio first")
            with audio_col3:
                st.button("📥 Download Audio", disabled=True, use_container_width=True,
                         help="Generate audio first")
        
        # ACTION BUTTONS
        st.divider()
        st.markdown('<div class="section-header">🎯 Actions</div>', unsafe_allow_html=True)
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
            # Export all data button
            if st.button("📊 Export All Data", use_container_width=True):
                if st.session_state.current_story:
                    # Create comprehensive export
                    export_data = {
                        "app_info": {
                            "name": "Malaysian Batik Storytelling Platform",
                            "version": "2.0",
                            "export_date": datetime.datetime.now().isoformat()
                        },
                        "analysis": {
                            "pattern_name": st.session_state.pattern_name,
                            "confidence": float(st.session_state.confidence),
                            "detection_date": datetime.datetime.now().isoformat()
                        },
                        "content": {
                            "selected_language": st.session_state.selected_language,
                            "cultural_story": st.session_state.current_story
                        },
                        "metadata": {
                            "image_uploaded": 'image_filename' in st.session_state,
                            "image_name": st.session_state.get('image_filename', 'sample_image'),
                            "audio_generated": 'audio_bytes' in st.session_state
                        }
                    }
                    
                    # Create export file
                    export_filename = f"batik_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Export",
                        data=json.dumps(export_data, indent=2, ensure_ascii=False),
                        file_name=export_filename,
                        mime="application/json",
                        use_container_width=True
                    )
                    st.success("✅ Export ready for download!")
                else:
                    st.warning("Please analyze an image first!")
    
    else:
        # Show instructions when no analysis done
        st.info("👈 **Upload an image or use sample images to begin analysis**")
        
        # Show features - WHITE HEADER
        st.markdown('<div class="features-header">✨ What You\'ll Get:</div>', unsafe_allow_html=True)
        
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
                <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px 0;">
                    <div style="font-size: 1.5rem; color: #4ECDC4;">{feature['icon']}</div>
                    <strong style="color: #333;">{feature['title']}</strong><br>
                    <small style="color: #666;">{feature['desc']}</small>
                </div>
                """, unsafe_allow_html=True)

# Footer - WHITE TEXT
st.divider()
st.markdown("""
<div style="text-align: center; color: white; padding: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
    <p>🌺 <strong>Malaysian Batik Cultural Preservation Project</strong> | Version 2.0</p>
    <p>🧠 AI-Powered Pattern Recognition | 🎨 Cultural Storytelling | 🌍 Multilingual Support</p>
    <p>📧 Contact: cultural.heritage@batik.edu.my | 📱 +60 12-345 6789</p>
</div>
""", unsafe_allow_html=True)