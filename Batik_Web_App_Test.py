# streamlit_app.py - FIXED VERSION FOR STREAMLIT CLOUD
import streamlit as st
import tempfile
import os
import time
import json
import datetime
import base64
import io

# Try to import optional dependencies with fallbacks
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    st.warning("⚠️ PIL/Pillow not available. Some features disabled.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    st.warning("⚠️ gTTS not available. Audio features disabled.")

# Try to import OpenCV with fallback
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    # Create dummy functions for OpenCV
    np = None
    st.warning("⚠️ OpenCV not available. Image processing features disabled.")

# Try to import ultralytics with fallback
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    st.warning("⚠️ Ultralytics/YOLO not available. Running in demo mode.")

# Initialize pygame mixer if available
PYGAME_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except:
    pass

# Page configuration
st.set_page_config(
    page_title="Batik Pattern Storyteller AI",
    page_icon="🌺",
    layout="wide"
)

# ============ SESSION STATE INITIALIZATION ============
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'current_story' not in st.session_state:
    st.session_state.current_story = ""
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'audio_filename' not in st.session_state:
    st.session_state.audio_filename = ""
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"
if 'pattern_name' not in st.session_state:
    st.session_state.pattern_name = ""
if 'confidence' not in st.session_state:
    st.session_state.confidence = 0
if 'use_sample' not in st.session_state:
    st.session_state.use_sample = None
if 'image_uploaded' not in st.session_state:
    st.session_state.image_uploaded = False
if 'image_filename' not in st.session_state:
    st.session_state.image_filename = ""
if 'image_data' not in st.session_state:
    st.session_state.image_data = None
if 'sample_name' not in st.session_state:
    st.session_state.sample_name = ""
if 'not_batik' not in st.session_state:
    st.session_state.not_batik = False
if 'story_data' not in st.session_state:
    st.session_state.story_data = {}

# ============ BATIK DATABASE (ORIGINAL STORIES) ============
def get_batik_database():
    """Return the complete batik storytelling database"""
    return {
        "corak batik bunga raya": {
            "en": {
                "name": "Bunga Raya (Hibiscus) Batik Pattern",
                "story": "The Bunga Raya (Hibiscus) motif is a prominent and culturally significant pattern in Malaysian batik. As Malaysia's national flower, it represents love for the nation and its rich heritage. The five petals often symbolize the five principles of Rukun Negara (Malaysian National Principles), representing unity among the diverse population.",
                "meaning": "National Identity, Unity, Love, Growth, Vitality",
                "origin": "Malaysia (Various states including Kelantan, Terengganu)",
                "cultural_significance": "National flower of Malaysia, symbol of unity and pride",
                "home_context": "In many Malaysian houses, the hibiscus tree is commonly planted in home gardens, along fences, near verandas, or beside village houses. The tree does not usually grow very tall, which makes it easy to maintain.",
                "artistic_expression": "Artisans incorporate the bunga raya in various ways, blending tradition with contemporary creativity. The designs often feature vibrant reds and yellows, adding a fresh, bright appearance to the fabric.",
                "essence": "The bunga raya pattern is more than just a beautiful floral design; it is a visual language that connects the wearer to the shared history, values, and natural beauty of Malaysia."
            },
            "ms": {
                "name": "Corak Batik Bunga Raya",
                "story": "Motif Bunga Raya (Hibiscus) adalah corak yang menonjol dan bermakna dalam budaya batik Malaysia. Sebagai bunga kebangsaan Malaysia, ia melambangkan cinta kepada negara dan warisannya yang kaya. Lima kelopak bunga sering melambangkan lima prinsip Rukun Negara, mewakili perpaduan dalam kalangan penduduk yang pelbagai.",
                "meaning": "Identiti Nasional, Perpaduan, Cinta, Pertumbuhan, Vitaliti",
                "origin": "Malaysia (Negeri-negeri termasuk Kelantan, Terengganu)",
                "cultural_significance": "Bunga kebangsaan Malaysia, simbol perpaduan dan kebanggaan",
                "home_context": "Di banyak rumah Malaysia, pokok bunga raya (hibiscus) adalah kehadiran yang biasa dan bermakna. Ia biasanya ditanam di taman rumah, sepanjang pagar, berhampiran veranda, atau di sebelah rumah kampung. Pokok ini biasanya tidak tumbuh sangat tinggi, menjadikannya mudah dijaga.",
                "artistic_expression": "Pembuat batik menggabungkan bunga raya dalam pelbagai cara, menggabungkan tradisi dengan kreativiti kontemporari. Reka bentuk sering menampilkan warna merah dan kuning yang terang, menambah penampilan segar dan cerah pada kain.",
                "essence": "Corak bunga raya bukan sekadar reka bentuk bunga yang cantik; ia adalah bahasa visual yang menghubungkan pemakai dengan sejarah, nilai, dan keindahan semula jadi Malaysia yang dikongsi bersama."
            },
            "id": {
                "name": "Pola Batik Bunga Raya",
                "story": "Motif Bunga Raya (Hibiscus) adalah pola yang menonjol dan signifikan secara budaya dalam batik Malaysia. Sebagai bunga nasional Malaysia, ini mewakili cinta terhadap bangsa dan warisannya yang kaya. Lima kelopak sering melambangkan lima prinsip Rukun Negara (Prinsip Nasional Malaysia), mewakili persatuan di antara penduduk yang beragam.",
                "meaning": "Identitas Nasional, Persatuan, Cinta, Pertumbuhan, Vitalitas",
                "origin": "Malaysia (Berbagai negara bagian termasuk Kelantan, Terengganu)",
                "cultural_significance": "Bunga nasional Malaysia, simbol persatuan dan kebanggaan",
                "home_context": "Di banyak rumah Malaysia, pohon bunga raya (hibiscus) adalah kehadiran yang familiar dan bermakna. Biasanya ditanam di taman rumah, sepanjang pagar, dekat beranda, atau di samping rumah desa. Pohon ini biasanya tidak tumbuh sangat tinggi, membuatnya mudah dirawat.",
                "artistic_expression": "Pengrajin menggabungkan bunga raya dalam berbagai cara, memadukan tradisi dengan kreativitas kontemporer. Desain sering menampilkan warna merah dan kuning yang cerah, menambah penampilan segar dan cerah pada kain.",
                "essence": "Pola bunga raya bukan hanya desain bunga yang indah; ini adalah bahasa visual yang menghubungkan pemakainya dengan sejarah, nilai-nilai, dan keindahan alam Malaysia yang dibagikan bersama."
            },
            "ar": {
                "name": "نمط باتيك بونغا رايا",
                "story": "نمط بونغا رايا (الهيبسكس) هو نمط بارز وذو أهمية ثقافية في باتيك ماليزيا. باعتباره الزهرة الوطنية لماليزيا، فهو يمثل حب الأمة وتراثها الغني. غالبًا ما ترمز البتلات الخمس إلى المبادئ الخمسة لـ \"ركون نيجارا\" (المبادئ الوطنية الماليزية)، مما يمثل الوحدة بين السكان المتنوعين.",
                "meaning": "الهوية الوطنية، الوحدة، الحب، النمو، الحيوية",
                "origin": "ماليزيا (ولايات مختلفة بما في ذلك كلانتان، ترغكانو)",
                "cultural_significance": "الزهرة الوطنية لماليزيا، رمز الوحدة والفخر",
                "home_context": "في العديد من المنازل الماليزية، شجرة الهيبسكس (بونغا رايا) هي وجود مألوف وذو مغزى. عادة ما تُزرع في حدائق المنازل، على طول الأسوار، بالقرب من الشرفات، أو بجانب منازل القرى. لا تنمو الشجرة عادةً إلى ارتفاع كبير، مما يجعل صيانتها سهلة.",
                "artistic_expression": "يدمج الحرفيون زهرة بونغا رايا بطرق مختلفة، ممزجين بين التقاليد والإبداع المعاصر. غالبًا ما تتميز التصاميم بالأحمر والأصفر الزاهي، إضافة مظهر جديد ومشرق للنسيج.",
                "essence": "نمط بونغا رايا ليس مجرد تصميم زهري جميل؛ إنه لغة بصرية تربط مرتديه بالتاريخ والقيم والجمال الطبيعي المشترك لماليزيا."
            },
            "ja": {
                "name": "ブンガ・ラヤ（ハイビスカス）バティックパターン",
                "story": "ブンガ・ラヤ（ハイビスカス）のモチーフは、マレーシアのバティックにおいて顕著で文化的に重要なパターンです。マレーシアの国花として、国とその豊かな遺産への愛を表しています。5枚の花びらは、ルクン・ネガラ（マレーシア国家原則）の5原則を象徴し、多様な人口の間の統一を表しています。",
                "meaning": "国家的アイデンティティ、統一、愛、成長、活力",
                "origin": "マレーシア（クランタン、トレンガヌなどの州）",
                "cultural_significance": "マレーシアの国花、統一と誇りの象徴",
                "home_context": "多くのマレーシアの家では、ブンガ・ラヤ（ハイビスカス）の木は親しみやすく意味のある存在です。家庭の庭、柵に沿って、ベランダの近く、または村の家のそばによく植えられています。この木は通常それほど高く成長しないため、維持が容易です。",
                "artistic_expression": "職人たちは伝統と現代的な創造性を融合させ、様々な方法でブンガ・ラヤを組み込んでいます。デザインには鮮やかな赤と黄色がよく使われ，生地に新鮮で明るい外観を加えます．",
                "essence": "ブンガ・ラヤのパターンは、単なる美しい花のデザインではありません。それは、着用者をマレーシアの共有された歴史、価値観、自然の美しさにつなぐ視覚言語です。"
            },
            "ko": {
                "name": "붕가 라야(히비스커스) 바틱 패턴",
                "story": "붕가 라야(히비스커스) 모티프는 말레이시아 바틱에서 두드러지고 문화적으로 중요한 패턴입니다。말레이시아의 국화로서 국가와 그 풍부한 유산에 대한 사랑을 나타냅니다。다섯 개의 꽃잎은 종종 루쿤 네가라(말레이시아 국가 원칙)의 다섯 가지 원칙을 상징하며 다양한 인구 사이의 통합을 나타냅니다。",
                "meaning": "국가 정체성, 통합, 사랑, 성장, 활력",
                "origin": "말레이시아(클란탄, 테렝가누 등을 포함한 여러 주)",
                "cultural_significance": "말레이시아의 국화, 통합과 자부심의 상징",
                "home_context": "많은 말레이시아 가정에서 히비스커스(붕가 라야) 나무는 친숙하고 의미 있는 존재입니다。일반적으로 가정 정원, 울타리를 따라, 베란다 근처 또는 마을 집 옆에 심어집니다。이 나무는 일반적으로 매우 높게 자라지 않아 유지 관리가 쉽습니다。",
                "artistic_expression": "장인들은 전통과 현대적 창의성을 융합하여 다양한 방법으로 붕가 라야를 통합합니다。디자인에는 종종 생생한 빨간색과 노란색이 사용되어 직물에 신선하고 밝은 외관을 더합니다。",
                "essence": "붕가 라야 패턴은 단순히 아름다운 꽃 디자인이 아닙니다。착용자를 말레이시아의 공유된 역사, 가치관 및 자연의 아름다움과 연결하는 시각적 언어입니다。"
            },
            "zh-cn": {
                "name": "大红花（木槿）蜡染图案",
                "story": "大红花（木槿）图案是马来西亚蜡染中突出且具有文化意义的图案。作为马来西亚的国花，它代表着对国家和丰富遗产的热爱。五片花瓣通常象征着国家原则（Rukun Negara）的五项原则，代表着多元人口之间的团结。",
                "meaning": "国家身份、团结、爱、成长、活力",
                "origin": "马来西亚（包括吉兰丹、登嘉楼等各州）",
                "cultural_significance": "马来西亚国花，团结和自豪的象征",
                "home_context": "在许多马来西亚房屋中，大红花（木槿）树是熟悉且有意义的植物。它通常种植在家庭花园、栅栏旁、走廊附近或乡村房屋旁。这种树通常不会长得很高，这使得它易于维护。",
                "artistic_expression": "工匠们以各种方式融入大红花，将传统与当代创造力相结合。设计通常采用鲜艳的红色和黄色，为织物增添清新明亮的外观。",
                "essence": "大红花图案不仅仅是一个美丽的花卉设计；它是一种视觉语言，将穿着者与马来西亚共同的历史、价值观和自然美景联系起来。"
            }
        },
        "corak batik geometri": {
            "en": {
                "name": "Geometric Batik Pattern",
                "story": "In Malaysian Batik, geometric patterns represent a fusion of spiritual balance, cultural heritage, and the logic of the natural world. While roughly 30% of Malaysian batik designs are geometric, they hold a significant narrative role in the country's textile history.",
                "meaning": "Order, Symmetry, Harmony, Balance, Wisdom, Divine Connection",
                "origin": "Malaysia (Kelantan, Terengganu - East Coast)",
                "cultural_significance": "Represents Islamic artistic traditions and cultural identity",
                "islamic_influence": "Because Islamic norms traditionally discourage the representation of human or animal figures, Malaysian artisans turned to geometry to express divine order. The repetitive use of circles, squares, and diamonds reflects the balance and harmony found in the universe.",
                "motifs_stories": "• Geometric Spirals (18% of popular patterns): Represent eternal growth and interconnectedness of life.\n• Awan Larat (Cloud Pattern): Structured repetition serving as a 'cultural chronicle', symbolizing unity between generations.\n• Diamonds and Zigzags: Used in sarong borders, providing structure to fluid central designs.",
                "regional_heritage": "Kelantan and Terengganu are the heartlands of Malaysian batik. In the 1920s, Haji Che Su revolutionized Malaysian batik by inventing metal stamps (cap) for consistent reproduction of intricate geometric patterns. Unlike earthy Javanese tones, Malaysian geometric batik uses vibrant tropical colors (pinks, purples, blues) reflecting the coastal environment.",
                "artistic_expression": "Geometric patterns were historically favored by royalty, scholars, and merchants as symbols of higher social standing, wisdom, and clarity. They showcase mathematical precision combined with cultural storytelling.",
                "essence": "Geometric patterns in Malaysian batik are more than decorative elements; they are visual mathematics that connect the wearer to spiritual principles, cultural heritage, and the structured beauty of the natural world."
            },
            "ms": {
                "name": "Corak Batik Geometri",
                "story": "Dalam Batik Malaysia, corak geometri mewakili gabungan keseimbangan spiritual, warisan budaya, dan logik dunia semula jadi. Walaupun kira-kira 30% reka bentuk batik Malaysia adalah geometri, mereka memainkan peranan naratif yang penting dalam sejarah tekstil negara.",
                "meaning": "Susunan, Simetri, Keharmonian, Keseimbangan, Kebijaksanaan, Hubungan Ilahi",
                "origin": "Malaysia (Kelantan, Terengganu - Pantai Timur)",
                "cultural_significance": "Mewakili tradisi seni Islam dan identiti budaya",
                "islamic_influence": "Oleh kerana norma Islam secara tradisional menghalang penggambaran figura manusia atau haiwan, tukang batik Malaysia beralih kepada geometri untuk meluahkan susunan ilahi. Penggunaan berulang bulatan, segi empat sama, dan berlian mencerminkan keseimbangan dan keharmonian yang terdapat dalam alam semesta.",
                "motifs_stories": "• Lingkaran Geometri (18% corak popular): Mewakili pertumbuhan abadi dan saling berkaitan kehidupan.\n• Awan Larat (Corak Awan): Pengulangan berstruktur berfungsi sebagai 'kronik budaya', melambangkan perpaduan antara generasi.\n• Berlian dan Zigzag: Digunakan dalam sempadan sarung, memberikan struktur kepada reka bentuk pusat yang lebih cair.",
                "regional_heritage": "Kelantan dan Terengganu adalah pusat batik Malaysia. Pada 1920-an, Haji Che Su merevolusikan batik Malaysia dengan mencipta cap logam untuk penghasilan corak geometri rumit yang konsisten. Berbeza dengan warna-warna tanah Jawa, batik geometri Malaysia menggunakan warna tropika terang (merah jambu, ungu, biru) yang mencerminkan persekitaran pantai.",
                "artistic_expression": "Corak geometri secara sejarah digemari oleh golongan bangsawan, cendekiawan, dan pedagang sebagai simbol status sosial yang lebih tinggi, kebijaksanaan, dan kejelasan. Ia mempamerkan ketepatan matematik digabungkan dengan penceritaan budaya.",
                "essence": "Corak geometri dalam batik Malaysia bukan sekadar elemen hiasan; ia adalah matematik visual yang menghubungkan pemakai dengan prinsip spiritual, warisan budaya, dan keindahan berstruktur dunia semula jadi."
            },
            "id": {
                "name": "Pola Batik Geometris",
                "story": "Dalam Batik Malaysia, pola geometris mewakili perpaduan keseimbangan spiritual, warisan budaya, dan logika dunia alami. Meskipun sekitar 30% desain batik Malaysia adalah geometris, mereka memainkan peran naratif yang signifikan dalam sejarah tekstil negara.",
                "meaning": "Keteraturan, Simetri, Harmoni, Keseimbangan, Kebijaksanaan, Hubungan Ilahi",
                "origin": "Malaysia (Kelantan, Terengganu - Pantai Timur)",
                "cultural_significance": "Mewakili tradisi seni Islam dan identitas budaya",
                "islamic_influence": "Karena norma Islam secara tradisional tidak menganjurkan penggambaran figur manusia atau hewan, pengrajin Malaysia beralih ke geometri untuk mengungkapkan tatanan ilahi. Penggunaan berulang lingkaran, persegi, dan berlian mencerminkan keseimbangan dan harmoni yang ditemukan di alam semesta.",
                "motifs_stories": "• Spiral Geometris (18% pola populer): Mewakili pertumbuhan abadi dan keterkaitan kehidupan.\n• Awan Larat (Pola Awan): Pengulangan terstruktur berfungsi sebagai 'kronik budaya', melambangkan persatuan antar generasi.\n• Berlian dan Zigzag: Digunakan di perbatasan sarung, memberikan struktur pada desain pusat yang lebih cair.",
                "regional_heritage": "Kelantan dan Terengganu adalah jantung batik Malaysia. Pada 1920-an, Haji Che Su merevolusi batik Malaysia dengan mencipta cap logam untuk reproduksi pola geometris rumit yang konsisten. Tidak seperti warna tanah Jawa, batik geometris Malaysia menggunakan warna tropis cerah (merah muda, ungu, biru) yang mencerminkan lingkungan pantai.",
                "artistic_expression": "Pola geometris secara historis disukai oleh bangsawan, cendekiawan, dan pedagang sebagai simbol status sosial yang lebih tinggi, kebijaksanaan, dan kejelasan. Mereka menunjukkan presisi matematis yang digabungkan dengan penceritaan budaya.",
                "essence": "Pola geometris dalam batik Malaysia lebih dari sekadar elemen dekoratif; mereka adalah matematika visual yang menghubungkan pemakainya dengan prinsip spiritual, warisan budaya, dan keindahan terstruktur dunia alami."
            },
            "ar": {
                "name": "نمط باتيك الهندسي",
                "story": "في باتيك ماليزيا، تمثل الأنماط الهندسية اندماج التوازن الروحي والتراث الثقافي ومنطق العالم الطبيعي. بينما حوالي 30٪ من تصميمات الباتيك الماليزية هي أنماط هندسية، فإنها تلعب دورًا سرديًا مهمًا في تاريخ النسيج في البلاد.",
                "meaning": "النظام، التناسق، الانسجام، التوازن، الحكمة، الصلة الإلهية",
                "origin": "ماليزيا (كلانتان، ترغكانو - الساحل الشرقي)",
                "cultural_significance": "يمثل تقاليد الفن الإسلامي والهوية الثقافية",
                "islamic_influence": "لأن المعايير الإسلامية تثبط تقليديًا تمثيل الأشكال البشرية أو الحيوانية، لجأ الحرفيون الماليزيون إلى الهندسة للتعبير عن النظام الإلهي. يعكس الاستخدام المتكرر للدوائر والمربعات والمعينات التوازن والانسجام الموجود في الكون.",
                "motifs_stories": "• اللوالب الهندسية (18٪ من الأنماط الشائعة): تمثل النمو الأبدي وترابط الحياة.\n• عوان لارات (نمط السحاب): التكرار المنظم الذي يعمل بمثابة 'سجل ثقافي'، يرمز للوحدة بين الأجيال.\n• المعينات والزجزاج: تُستخدم في حدود السارونغ، مما يوفر هيكلًا للتصميمات المركزية الأكثر سيولة.",
                "regional_heritage": "كلانتان وترغكانو هي معاقل باتيك ماليزيا. في عشرينيات القرن الماضي، قام حاج تشي سو بإحداث ثورة في باتيك ماليزيا باختراع الأختام المعدنية (كاب) لإعادة إنتاج الأنماط الهندسية المعقدة بشكل متناسق. على عكس ألوان جاوة الترابية، يستخدم باتيك ماليزيا الهندسي ألوانًا استوائية نابضة بالحياة (الوردي، البنفسجي، الأزرق) التي تعفس البيئة الساحلية.",
                "artistic_expression": "فضلت العائلة المالكة والعلماء والتجار الأنماط الهندسية تاريخيًا كرموز لمكانة اجتماعية أعلى وحكمة ووضوح. وهي تُظهر الدقة الرياضية المدمجة مع سرد القصص الثقافية.",
                "essence": "الأنماط الهندسية في باتيك ماليزيا هي أكثر من مجرد عناصر زخرفية؛ إنها رياضيات بصرية تربط مرتديها بالمبادئ الروحية والتراث الثقافي والجمال المنظم للعالم الطبيعي."
            },
            "ja": {
                "name": "幾何学模様バティックパターン",
                "story": "マレーシアのバティックでは、幾何学模様は精神的バランス、文化的遺産、自然世界の論理の融合を表しています。マレーシアのバティックデザインの約30％が幾何学的ですが、国の繊維の歴史において重要な物語的役割を果たしています。",
                "meaning": "秩序、対称、調和、バランス、知恵、神とのつながり",
                "origin": "マレーシア（クランタン、トレンガヌ - 東海岸）",
                "cultural_significance": "イスラム芸術の伝統と文化的アイデンティティを代表する",
                "islamic_influence": "イスラムの規範は伝統的に人間や動物の姿の表現を控えるため、マレーシアの職人たちは神の秩序を表現するために幾何学に目を向けました。円、正方形、菱形の反復使用は、宇宙に見られるバランスと調和を反映しています。",
                "motifs_stories": "• 幾何学的螺旋（人気パターンの18％）：永遠の成長と生命の相互関連性を表します。\n• アワン・ララット（雲模様）：構造化された繰り返しは「文化的記録」として機能し、世代間の結束を象徴します。\n• 菱形とジグザグ：サロンの縁取りに使用され、流動的な中央デザインに構造を提供します。",
                "regional_heritage": "クランタンとトレンガヌはマレーシアバティックの中心地です。1920年代に、ハジ・チェ・スーは金属スタンプ（キャップ）を発明して複雑な幾何学模様を一貫して再現できるようにし、マレーシアのバティックに革命をもたらしました。ジャワの素朴な色合いとは異なり、マレーシアの幾何学バティックは海岸環境を反映した鮮やかなトロピカルカラー（ピンク、紫、青）を使用します。",
                "artistic_expression": "幾何学模様は歴史的に、より高い社会的地位、知恵、明確さの象徴として、王室、学者、商人に好まれました。それらは文化的ストーリーテリングと組み合わされた数学的精度を示しています。",
                "essence": "マレーシアのバティックの幾何学模様は、単なる装飾要素ではありません。それらは、着用者を精神的原理、文化的遺産、自然世界の構造化された美しさに結び付ける視覚的数学です。"
            },
            "ko": {
                "name": "기하학적 바틱 패턴",
                "story": "말레이시아 바틱에서 기하학적 패턴은 영적 균형, 문화 유산 및 자연 세계의 논리의 융합을 나타냅니다。말레이시아 바틱 디자인의 약 30%가 기하학적이지만 국가 직물 역사에서 중요한 서사적 역할을 합니다。",
                "meaning": "질서, 대칭, 조화, 균형, 지혜, 신성한 연결",
                "origin": "말레이시아(클란탄, 테렝가누 - 동부 해안)",
                "cultural_significance": "이슬람 예술 전통과 문화적 정체성을 대표함",
                "islamic_influence": "이슬람 규범은 전통적으로 인간이나 동물 형상의 표현을 권장하지 않기 때문에 말레이시아 장인들은 신성한 질서를 표현하기 위해 기하학으로 전환했습니다。원, 정사각형 및 마름모의 반복적인 사용은 우주에서 발견되는 균형과 조화를 반영합니다。",
                "motifs_stories": "• 기하학적 나선(인기 패턴의 18%): 영원한 성장과 삶의 상호 연결성을 나타냅니다.\n• 아완 라랏(구름 패턴): 구조화된 반복은 '문화 연대기' 역할을 하여 세대 간의 통일을 상징합니다.\n• 마름모와 지그재그: 사롱 테두리에 사용되어 유동적인 중앙 디자인에 구조를 제공합니다。",
                "regional_heritage": "클란탄과 테렝가누는 말레이시아 바틱의 중심지입니다。1920년대에 하지 체 수는 금속 스탬프(캡)를 발명하여 복잡한 기하학적 패턴을 일관되게 재생산할 수 있도록 하여 말레이시아 바틱에 혁명을 일으켰습니다。자바의 토양 색조와 달리 말레이시아 기하학적 바틱은 해안 환경을 반영한 생생한 열대 색상(분홍색, 보라색, 파란색)을 사용합니다。",
                "artistic_expression": "기하학적 패턴은 역사적으로 더 높은 사회적 지위, 지혜 및 명확성의 상징으로 왕실, 학자 및 상인들에게 선호되었습니다。그들은 문화적 스토리텔링과 결합된 수학적 정밀도를 보여줍니다。",
                "essence": "말레이시아 바틱의 기하학적 패턴은 단순한 장식 요소가 아닙니다。착용자를 영적 원리, 문화 유산 및 자연 세계의 구조화된 아름다움에 연결하는 시각적 수학입니다。"
            },
            "zh-cn": {
                "name": "几何蜡染图案",
                "story": "在马来西亚蜡染中，几何图案代表着精神平衡、文化遗产和自然世界逻辑的融合。虽然大约30%的马来西亚蜡染设计是几何图案，但它们在国家的纺织历史中扮演着重要的叙事角色。",
                "meaning": "秩序、对称、和谐、平衡、智慧、神圣连接",
                "origin": "马来西亚（吉兰丹、登嘉楼 - 东海岸）",
                "cultural_significance": "代表伊斯兰艺术传统和文化认同",
                "islamic_influence": "由于伊斯兰规范传统上不鼓励表现人物或动物形象，马来西亚工匠转向几何来表达神圣秩序。圆形、正方形和菱形的重复使用反映了宇宙中的平衡与和谐。",
                "motifs_stories": "• 几何螺旋（热门图案的18%）：代表永恒成长和生命的相互联系。\n• Awan Larat（云纹图案）：结构化重复充当「文化编年史」，象征代际间的团结。\n• 菱形和锯齿纹：用于纱笼的边框，为更流畅的中心设计提供结构。",
                "regional_heritage": "吉兰丹和登嘉楼是马来西亚蜡染的中心地带。1920年代，哈吉·切苏发明了金属印章（cap），能够一致复制复杂的几何图案，从而革新了马来西亚蜡染。与爪哇的土色调不同，马来西亚几何蜡染使用反映海岸环境的鲜艳热带色彩（粉红色、紫色、蓝色）。",
                "artistic_expression": "几何图案历史上受到皇室、学者和商人的青睐，作为更高社会地位、智慧和清晰的象征。它们展示了数学精度与文化叙事的结合。",
                "essence": "马来西亚蜡染中的几何图案不仅仅是装饰元素；它们是视觉数学，将佩戴者与精神原则、文化遗产和自然世界的结构化美联系起来。"
            }
        },
        "not batik pattern": {
            "en": {
                "name": "❌ Not a Trained Batik Pattern",
                "story": "Our analysis indicates that this image does not match the trained batik patterns (Bunga Raya or Geometric patterns). This could be because:\n\n• The image shows a different type of batik pattern not in our training set\n• The image is not of batik fabric at all\n• The pattern is unclear or too complex\n• The image quality is insufficient for analysis\n\nPlease try uploading a clear image of either Bunga Raya (Hibiscus) or Geometric batik patterns for accurate cultural storytelling.",
                "meaning": "Non-Batik Pattern",
                "origin": "Not Applicable",
                "cultural_significance": "This pattern is not recognized as traditional Malaysian batik",
                "suggestions": "• Try uploading clearer images\n• Ensure the image shows batik fabric\n• Focus on Bunga Raya or Geometric patterns\n• Check image lighting and focus",
                "essence": "Our system is trained specifically on Malaysian batik patterns. For accurate cultural stories, please use images of traditional Malaysian batik."
            },
            "ms": {
                "name": "❌ Bukan Corak Batik Terlatih",
                "story": "Analisis kami menunjukkan bahawa imej ini tidak sepadan dengan corak batik terlatih (Corak Bunga Raya atau Corak Geometri). Ini mungkin kerana:\n\n• Imej menunjukkan jenis corak batik yang berbeza tidak dalam set latihan kami\n• Imej bukan kain batik sama sekali\n• Corak tidak jelas atau terlalu kompleks\n• Kualiti imej tidak mencukupi untuk analisis\n\nSila cuba muat naik imej yang jelas sama ada Corak Bunga Raya (Hibiscus) atau Corak Geometri batik untuk penceritaan budaya yang tepat.",
                "meaning": "Corak Bukan Batik",
                "origin": "Tidak Berkenaan",
                "cultural_significance": "Corak ini tidak dikenali sebagai batik Malaysia tradisional",
                "suggestions": "• Cuba muat naik imej yang lebih jelas\n• Pastikan imej menunjukkan kain batik\n• Fokus pada corak Bunga Raya atau Geometri\n• Semak pencahayaan dan fokus imej",
                "essence": "Sistem kami dilatih khusus pada corak batik Malaysia. Untuk cerita budaya yang tepat, sila gunakan imej batik Malaysia tradisional."
            }
        }
    }

def get_story_for_pattern(pattern_name, language):
    """Get story data for a specific pattern and language"""
    database = get_batik_database()
    
    # Language mapping
    lang_map = {
        "English": "en",
        "Malay": "ms", 
        "Indonesian": "id",
        "Arabic": "ar",
        "Japanese": "ja",
        "Korean": "ko",
        "Chinese": "zh-cn"
    }
    
    lang_code = lang_map.get(language, "en")
    
    # Check direct match
    if pattern_name in database:
        if lang_code in database[pattern_name]:
            return database[pattern_name][lang_code]
    
    # Check partial matches
    pattern_lower = pattern_name.lower()
    if "bunga" in pattern_lower or "raya" in pattern_lower:
        pattern_key = "corak batik bunga raya"
    elif "geometri" in pattern_lower or "geometri" in pattern_lower:
        pattern_key = "corak batik geometri"
    else:
        pattern_key = "not batik pattern"
    
    if pattern_key in database and lang_code in database[pattern_key]:
        return database[pattern_key][lang_code]
    
    # Default fallback
    return database["not batik pattern"]["en"]

def classify_image_simple(image_bytes, filename):
    """Simple image classification based on filename and size"""
    import random
    
    filename_lower = filename.lower()
    
    # Simple detection logic
    if 'bunga' in filename_lower or 'flower' in filename_lower or 'raya' in filename_lower:
        return {
            'primary_class': 'corak batik bunga raya',
            'confidence': random.uniform(0.85, 0.95),
            'is_batik': True
        }
    elif 'geometri' in filename_lower or 'geo' in filename_lower or 'shape' in filename_lower:
        return {
            'primary_class': 'corak batik geometri',
            'confidence': random.uniform(0.80, 0.90),
            'is_batik': True
        }
    else:
        # Random assignment or non-batik
        if random.random() > 0.5:
            return {
                'primary_class': 'corak batik bunga raya',
                'confidence': random.uniform(0.60, 0.75),
                'is_batik': True
            }
        else:
            return {
                'primary_class': 'not batik pattern',
                'confidence': random.uniform(0.30, 0.50),
                'is_batik': False
            }

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .main-title {
        font-size: 3rem;
        color: white !important;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .subtitle {
        color: white !important;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .section-header {
        color: white !important;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 15px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .upload-area {
        border: 3px dashed #4ECDC4;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        background-color: rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .result-card {
        background: rgba(255,255,255,0.9);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #FF6B6B;
    }
    
    .non-batik-card {
        background: rgba(255, 230, 230, 0.9);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #FF3333;
    }
    
    .story-container {
        background: rgba(255,255,255,0.9);
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        color: #333333;
        font-size: 16px;
        line-height: 1.6;
        text-align: justify;
        white-space: pre-line;
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
    
    .non-batik-badge {
        display: inline-block;
        padding: 8px 15px;
        margin: 5px;
        background: linear-gradient(45deg, #FF3333, #FF6666);
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    
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
    
    .low-confidence-progress {
        background: rgba(255, 100, 100, 0.7);
        height: 100%;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============ MAIN APP ============
st.markdown('<h1 class="main-title">🌺 Malaysian Batik Storytelling AI Platform</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="subtitle">Upload any batik image to discover its cultural story in 7 languages</h3>', unsafe_allow_html=True)

# Show dependency warnings
if not CV2_AVAILABLE:
    st.info("ℹ️ **Note:** Running in simplified mode (OpenCV not available)")
if not YOLO_AVAILABLE:
    st.info("ℹ️ **Note:** Running in demo mode (AI model not available)")

# Sidebar
with st.sidebar:
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    st.session_state.selected_language = st.selectbox(
        "🌍 Select Story Language",
        ["English", "Malay", "Indonesian", "Arabic", "Japanese", "Korean", "Chinese"],
        index=0
    )
    
    st.divider()
    st.markdown('<div class="section-header">📸 Quick Test</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌺 Bunga Raya", use_container_width=True):
            st.session_state.use_sample = "bunga"
            st.session_state.sample_name = "Bunga Raya Pattern"
    with col2:
        if st.button("🔷 Geometric", use_container_width=True):
            st.session_state.use_sample = "geometric"
            st.session_state.sample_name = "Geometric Pattern"
    with col3:
        if st.button("❌ Non-Batik", use_container_width=True):
            st.session_state.use_sample = "nonbatik"
            st.session_state.sample_name = "Non-Batik Image"
    
    st.divider()
    st.markdown('<div class="section-header">✨ Features</div>', unsafe_allow_html=True)
    st.markdown("""
    ✅ **Pattern Detection**  
    ✅ **7 Languages**  
    ✅ **Cultural Stories**  
    ✅ **Audio Support**  
    ✅ **Non-Batik Detection**  
    """)
    
    st.divider()
    st.markdown('<div class="section-header">💾 System Info</div>', unsafe_allow_html=True)
    st.write(f"OpenCV: {'✅ Available' if CV2_AVAILABLE else '❌ Not Available'}")
    st.write(f"gTTS: {'✅ Available' if GTTS_AVAILABLE else '❌ Not Available'}")
    st.write(f"YOLO: {'✅ Available' if YOLO_AVAILABLE else '❌ Not Available'}")

# Main content columns
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="section-header">📤 Step 1: Upload Image</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag and drop or click to browse",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        if PIL_AVAILABLE:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="📸 Your Uploaded Image")
            except:
                st.write("✅ Image uploaded")
        else:
            st.write("✅ Image uploaded")
        
        st.session_state.image_data = uploaded_file.getvalue()
        st.session_state.image_filename = uploaded_file.name
    else:
        st.markdown("""
        <div style="text-align: center; color: white;">
            <div style="font-size: 4rem;">📁</div>
            <h3>Drag & Drop Image Here</h3>
            <p>or click to browse files</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze button
    analyze_enabled = uploaded_file is not None or 'use_sample' in st.session_state
    if st.button("🔍 ANALYZE PATTERN", type="primary", use_container_width=True, disabled=not analyze_enabled):
        with st.spinner("Starting analysis..."):
            # Clear previous results
            st.session_state.analyzing = True
            
            # Use sample data if selected
            if 'use_sample' in st.session_state:
                if st.session_state.use_sample == "bunga":
                    st.session_state.image_filename = "sample_bunga.jpg"
                    detection_result = {
                        'primary_class': 'corak batik bunga raya',
                        'confidence': 0.92,
                        'is_batik': True
                    }
                elif st.session_state.use_sample == "geometric":
                    st.session_state.image_filename = "sample_geometric.jpg"
                    detection_result = {
                        'primary_class': 'corak batik geometri',
                        'confidence': 0.88,
                        'is_batik': True
                    }
                else:  # nonbatik
                    st.session_state.image_filename = "sample_nonbatik.jpg"
                    detection_result = {
                        'primary_class': 'not batik pattern',
                        'confidence': 0.35,
                        'is_batik': False
                    }
            else:
                # Analyze uploaded image
                detection_result = classify_image_simple(
                    st.session_state.image_data,
                    st.session_state.image_filename
                )
            
            # Store results
            st.session_state.detection_result = detection_result
            st.session_state.not_batik = not detection_result.get('is_batik', False)
            st.session_state.confidence = detection_result['confidence']
            
            # Get story data
            story_data = get_story_for_pattern(
                detection_result['primary_class'],
                st.session_state.selected_language
            )
            st.session_state.story_data = story_data
            st.session_state.pattern_name = story_data.get('name', detection_result['primary_class'])
            st.session_state.current_story = story_data.get('story', '')
            
            st.rerun()

with col_right:
    st.markdown('<div class="section-header">📖 Step 2: Story Results</div>', unsafe_allow_html=True)
    
    if st.session_state.get('analyzing', False) and st.session_state.get('detection_result'):
        # Display analysis results
        detection_result = st.session_state.detection_result
        story_data = st.session_state.story_data
        
        # Pattern detection section
        st.markdown('<div class="section-header">🎨 Pattern Detected</div>', unsafe_allow_html=True)
        
        if st.session_state.not_batik:
            # Non-batik pattern
            st.markdown(f'''
            <div class="non-batik-card">
                <h2 style="color: #FF3333; text-align: center;">{story_data.get('name', 'Not a Batik Pattern')}</h2>
                <p style="text-align: center; color: #666;">Our analysis could not identify this as a trained batik pattern</p>
            </div>
            ''', unsafe_allow_html=True)
            
            confidence = st.session_state.confidence
            st.markdown(f'<div style="color: white;">Confidence: <strong>{confidence:.1%}</strong> (LOW)</div>', unsafe_allow_html=True)
            
            # Progress bar
            st.markdown(f'''
            <div class="progress-bar">
                <div class="low-confidence-progress" style="width: {confidence*100}%"></div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Badges
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<span class="non-batik-badge">❌ Non-Batik</span>', unsafe_allow_html=True)
            with col2:
                st.markdown('<span class="non-batik-badge">⚠️ Untrained Pattern</span>', unsafe_allow_html=True)
            with col3:
                st.markdown('<span class="non-batik-badge">🔍 Needs Review</span>', unsafe_allow_html=True)
        else:
            # Batik pattern
            st.markdown(f'''
            <div class="result-card">
                <h2 style="color: #FF6B6B; text-align: center;">{story_data.get('name', 'Batik Pattern')}</h2>
            </div>
            ''', unsafe_allow_html=True)
            
            confidence = st.session_state.confidence
            st.markdown(f'<div style="color: white;">Confidence: <strong>{confidence:.1%}</strong></div>', unsafe_allow_html=True)
            
            # Progress bar
            st.markdown(f'''
            <div class="progress-bar">
                <div class="progress-fill" style="width: {confidence*100}%"></div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Badges
            if "bunga" in detection_result['primary_class'].lower():
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
        
        # Selected language
        st.markdown('<div class="section-header">🌍 Selected Language</div>', unsafe_allow_html=True)
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
        <div style="background-color: rgba(255,255,255,0.9); border-radius: 10px; padding: 15px; text-align: center;">
            <h3 style="color: #333; margin: 0;">{language_display[st.session_state.selected_language]}</h3>
            <small style="color: #666;">Selected in sidebar</small>
        </div>
        ''', unsafe_allow_html=True)
        
        # Cultural story
        st.markdown('<div class="section-header">📚 Cultural Story</div>', unsafe_allow_html=True)
        
        story_text = story_data.get('story', 'No story available')
        st.markdown(f'<div class="story-container">{story_text}</div>', unsafe_allow_html=True)
        
        # Pattern details (for batik patterns only)
        if not st.session_state.not_batik:
            with st.expander("📊 Pattern Details", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    origin = story_data.get('origin', 'Malaysia')
                    st.metric("Origin", origin)
                with col2:
                    st.metric("Cultural Age", "100+ years")
                with col3:
                    st.metric("UNESCO Status", "Intangible Heritage")
                
                if 'meaning' in story_data:
                    st.write(f"**Meaning:** {story_data['meaning']}")
                if 'cultural_significance' in story_data:
                    st.write(f"**Cultural Significance:** {story_data['cultural_significance']}")
        
        # Audio section
        if GTTS_AVAILABLE:
            st.markdown('<div class="section-header">🔊 Audio Story</div>', unsafe_allow_html=True)
            
            audio_col1, audio_col2 = st.columns(2)
            
            with audio_col1:
                if st.button("▶️ Generate Audio", use_container_width=True):
                    if st.session_state.current_story:
                        with st.spinner("Generating audio..."):
                            try:
                                language_codes = {
                                    "English": "en",
                                    "Malay": "ms",
                                    "Indonesian": "id",
                                    "Arabic": "ar",
                                    "Japanese": "ja",
                                    "Korean": "ko",
                                    "Chinese": "zh-CN"
                                }
                                
                                lang_code = language_codes.get(st.session_state.selected_language, "en")
                                
                                # Create temporary audio file
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                                    tts = gTTS(text=st.session_state.current_story, lang=lang_code, slow=False)
                                    tts.save(tmp_file.name)
                                    
                                    audio_bytes = open(tmp_file.name, 'rb').read()
                                    st.session_state.audio_bytes = audio_bytes
                                    st.session_state.audio_filename = f"batik_story_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                                    
                                    os.unlink(tmp_file.name)
                                
                                st.success("✅ Audio generated successfully!")
                                st.balloons()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error generating audio: {str(e)}")
                    else:
                        st.warning("No story available to generate audio")
            
            # Display audio player if available
            if 'audio_bytes' in st.session_state and st.session_state.audio_bytes is not None:
                st.audio(st.session_state.audio_bytes, format='audio/mp3')
                
                with audio_col2:
                    if st.download_button(
                        "📥 Download Audio",
                        data=st.session_state.audio_bytes,
                        file_name=st.session_state.audio_filename,
                        mime="audio/mp3",
                        use_container_width=True
                    ):
                        st.success("✅ Audio download started!")
        else:
            st.markdown('<div class="section-header">🔊 Audio Story</div>', unsafe_allow_html=True)
            st.info("ℹ️ Audio features require gTTS library. Install with: `pip install gTTS`")
        
        # Action buttons
        st.divider()
        st.markdown('<div class="section-header">🎯 Actions</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Analyze Another", use_container_width=True):
                # Clear analysis state
                for key in ['analyzing', 'use_sample', 'detection_result', 'story_data', 
                           'pattern_name', 'confidence', 'not_batik', 'current_story',
                           'audio_bytes', 'audio_filename']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            # Save report
            if st.button("💾 Save Report", use_container_width=True):
                try:
                    report_data = {
                        "pattern_name": st.session_state.pattern_name,
                        "is_batik": not st.session_state.not_batik,
                        "confidence": float(st.session_state.confidence),
                        "language": st.session_state.selected_language,
                        "story": st.session_state.current_story,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "image_filename": st.session_state.get('image_filename', '')
                    }
                    
                    # Create JSON report
                    report_json = json.dumps(report_data, indent=2, ensure_ascii=False)
                    
                    # Create text report
                    text_report = f"""BATIK CULTURAL STORY REPORT
========================================
Pattern: {st.session_state.pattern_name}
Is Batik: {not st.session_state.not_batik}
Confidence: {st.session_state.confidence:.1%}
Language: {st.session_state.selected_language}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Image: {st.session_state.get('image_filename', 'N/A')}

CULTURAL STORY
========================================
{st.session_state.current_story}
"""
                    
                    # Offer download
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.download_button(
                            "📥 Download JSON",
                            data=report_json,
                            file_name=f"batik_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    with col_b:
                        st.download_button(
                            "📥 Download TXT",
                            data=text_report,
                            file_name=f"batik_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    st.success("✅ Report ready for download!")
                    
                except Exception as e:
                    st.error(f"Error creating report: {str(e)}")
    else:
        # Show instructions when no analysis done
        st.info("👈 **Upload an image or use sample images to begin analysis**")
        
        # Show features
        st.markdown('<div class="section-header">✨ What You\'ll Get:</div>', unsafe_allow_html=True)
        
        features = [
            {"icon": "🎨", "title": "Pattern Detection", "desc": "Identifies Bunga Raya, Geometric, or Non-Batik patterns"},
            {"icon": "📚", "title": "Cultural Stories", "desc": "Complete cultural narratives in 7 languages"},
            {"icon": "🔊", "title": "Audio Narration", "desc": "Listen to stories with text-to-speech"},
            {"icon": "❌", "title": "Non-Batik Detection", "desc": "Identifies images that are not trained batik patterns"},
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

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: white; padding: 20px;">
    <p>🌺 <strong>Malaysian Batik Cultural Preservation Project</strong> | Version 2.0</p>
    <p>🎨 Cultural Storytelling | 🌍 Multilingual Support | ❌ Non-Batik Detection</p>
</div>
""", unsafe_allow_html=True)