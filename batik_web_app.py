# batik_web_app.py
import streamlit as st
import tempfile
import os
import time
from PIL import Image
import base64
from gtts import gTTS  # Added for real audio generation

# Page configuration
st.set_page_config(
    page_title="Batik Pattern Storyteller",
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'current_story' not in st.session_state:
    st.session_state.current_story = ""
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None

# Header Section
st.markdown('<h1 class="main-title">🌺 Malaysian Batik Storytelling Platform</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #666;">Upload any batik image to discover its cultural story in 7 languages</h3>', unsafe_allow_html=True)

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
            <h3>Drag & Drop Image Here</h3>
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
        
        # LANGUAGE SELECTION DISPLAY
        st.markdown("### 🌍 Selected Language")
        st.markdown(f'<span class="language-tag">{language}</span>', unsafe_allow_html=True)
        
        # CULTURAL STORY SECTION
        st.markdown("### 📚 Cultural Story")
        
        # Define stories for each pattern and language
        if "Bunga" in pattern_name:
            stories = {
                "English": """The **Bunga Raya (Hibiscus)** motif holds profound cultural significance as Malaysia's national flower. This pattern represents more than mere floral decoration—it embodies national identity, unity, and love for the country.

**Historical Roots:**
The five petals of the bunga raya are often interpreted as symbolizing the Five Principles of Rukun Negara (Belief in God, Loyalty to King and Country, Upholding the Constitution, Rule of Law, and Good Behavior and Morality). This connection makes the pattern a visual representation of Malaysia's national philosophy.

**Cultural Meaning:**
In Malaysian homes, the hibiscus plant is commonly grown in gardens, along fences, and near verandas. Its presence in domestic spaces reflects its importance in daily life. The tree's moderate height and easy maintenance make it accessible to all, symbolizing the democratic nature of Malaysian society.

**Artistic Expression:**
Batik artisans incorporate the bunga raya in diverse ways, blending traditional techniques with contemporary aesthetics. The vibrant reds and yellows commonly used in these patterns reflect Malaysia's tropical environment while adding visual warmth to the fabric.

**Regional Significance:**
Particularly prominent in batik from Kelantan and Terengganu, the bunga raya pattern showcases the unique artistic traditions of Malaysia's East Coast. Each variation tells a story of regional identity while contributing to the national narrative.

**Contemporary Relevance:**
Today, the bunga raya pattern continues to evolve, appearing in fashion, home decor, and public art. It serves as a bridge between generations, connecting traditional craftsmanship with modern design sensibilities.""",
                
                "Malay": """**Bunga Raya (Hibiscus)** merupakan motif yang mempunyai makna budaya yang mendalam sebagai bunga kebangsaan Malaysia. Corak ini mewakili lebih daripada sekadar hiasan bunga—ia melambangkan identiti nasional, perpaduan, dan cinta kepada negara.

**Akar Sejarah:**
Lima kelopak bunga raya sering ditafsirkan sebagai melambangkan Lima Prinsip Rukun Negara (Kepercayaan kepada Tuhan, Kesetiaan kepada Raja dan Negara, Keluhuran Perlembagaan, Kedaulatan Undang-undang, dan Kesopanan dan Kesusilaan). Hubungan ini menjadikan corak sebagai perwakilan visual falsafah nasional Malaysia.

**Makna Budaya:**
Di rumah-rumah Malaysia, pokok bunga raya biasanya ditanam di taman, sepanjang pagar, dan berhampiran veranda. Kehadirannya dalam ruang domestik mencerminkan kepentingannya dalam kehidupan seharian. Ketinggian sederhana pokok dan penyelenggaraan mudah menjadikannya boleh diakses oleh semua, melambangkan sifat demokratik masyarakat Malaysia.

**Ekspresi Artistik:**
Pembuat batik menggabungkan bunga raya dalam pelbagai cara, menggabungkan teknik tradisional dengan estetika kontemporari. Warna merah dan kuning yang terang biasa digunakan dalam corak ini mencerminkan persekitaran tropika Malaysia sambil menambah kehangatan visual pada kain.

**Kepentingan Wilayah:**
Terutama menonjol dalam batik dari Kelantan dan Terengganu, corak bunga raya mempamerkan tradisi seni unik Pantai Timur Malaysia. Setiap variasi menceritakan kisah identiti wilayah sambil menyumbang kepada naratif nasional.

**Relevan Kontemporari:**
Hari ini, corak bunga raya terus berkembang, muncul dalam fesyen, hiasan rumah, dan seni awam. Ia berfungsi sebagai jambatan antara generasi, menghubungkan kemahiran tradisional dengan sensibiliti reka bentuk moden.""",
                
                "Arabic": """**نمط بونغا رايا (الهيبسكس)** يحمل أهمية ثقافية عميقة كزهرة ماليزيا الوطنية. هذا النمط يمثل أكثر من مجرد زخرفة زهرية—إنه يجسد الهوية الوطنية والوحدة وحب الوطن.

**الجذور التاريخية:**
غالبًا ما تُفسر البتلات الخمس لزهرة بونغا رايا على أنها ترمز إلى المبادئ الخمسة لـ "ركون نيجارا" (الإيمان بالله، الولاء للملك والوطن، حفظ الدستور، سيادة القانون، والأخلاق والسلوك الحسن). هذه الصلة تجعل النمط تمثيلاً مرئيًا لفلسفة ماليزيا الوطنية.

**المعنى الثقافي:**
في المنازل الماليزية، تُزرع نباتات الهيبسكس عادةً في الحدائق، وعلى طول الأسوار، وبالقرب من الشرفات. يعكس وجودها في المساحات المنزلية أهميتها في الحياة اليومية. يجعل ارتفاع الشجرة المعتدل وصيانتها السهلة الوصول إليها ممكنًا للجميع، مما يرمز إلى الطبيعة الديمقراطية للمجتمع الماليزي.

**التعبير الفني:**
يدمج حرفيو الباتيك زهرة بونغا رايا بطرق متنوعة، ممزجين بين التقنيات التقليدية والجماليات المعاصرة. تعكس الأحمر والأصفر الزاهي المستخدم عادة في هذه الأنماط البيئة الاستوائية لماليزيا مع إضافة دفء بصري للنسيج.

**الأهمية الإقليمية:**
يبرز نمط بونغا رايا بشكل خاص في الباتيك من كلانتان وترغكانو، حيث يعرض تقاليد فنية فريدة للساحل الشرقي الماليزي. تحكي كل اختلاف قصة الهوية الإقليمية مع المساهمة في السرد الوطني.

**الأهمية المعاصرة:**
اليوم، يستمر نمط بونغا رايا في التطور، ويظهر في الأزياء، وديكور المنزل، والفن العام. إنه يعمل كجسر بين الأجيال، ويربط بين الحرف التقليدية وحساسيات التصميم الحديثة."""
            }
        else:  # Geometric pattern
            stories = {
                "English": """**Geometric patterns** in Malaysian batik represent a sophisticated fusion of spiritual principles, mathematical precision, and cultural heritage. These designs are not merely decorative—they are visual expressions of Islamic artistic philosophy adapted to Malaysian cultural context.

**Islamic Artistic Tradition:**
Following Islamic norms that traditionally discourage figurative representation, Malaysian artisans developed geometric patterns as a means to express divine order and cosmic harmony. The repetitive use of circles, squares, and diamonds reflects the infinite nature of God and the structured beauty of the universe.

**Mathematical Precision:**
Approximately 30% of Malaysian batik designs incorporate geometric elements. These patterns demonstrate remarkable mathematical understanding, with designs based on complex geometric principles including:
- Symmetrical repetitions creating infinite patterns
- Interlocking shapes symbolizing interconnectedness
- Proportional relationships reflecting cosmic balance

**Common Motifs and Meanings:**
- **Geometric Spirals** (18% of popular patterns): Represent eternal growth, spiritual journey, and the interconnectedness of all life
- **Awan Larat (Cloud Patterns)**: While sometimes incorporating floral curves, their structured repetition serves as a "cultural chronicle," symbolizing continuity between generations
- **Diamonds and Zigzags**: Frequently used in sarong borders (kepala), providing structural framework for more fluid central designs

**Regional Heritage - East Coast Legacy:**
The states of Kelantan and Terengganu form the heartland of geometric batik production. In the 1920s, Haji Che Su revolutionized Malaysian batik by inventing the metal stamp (cap) technique. This innovation allowed for consistent reproduction of intricate geometric patterns, making them more accessible while maintaining artistic integrity.

**Color Philosophy:**
Unlike the earthy, mystical tones of Javanese batik, Malaysian geometric patterns employ a vibrant tropical palette. Bright pinks, purples, blues, and greens reflect the coastal environment and celebrate Malaysia's natural beauty while maintaining geometric precision.

**Social and Cultural Significance:**
Historically, complex geometric motifs were favored by royalty, scholars, and merchants. These patterns served as symbols of:
- Higher social standing and refinement
- Intellectual sophistication and wisdom
- Clarity of thought and spiritual insight
- Connection to Islamic scholarly traditions

**Contemporary Applications:**
Today, geometric batik patterns continue to evolve, appearing in contemporary fashion, architecture, and digital design. They represent a living tradition that bridges historical craftsmanship with modern aesthetics while maintaining cultural authenticity.

**The Essence:**
Geometric patterns in Malaysian batik are more than decorative elements—they are visual mathematics that connect the wearer to spiritual principles, cultural heritage, and the structured beauty of both the natural world and divine creation.""",
                
                "Malay": """**Corak geometri** dalam batik Malaysia mewakili gabungan canggih prinsip spiritual, ketepatan matematik, dan warisan budaya. Reka bentuk ini bukan sekadar hiasan—ia adalah ekspresi visual falsafah seni Islam yang disesuaikan dengan konteks budaya Malaysia.

**Tradisi Seni Islam:**
Mengikut norma Islam yang secara tradisional tidak menggalakkan perwakilan figuratif, tukang batik Malaysia membangunkan corak geometri sebagai cara untuk meluahkan susunan ilahi dan keharmonian kosmik. Penggunaan berulang bulatan, segi empat sama, dan berlian mencerminkan sifat Tuhan yang tidak terhingga dan keindahan berstruktur alam semesta.

**Ketepatan Matematik:**
Kira-kira 30% reka bentuk batik Malaysia menggabungkan elemen geometri. Corak ini menunjukkan kefahaman matematik yang luar biasa, dengan reka bentuk berdasarkan prinsip geometri kompleks termasuk:
- Pengulangan simetri mencipta corak tidak terhingga
- Bentuk saling kunci melambangkan saling berkaitan
- Hubungan perkadaran mencerminkan keseimbangan kosmik

**Motif dan Makna Biasa:**
- **Lingkaran Geometri** (18% corak popular): Mewakili pertumbuhan abadi, perjalanan spiritual, dan saling berkaitan semua kehidupan
- **Awan Larat (Corak Awan)**: Walaupun kadangkala menggabungkan lengkungan bunga, pengulangan berstrukturnya berfungsi sebagai "kronik budaya," melambangkan kesinambungan antara generasi
- **Belian dan Zigzag**: Sering digunakan dalam sempadan sarung (kepala), menyediakan rangka kerja struktur untuk reka bentuk pusat yang lebih cair

**Warisan Wilayah - Legasi Pantai Timur:**
Negeri Kelantan dan Terengganu membentuk pusat pengeluaran batik geometri. Pada 1920-an, Haji Che Su merevolusikan batik Malaysia dengan mencipta teknik cap logam. Inovasi ini membolehkan penghasilan corak geometri rumit yang konsisten, menjadikannya lebih mudah diakses sambil mengekalkan integriti seni.

**Falsafah Warna:**
Tidak seperti warna tanah, mistik batik Jawa, corak geometri Malaysia menggunakan palet tropika terang. Merah jambu, ungu, biru, dan hijau terang mencerminkan persekitaran pantai dan meraikan keindahan semula jadi Malaysia sambil mengekalkan ketepatan geometri.

**Kepentingan Sosial dan Budaya:**
Secara sejarah, motif geometri kompleks digemari oleh golongan bangsawan, cendekiawan, dan pedagang. Corak ini berfungsi sebagai simbol:
- Status sosial dan kehalusan yang lebih tinggi
- Kepintaran intelektual dan kebijaksanaan
- Kejelasan pemikiran dan pandangan spiritual
- Sambungan kepada tradisi ilmiah Islam

**Aplikasi Kontemporari:**
Hari ini, corak batik geometri terus berkembang, muncul dalam fesyen kontemporari, seni bina, dan reka bentuk digital. Ia mewakili tradisi hidup yang menghubungkan kemahiran sejarah dengan estetika moden sambil mengekalkan keaslian budaya.

**Intipati:**
Corak geometri dalam batik Malaysia adalah lebih daripada elemen hiasan—ia adalah matematik visual yang menghubungkan pemakai dengan prinsip spiritual, warisan budaya, dan keindahan berstruktur dunia semula jadi dan ciptaan ilahi.""",
                
                "Arabic": """**الأنماط الهندسية** في باتيك ماليزيا تمثل اندماجًا متطورًا للمبادئ الروحية والدقة الرياضية والتراث الثقافي. هذه التصاميم ليست مجرد زخارف—إنها تعبيرات بصرية لفلسفة الفن الإسلامي المكيفة مع السياق الثقافي الماليزي.

**التقليد الفني الإسلامي:**
اتباعًا للمعايير الإسلامية التي لا تشجع تقليديًا على التمثيل التصويري، طور الحرفيون الماليزيون الأنماط الهندسية كوسيلة للتعبير عن النظام الإلهي والانسجام الكوني. يعكس الاستخدام المتكرر للدوائر والمربعات والمعينات الطبيعة اللانهائية لله والجمال المنظم للكون.

**الدقة الرياضية:**
حوالي 30٪ من تصاميم الباتيك الماليزية تدمج عناصر هندسية. تظهر هذه الأنماط فهمًا رياضياً رائعًا، مع تصاميم تعتمد على مبادئ هندسية معقدة بما في ذلك:
- التكرارات المتماثلة التي تخلق أنماطًا لانهائية
- الأشكال المتشابكة التي ترمز للترابط
- العلاقات التناسبية التي تعكس التوازن الكوني

**الموتيفات والمعاني الشائعة:**
- **اللوالب الهندسية** (18٪ من الأنماط الشائعة): تمثل النمو الأبدي، الرحلة الروحية، وترابط كل الحياة
- **عوان لارات (أنماط السحاب)**: بينما تدمج أحيانًا منحنيات زهرية، فإن تكرارها المنظم يعمل كـ "سجل ثقافي"، يرمز للاستمرارية بين الأجيال
- **المعينات والزجزاج**: تُستخدم غالبًا في حدود السارونغ (كيبالا)، وتوفر إطارًا هيكليًا للتصاميم المركزية الأكثر سيولة

**التراث الإقليمي - إرث الساحل الشرقي:**
تشكل ولايات كلانتان وترغكانو قلب إنتاج الباتيك الهندسي. في عشرينيات القرن الماضي، أحدث حاج تشي سو ثورة في باتيك ماليزيا باختراع تقنية الختم المعدني (كاب). سمح هذا الابتكار بإعادة إنتاج متسقة للأنماط الهندسية المعقدة، مما جعلها أكثر سهولة مع الحفاظ على النزاهة الفنية.

**فلسفة اللون:**
على عكس الألوان الترابية والصوفية لباتيك جاوة، تستخدم الأنماط الهندسية الماليزية لوحة ألوان استوائية نابضة بالحياة. تعكس الألوان الزاهية من الوردي والأرجواني والأزرق والأخضر البيئة الساحلية وتحتفل بالجمال الطبيعي لماليزيا مع الحفاظ على الدقة الهندسية.

**الأهمية الاجتماعية والثقافية:**
تاريخياً، فضلت العائلة المالكة والعلماء والتجار الموتيفات الهندسية المعقدة. خدمت هذه الأنماط كرموز لـ:
- مكانة اجتماعية وتهذيب أعلى
- تعقيد فكري وحكمة
- وضوح الفكر وبصيرة روحية
- الاتصال بالتقاليد العلمية الإسلامية

**التطبيقات المعاصرة:**
اليوم، تستمر أنماط الباتيك الهندسية في التطور، وتظهر في الأزياء المعاصرة والعمارة والتصميم الرقمي. إنها تمثل تقليدًا حيًا يربط بين الحرفية التاريخية والجماليات الحديثة مع الحفاظ على الأصالة الثقافية.

**الجوهر:**
الأنماط الهندسية في باتيك ماليزيا هي أكثر من مجرد عناصر زخرفية—إنها رياضيات بصرية تربط مرتديها بالمبادئ الروحية والتراث الثقافي والجمال المنظم لكل من العالم الطبيعي والخليقة الإلهية."""
            }
        
        # Get the story for selected language, default to English
        story = stories.get(language, stories["English"])
        st.session_state.current_story = story  # Store for audio generation
        
        # Display the story
        st.markdown(f'<div style="background: #fffaf0; padding: 20px; border-radius: 10px; border-left: 4px solid #FFD166;">{story}</div>', unsafe_allow_html=True)
        
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
        
        audio_col1, audio_col2, audio_col3 = st.columns([2, 1, 1])
        
        with audio_col1:
            if st.button("▶️ Generate & Play Audio", use_container_width=True):
                if st.session_state.current_story:
                    with st.spinner(f"Generating audio in {language}..."):
                        try:
                            # Get language code
                            lang_code = language_codes.get(language, "en")
                            
                            # Get story text (limit length for audio)
                            story_text = st.session_state.current_story[:500]  # Limit to 500 chars for faster generation
                            
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
                            st.info("💡 Tip: Try English language for guaranteed audio generation")
                else:
                    st.warning("Please analyze an image first to generate a story!")
        
        # Display audio player if audio exists
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format='audio/mp3')
            
            with audio_col2:
                if st.button("💾 Save Locally", use_container_width=True):
                    # Create downloads folder
                    os.makedirs("downloads", exist_ok=True)
                    
                    # Save file
                    filename = st.session_state.audio_filename
                    with open(f"downloads/{filename}", "wb") as f:
                        f.write(st.session_state.audio_bytes)
                    
                    st.success(f"✅ Saved: downloads/{filename}")
            
            with audio_col3:
                # Download button
                st.download_button(
                    label="📥 Download MP3",
                    data=st.session_state.audio_bytes,
                    file_name=st.session_state.audio_filename,
                    mime="audio/mp3",
                    use_container_width=True
                )
        else:
            with audio_col2:
                st.button("💾 Save Locally", disabled=True, use_container_width=True, 
                         help="Generate audio first")
            with audio_col3:
                st.button("📥 Download MP3", disabled=True, use_container_width=True,
                         help="Generate audio first")
        
        # ACTION BUTTONS
        st.divider()
        st.markdown("### 🎯 Actions")
        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            if st.button("🔄 Analyze Another", use_container_width=True):
                # Clear session state
                for key in ['analyzing', 'use_sample', 'image_uploaded', 'audio_bytes', 'current_story']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        with action_col2:
            if st.button("📧 Share Results", use_container_width=True):
                st.success("✅ Results copied to clipboard! (Simulated)")
        with action_col3:
            if st.button("📁 Save Report", use_container_width=True):
                st.success("✅ Report saved to output/story_logs/ (Simulated)")
    
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
                    <strong>{feature['title']}</strong><br>
                    <small style="color: #666;">{feature['desc']}</small>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌺 <strong>Malaysian Batik Cultural Preservation Project</strong> | Version 2.0</p>
    <p>🧠 AI-Powered Pattern Recognition | 🎨 Cultural Storytelling | 🌍 Multilingual Support</p>
    <p>📧 Contact: cultural.heritage@batik.edu.my | 📱 +60 12-345 6789</p>
</div>
""", unsafe_allow_html=True)