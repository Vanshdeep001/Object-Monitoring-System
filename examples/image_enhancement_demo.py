"""
Image Enhancement Demo for Low-light and Noisy Conditions
"""

import cv2
import numpy as np
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_enhancer import ImageEnhancer, AdaptiveEnhancer

def create_sample_images():
    """Create sample images for demonstration"""
    # Create a low-light image
    low_light = np.random.randint(0, 50, (480, 640, 3), dtype=np.uint8)
    cv2.putText(low_light, "Low Light Image", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Create a noisy image
    noisy = np.random.randint(100, 200, (480, 640, 3), dtype=np.uint8)
    noise = np.random.randint(-30, 30, (480, 640, 3), dtype=np.int16)
    noisy = np.clip(noisy.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    cv2.putText(noisy, "Noisy Image", (220, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return low_light, noisy

def main():
    """Image enhancement demonstration"""
    print("Image Enhancement Demo")
    print("=" * 40)
    
    # Initialize enhancers
    enhancer = ImageEnhancer()
    adaptive_enhancer = AdaptiveEnhancer()
    
    # Create sample images
    print("Creating sample images...")
    low_light_image, noisy_image = create_sample_images()
    
    # Save original images
    cv2.imwrite("output/original_low_light.jpg", low_light_image)
    cv2.imwrite("output/original_noisy.jpg", noisy_image)
    
    # Enhance low-light image
    print("Enhancing low-light image...")
    enhanced_low_light = enhancer.enhance_image(low_light_image, 'low_light')
    cv2.imwrite("output/enhanced_low_light.jpg", enhanced_low_light)
    
    # Enhance noisy image
    print("Enhancing noisy image...")
    enhanced_noisy = enhancer.enhance_image(noisy_image, 'noisy')
    cv2.imwrite("output/enhanced_noisy.jpg", enhanced_noisy)
    
    # Adaptive enhancement
    print("Applying adaptive enhancement...")
    adaptive_low_light = adaptive_enhancer.enhance_adaptive(low_light_image)
    adaptive_noisy = adaptive_enhancer.enhance_adaptive(noisy_image)
    
    cv2.imwrite("output/adaptive_low_light.jpg", adaptive_low_light)
    cv2.imwrite("output/adaptive_noisy.jpg", adaptive_noisy)
    
    print("\nEnhancement completed!")
    print("Original images saved to:")
    print("  - output/original_low_light.jpg")
    print("  - output/original_noisy.jpg")
    print("\nEnhanced images saved to:")
    print("  - output/enhanced_low_light.jpg")
    print("  - output/enhanced_noisy.jpg")
    print("  - output/adaptive_low_light.jpg")
    print("  - output/adaptive_noisy.jpg")

if __name__ == "__main__":
    main()

