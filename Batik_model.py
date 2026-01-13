@st.cache_resource
def load_yolo_model():
    """Load YOLOv8 model for Streamlit Cloud deployment"""
    try:
        # Your model path - simplified for cloud deployment
        model_path = "batik_75epochsv2/weights/best.pt"
        
        # Alternative paths if the above doesn't work
        alternative_paths = [
            "batik_75epochsv2/weights/best.pt",
            "./batik_75epochsv2/weights/best.pt",
            "runs/classify/batik_75epochsv2/weights/best.pt",
            "./runs/classify/batik_75epochsv2/weights/best.pt",
            "batik_model.pt",
            "./batik_model.pt",
            "models/batik_75epochsv2.pt",
            "./models/batik_75epochsv2.pt"
        ]
        
        loaded_model = None
        loaded_path = None
        
        for path in alternative_paths:
            try:
                if os.path.exists(path):
                    print(f"🔄 Loading model from: {path}")
                    loaded_model = YOLO(path)
                    loaded_path = path
                    print(f"✅ Model loaded successfully from: {path}")
                    break
                else:
                    print(f"⚠️ Model not found at: {path}")
            except Exception as e:
                print(f"❌ Error loading from {path}: {e}")
                continue
        
        if loaded_model is None:
            print("❌ Could not load model from any path")
            print("📁 Current directory contents:")
            import glob
            for file in glob.glob("*"):
                print(f"  - {file}")
            return None, None
        
        return loaded_model, loaded_path
    except Exception as e:
        print(f"❌ Error loading YOLO model: {e}")
        return None, None