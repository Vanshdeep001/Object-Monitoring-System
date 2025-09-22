"""
Setup script for Object Detection and Monitoring System
"""

import os
import subprocess
import sys

def create_directories():
    """Create necessary directories"""
    directories = ['output', 'logs', 'models', 'examples']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def download_yolo_model():
    """Download YOLOv8 model if not present"""
    model_path = "models/yolov8n.pt"
    
    if os.path.exists(model_path):
        print(f"📁 YOLO model already exists: {model_path}")
        return True
    
    print("⬇️  Downloading YOLOv8 model...")
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        # Save to models directory
        import shutil
        shutil.move('yolov8n.pt', model_path)
        print(f"✅ YOLO model downloaded: {model_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download YOLO model: {e}")
        return False

def create_sample_files():
    """Create sample files for testing"""
    # Create a sample configuration file
    sample_config = """# Sample Configuration
# Modify these settings as needed

# Model settings
MODEL_PATH = "models/yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Zone monitoring
RESTRICTED_ZONE_COLOR = (0, 0, 255)  # Red
ALERT_COOLDOWN = 2.0

# Enhancement settings
DENOISE_STRENGTH = 10
CLAHE_CLIP_LIMIT = 2.0
GAMMA_CORRECTION = 1.2
"""
    
    with open("sample_config.py", "w") as f:
        f.write(sample_config)
    
    print("✅ Created sample configuration file")

def main():
    """Main setup function"""
    print("🚀 Setting up Object Detection and Monitoring System")
    print("=" * 55)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return False
    
    # Download YOLO model
    print("\n⬇️  Downloading YOLO model...")
    if not download_yolo_model():
        print("⚠️  YOLO model download failed, but you can still use the system")
    
    # Create sample files
    print("\n📄 Creating sample files...")
    create_sample_files()
    
    # Run installation test
    print("\n🧪 Running installation test...")
    try:
        subprocess.check_call([sys.executable, "test_installation.py"])
    except subprocess.CalledProcessError:
        print("⚠️  Installation test failed, but setup is complete")
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 Quick Start:")
    print("1. Run the Streamlit dashboard: python run_streamlit.py")
    print("2. Or try basic detection: python examples/basic_detection.py")
    print("3. Test webcam monitoring: python examples/webcam_monitoring.py")
    
    return True

if __name__ == "__main__":
    main()

