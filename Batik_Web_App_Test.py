# batik_streamlit_app.py
import streamlit as st
import cv2
import os
from PIL import Image
import numpy as np
import tempfile
import base64
from ultralytics import YOLO
from gtts import gTTS
import io

# Set page configuration
st.set_page_config(
    page_title="Malaysian Batik Storyteller",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better fonts and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #2E7D32 !important;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #388E3C !important;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .section-header {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #4CAF50 !important;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #C8E6C9;
    }
    
    .info-text {
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        color: #333333 !important;
    }
    
    .success-box {
        background-color: #E8F5E9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .pattern-card {
        background-color: #F1F8E9;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #C8E6C9;
        margin: 1rem 0;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .confidence-high {
        background-color: #C8E6C9;
        color: #1B5E20;
    }
    
    .confidence-medium {
        background-color: #FFF3E0;
        color: #E65100;
    }
    
    .language-selector {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #388E3C;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .upload-section {
        background-color: #E8F5E9;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Database (copied from your original code)
BATIK_DATABASE = {
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
    }
}

SUPPORTED_LANGUAGES = {
    'en': 'English 🇬🇧',
    'ms': 'Malay 🇲🇾',
    'zh-cn': 'Chinese 🇨🇳'
}

class BatikStoryTeller:
    def __init__(self, model_path="runs/classify/batik_75epochsv2/weights/best.pt"):
        self.model = None
        self.class_names = {}
        self.current_language = 'en'
        
        # Try to load model
        try:
            if os.path.exists(model_path):
                self.model = YOLO(model_path)
                self.class_names = self.model.names if hasattr(self.model, 'names') else {}
                st.success(f"✅ Model loaded successfully")
            else:
                st.warning(f"⚠️ Model file not found at: {model_path}")
                st.info("Running in demo mode with sample stories.")
        except Exception as e:
            st.warning(f"⚠️ Could not load model: {e}")
            st.info("Running in demo mode with sample stories.")
    
    def classify_image(self, image_file):
        """Classify batik pattern in uploaded image"""
        try:
            if self.model is None:
                # Demo mode - simulate classification based on filename
                filename = image_file.name.lower()
                if 'bunga' in filename or 'raya' in filename or 'flower' in filename:
                    return {
                        'primary_class': 'corak batik bunga raya',
                        'confidence': 0.95,
                        'class_id': 0,
                        'image_array': Image.open(image_file)
                    }
                elif 'geometri' in filename or 'geometric' in filename:
                    return {
                        'primary_class': 'corak batik geometri',
                        'confidence': 0.92,
                        'class_id': 1,
                        'image_array': Image.open(image_file)
                    }
                else:
                    # Random selection for demo
                    import random
                    pattern = random.choice(['corak batik bunga raya', 'corak batik geometri'])
                    return {
                        'primary_class': pattern,
                        'confidence': 0.88,
                        'class_id': 0 if 'bunga' in pattern else 1,
                        'image_array': Image.open(image_file)
                    }
            
            # Real classification with YOLO
            image = Image.open(image_file)
            image_array = np.array(image)
            
            # Run prediction
            results = self.model.predict(image_array, verbose=False)
            
            if results:
                result = results[0]
                if hasattr(result, 'probs'):
                    probs = result.probs
                    top1_idx = probs.top1
                    confidence = probs.top1conf.item()
                    
                    if top1_idx in self.class_names:
                        class_name = self.class_names[top1_idx]
                    else:
                        class_name = f"Class_{top1_idx}"
                    
                    return {
                        'primary_class': class_name,
                        'confidence': confidence,
                        'class_id': top1_idx,
                        'image_array': image_array
                    }
            
            return None
            
        except Exception as e:
            st.error(f"Error classifying image: {e}")
            return None
    
    def get_story(self, batik_class):
        """Get storytelling for detected batik pattern"""
        batik_class_lower = batik_class.lower().strip()
        
        # Direct match
        if batik_class_lower in BATIK_DATABASE:
            if self.current_language in BATIK_DATABASE[batik_class_lower]:
                return BATIK_DATABASE[batik_class_lower][self.current_language]
        
        # Partial matches
        if 'bunga' in batik_class_lower or 'raya' in batik_class_lower:
            if "corak batik bunga raya" in BATIK_DATABASE:
                if self.current_language in BATIK_DATABASE["corak batik bunga raya"]:
                    return BATIK_DATABASE["corak batik bunga raya"][self.current_language]
        
        if 'geometri' in batik_class_lower:
            if "corak batik geometri" in BATIK_DATABASE:
                if self.current_language in BATIK_DATABASE["corak batik geometri"]:
                    return BATIK_DATABASE["corak batik geometri"][self.current_language]
        
        # Default story
        default_stories = {
            'en': {
                'name': f"{batik_class}",
                'story': f"This appears to be a {batik_class} pattern. Batik is a traditional wax-resist dyeing technique. Each pattern has unique cultural significance in Malaysian heritage.",
                'meaning': "Cultural Heritage, Tradition, Artistry",
                'origin': "Malaysia",
                'cultural_significance': "Part of UNESCO Intangible Cultural Heritage"
            },
            'ms': {
                'name': f"{batik_class}",
                'story': f"Ini adalah corak {batik_class}. Batik adalah teknik pewarnaan tradisional dengan lilin tahan warna. Setiap corak mempunyai makna budaya yang unik dalam warisan Malaysia.",
                'meaning': "Warisan Budaya, Tradisi, Seni",
                'origin': "Malaysia",
                'cultural_significance': "Sebahagian daripada Warisan Budaya Tak Ketara UNESCO"
            }
        }
        
        if self.current_language in default_stories:
            return default_stories[self.current_language]
        
        # Fallback to English
        return default_stories['en']
    
    def generate_audio(self, story_data):
        """Generate audio for the story"""
        try:
            audio_text = f"{story_data['name']}. {story_data['story']}"
            tts = gTTS(text=audio_text, lang=self.current_language)
            
            # Save to bytes
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            return audio_bytes
        except Exception as e:
            st.error(f"Error generating audio: {e}")
            return None

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🌸 Malaysian Batik Storyteller</h1>', unsafe_allow_html=True)
    st.markdown('<p class="info-text" style="text-align: center;">Discover the rich cultural heritage of Malaysian Batik patterns through AI-powered recognition and storytelling</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="section-header">⚙️ Settings</h2>', unsafe_allow_html=True)
        
        # Language Selection
        st.markdown('<div class="language-selector">', unsafe_allow_html=True)
        selected_lang = st.selectbox(
            "🌐 Select Language",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: SUPPORTED_LANGUAGES[x],
            index=0
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Information
        st.markdown('<h2 class="section-header">ℹ️ About</h2>', unsafe_allow_html=True)
        st.markdown('<p class="info-text">This AI-powered application detects and explains two traditional Malaysian batik patterns:</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="text-align: center; padding: 0.5rem; background-color: #E8F5E9; border-radius: 8px;">🌸<br><b>Bunga Raya</b><br>National Flower</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div style="text-align: center; padding: 0.5rem; background-color: #E8F5E9; border-radius: 8px;">🔶<br><b>Geometric</b><br>Islamic Art</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="info-text" style="font-size: 0.9rem; color: #666;">Powered by YOLO AI model • UNESCO Cultural Heritage • Made with ❤️ for Malaysian Culture</p>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📤 Upload Batik Image</h2>', unsafe_allow_html=True)
        
        # Upload section
        uploaded_file = st.file_uploader(
            "Choose an image of batik fabric",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            help="Upload an image containing Bunga Raya or Geometric patterns"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Analyze button
            if st.button("🔍 Analyze Pattern", type="primary", use_container_width=True):
                with st.spinner("Analyzing pattern..."):
                    # Initialize storyteller
                    storyteller = BatikStoryTeller()
                    storyteller.current_language = selected_lang
                    
                    # Classify image
                    result = storyteller.classify_image(uploaded_file)
                    
                    if result:
                        # Get story
                        story_data = storyteller.get_story(result['primary_class'])
                        
                        # Display results in col2
                        with col2:
                            st.markdown('<h2 class="sub-header">📖 Batik Story</h2>', unsafe_allow_html=True)
                            
                            # Pattern card
                            st.markdown('<div class="pattern-card">', unsafe_allow_html=True)
                            
                            # Pattern name and confidence
                            st.markdown(f'<h3 style="color: #2E7D32; margin-bottom: 0.5rem;">{story_data["name"]}</h3>', unsafe_allow_html=True)
                            
                            confidence_percent = result['confidence'] * 100
                            confidence_color = "confidence-high" if confidence_percent > 80 else "confidence-medium"
                            st.markdown(f'<span class="confidence-badge {confidence_color}">Confidence: {confidence_percent:.1f}%</span>', unsafe_allow_html=True)
                            
                            # Pattern details
                            st.markdown('<h4 class="section-header">📍 Origin</h4>', unsafe_allow_html=True)
                            st.markdown(f'<p class="info-text">{story_data["origin"]}</p>', unsafe_allow_html=True)
                            
                            st.markdown('<h4 class="section-header">💫 Meaning</h4>', unsafe_allow_html=True)
                            st.markdown(f'<p class="info-text">{story_data["meaning"]}</p>', unsafe_allow_html=True)
                            
                            st.markdown('<h4 class="section-header">🏛️ Cultural Significance</h4>', unsafe_allow_html=True)
                            st.markdown(f'<p class="info-text">{story_data["cultural_significance"]}</p>', unsafe_allow_html=True)
                            
                            st.markdown('<h4 class="section-header">📚 Story</h4>', unsafe_allow_html=True)
                            st.markdown(f'<p class="info-text">{story_data["story"]}</p>', unsafe_allow_html=True)
                            
                            # Special sections for BUNGA RAYA
                            if 'bunga' in result['primary_class'].lower() or 'raya' in result['primary_class'].lower():
                                if 'home_context' in story_data:
                                    st.markdown('<h4 class="section-header">🏡 In Malaysian Homes</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["home_context"]}</p>', unsafe_allow_html=True)
                                
                                if 'artistic_expression' in story_data:
                                    st.markdown('<h4 class="section-header">🎨 Artistic Expression</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["artistic_expression"]}</p>', unsafe_allow_html=True)
                                
                                if 'essence' in story_data:
                                    st.markdown('<h4 class="section-header">💎 The Essence</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["essence"]}</p>', unsafe_allow_html=True)
                            
                            # Special sections for GEOMETRIC
                            elif 'geometri' in result['primary_class'].lower():
                                if 'islamic_influence' in story_data:
                                    st.markdown('<h4 class="section-header">🕌 Islamic Influence</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["islamic_influence"]}</p>', unsafe_allow_html=True)
                                
                                if 'motifs_stories' in story_data:
                                    st.markdown('<h4 class="section-header">🔶 Common Motifs & Stories</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text" style="white-space: pre-line;">{story_data["motifs_stories"]}</p>', unsafe_allow_html=True)
                                
                                if 'regional_heritage' in story_data:
                                    st.markdown('<h4 class="section-header">🏝️ Regional Heritage</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["regional_heritage"]}</p>', unsafe_allow_html=True)
                                
                                if 'artistic_expression' in story_data:
                                    st.markdown('<h4 class="section-header">🎨 Artistic Expression</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["artistic_expression"]}</p>', unsafe_allow_html=True)
                                
                                if 'essence' in story_data:
                                    st.markdown('<h4 class="section-header">💎 The Essence</h4>', unsafe_allow_html=True)
                                    st.markdown(f'<p class="info-text">{story_data["essence"]}</p>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Audio section
                            st.markdown('<h4 class="section-header">🔊 Listen to the Story</h4>', unsafe_allow_html=True)
                            if st.button("🎵 Generate Audio Story", use_container_width=True):
                                with st.spinner("Generating audio..."):
                                    audio_bytes = storyteller.generate_audio(story_data)
                                    if audio_bytes:
                                        st.audio(audio_bytes, format='audio/mp3')
                                        st.success("Audio generated successfully!")
                                    else:
                                        st.error("Could not generate audio")
                    
                    else:
                        st.error("Could not analyze the image. Please try another image.")
        
        else:
            # Show sample images when no file is uploaded
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.markdown('<p class="info-text">Upload a batik image or try with sample images:</p>', unsafe_allow_html=True)
            
            col_sample1, col_sample2 = st.columns(2)
            with col_sample1:
                st.markdown("**Sample 1:** Bunga Raya Pattern")
                st.image("https://via.placeholder.com/150x150/C8E6C9/1B5E20?text=Bunga+Raya", use_column_width=True)
            with col_sample2:
                st.markdown("**Sample 2:** Geometric Pattern")
                st.image("https://via.placeholder.com/150x150/E8F5E9/2E7D32?text=Geometric", use_column_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if uploaded_file is None:
            st.markdown('<h2 class="sub-header">🎯 How to Use</h2>', unsafe_allow_html=True)
            st.markdown("""
            <div class="success-box">
            <ol style="font-size: 1.1rem; line-height: 2;">
                <li><b>Upload an image</b> of Malaysian batik fabric</li>
                <li><b>Click "Analyze Pattern"</b> to detect the design</li>
                <li><b>Read the cultural story</b> in your chosen language</li>
                <li><b>Listen to audio</b> explanation (optional)</li>
                <li><b>Change language</b> using the sidebar</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<h2 class="sub-header">🌺 About Malaysian Batik</h2>', unsafe_allow_html=True)
            st.markdown("""
            <div class="pattern-card">
            <p class="info-text">
            <b>Malaysian Batik</b> is a traditional textile art recognized by UNESCO as an Intangible Cultural Heritage. 
            It uses wax-resist dyeing techniques to create intricate patterns that tell stories of Malaysian culture, 
            nature, and Islamic artistic traditions.
            </p>
            <p class="info-text">
            <b>Key Patterns:</b><br>
            • <b>Bunga Raya (Hibiscus)</b>: Malaysia's national flower symbolizing unity and love<br>
            • <b>Geometric Patterns</b>: Islamic-inspired designs representing order and harmony
            </p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
