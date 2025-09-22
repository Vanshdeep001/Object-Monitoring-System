"""
Dependency Installation Script with Error Handling
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package with error handling"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def install_core_packages():
    """Install core packages first"""
    core_packages = [
        "opencv-python",
        "numpy",
        "matplotlib",
        "Pillow",
        "pandas",
        "scipy",
        "scikit-learn"
    ]
    
    print("Installing core packages...")
    success_count = 0
    
    for package in core_packages:
        if install_package(package):
            success_count += 1
    
    print(f"Core packages: {success_count}/{len(core_packages)} installed successfully")
    return success_count == len(core_packages)

def install_ml_packages():
    """Install machine learning packages"""
    ml_packages = [
        "torch",
        "torchvision",
        "ultralytics"
    ]
    
    print("\nInstalling machine learning packages...")
    success_count = 0
    
    for package in ml_packages:
        if install_package(package):
            success_count += 1
    
    print(f"ML packages: {success_count}/{len(ml_packages)} installed successfully")
    return success_count == len(ml_packages)

def install_streamlit():
    """Install Streamlit"""
    print("\nInstalling Streamlit...")
    return install_package("streamlit")

def install_plotly():
    """Install Plotly"""
    print("\nInstalling Plotly...")
    return install_package("plotly")

def install_deepsort():
    """Try to install DeepSORT with fallback options"""
    print("\nInstalling DeepSORT...")
    
    # Try different versions
    deepsort_versions = [
        "deep-sort-realtime",
        "deep-sort-realtime>=1.3.0",
        "deep-sort-realtime>=1.2.0",
        "deep-sort-realtime>=1.1.0"
    ]
    
    for version in deepsort_versions:
        try:
            print(f"Trying {version}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", version])
            print(f"✅ {version} installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {version}")
            continue
    
    print("⚠️  DeepSORT installation failed. The system will use basic centroid tracking instead.")
    return False

def main():
    """Main installation function"""
    print("🚀 Installing Object Detection and Monitoring System Dependencies")
    print("=" * 65)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("⚠️  Warning: Python 3.8+ is recommended for optimal performance")
    
    # Install packages in order
    success_count = 0
    total_steps = 5
    
    # Step 1: Core packages
    if install_core_packages():
        success_count += 1
    
    # Step 2: ML packages
    if install_ml_packages():
        success_count += 1
    
    # Step 3: Streamlit
    if install_streamlit():
        success_count += 1
    
    # Step 4: Plotly
    if install_plotly():
        success_count += 1
    
    # Step 5: DeepSORT (optional)
    if install_deepsort():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 65)
    print("📊 Installation Summary")
    print("=" * 30)
    print(f"Steps completed: {success_count}/{total_steps}")
    
    if success_count >= 4:  # At least core packages, ML packages, Streamlit, and Plotly
        print("🎉 Installation successful! The system is ready to use.")
        print("\n🚀 Quick Start:")
        print("1. Test installation: python test_installation.py")
        print("2. Run Streamlit dashboard: python run_streamlit.py")
        print("3. Try basic detection: python examples/basic_detection.py")
        
        if success_count == 4:
            print("✅ All features available (including DeepSORT tracking)")
        else:
            print("⚠️  DeepSORT tracking not available, using basic centroid tracking")
    else:
        print("❌ Installation incomplete. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Try installing packages individually")
        print("3. Check Python version compatibility")

if __name__ == "__main__":
    main()

