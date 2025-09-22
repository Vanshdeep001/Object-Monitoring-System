"""
Test Installation Script
Verifies that all dependencies are properly installed and working
"""

import sys
import importlib
import subprocess

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def test_opencv():
    """Test OpenCV functionality"""
    try:
        import cv2
        import numpy as np
        
        # Test basic OpenCV operations
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.putText(img, "Test", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        print("✅ OpenCV - OK")
        return True
    except Exception as e:
        print(f"❌ OpenCV - FAILED: {e}")
        return False

def test_yolo():
    """Test YOLO model loading"""
    try:
        from ultralytics import YOLO
        
        # Try to load a small model
        model = YOLO('yolov8n.pt')
        
        print("✅ YOLOv8 - OK")
        return True
    except Exception as e:
        print(f"❌ YOLOv8 - FAILED: {e}")
        return False

def test_torch():
    """Test PyTorch installation"""
    try:
        import torch
        import torchvision
        
        # Test basic operations
        x = torch.randn(1, 3, 224, 224)
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        x = x.to(device)
        
        print(f"✅ PyTorch - OK (Device: {device})")
        return True
    except Exception as e:
        print(f"❌ PyTorch - FAILED: {e}")
        return False

def test_streamlit():
    """Test Streamlit installation"""
    try:
        import streamlit as st
        
        print("✅ Streamlit - OK")
        return True
    except Exception as e:
        print(f"❌ Streamlit - FAILED: {e}")
        return False

def test_deepsort():
    """Test DeepSORT installation"""
    try:
        from deep_sort_realtime import DeepSort
        
        # Try to create a tracker
        tracker = DeepSort()
        
        print("✅ DeepSORT - OK")
        return True
    except Exception as e:
        print(f"❌ DeepSORT - FAILED: {e}")
        return False

def test_project_modules():
    """Test project-specific modules"""
    modules = [
        ('config', 'Configuration'),
        ('object_detector', 'Object Detector'),
        ('zone_monitor', 'Zone Monitor'),
        ('object_tracker', 'Object Tracker'),
        ('image_enhancer', 'Image Enhancer'),
        ('logger', 'Logger'),
        ('monitoring_system', 'Monitoring System')
    ]
    
    results = []
    for module, name in modules:
        result = test_import(module, name)
        results.append(result)
    
    return all(results)

def main():
    """Run all tests"""
    print("🧪 Testing Object Detection and Monitoring System Installation")
    print("=" * 60)
    
    # Test core dependencies
    print("\n📦 Testing Core Dependencies:")
    test_results = []
    
    test_results.append(test_opencv())
    test_results.append(test_torch())
    test_results.append(test_yolo())
    test_results.append(test_streamlit())
    test_results.append(test_deepsort())
    
    # Test additional dependencies
    print("\n📚 Testing Additional Dependencies:")
    additional_modules = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('matplotlib', 'Matplotlib'),
        ('PIL', 'Pillow'),
        ('scipy', 'SciPy'),
        ('sklearn', 'Scikit-learn'),
        ('plotly', 'Plotly')
    ]
    
    for module, name in additional_modules:
        result = test_import(module, name)
        test_results.append(result)
    
    # Test project modules
    print("\n🔧 Testing Project Modules:")
    project_results = test_project_modules()
    test_results.append(project_results)
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 Quick Start:")
        print("1. Run: python run_streamlit.py")
        print("2. Or try: python examples/basic_detection.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check Python version (3.8+ required)")
        print("3. Verify all files are in the correct directory")

if __name__ == "__main__":
    main()

