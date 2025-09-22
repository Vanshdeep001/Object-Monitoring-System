"""
Image Enhancement Module for Low-light and Noisy Conditions
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional
from config import *

logger = logging.getLogger(__name__)


class ImageEnhancer:
    """
    Image enhancement for improving object detection in challenging conditions
    """
    
    def __init__(self):
        self.denoise_strength = 10
        self.clahe_clip_limit = 2.0
        self.clahe_tile_size = (8, 8)
        self.gamma_correction = 1.2
        self.bilateral_d = 9
        self.bilateral_sigma_color = 75
        self.bilateral_sigma_space = 75
        
        # Initialize CLAHE
        self.clahe = cv2.createCLAHE(clipLimit=self.clahe_clip_limit, 
                                   tileGridSize=self.clahe_tile_size)
        
        logger.info("ImageEnhancer initialized")
    
    def enhance_image(self, image: np.ndarray, enhancement_type: str = 'auto') -> np.ndarray:
        """
        Enhance image based on the specified type
        
        Args:
            image: Input image
            enhancement_type: Type of enhancement ('auto', 'low_light', 'noisy', 'both')
            
        Returns:
            Enhanced image
        """
        if enhancement_type == 'auto':
            # Automatically detect enhancement type based on image characteristics
            enhancement_type = self._detect_enhancement_type(image)
        
        if enhancement_type == 'low_light':
            return self._enhance_low_light(image)
        elif enhancement_type == 'noisy':
            return self._enhance_noisy(image)
        elif enhancement_type == 'both':
            return self._enhance_both(image)
        else:
            logger.warning(f"Unknown enhancement type: {enhancement_type}")
            return image
    
    def _detect_enhancement_type(self, image: np.ndarray) -> str:
        """
        Automatically detect if image needs low-light or noise enhancement
        
        Args:
            image: Input image
            
        Returns:
            Enhancement type string
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate image statistics
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        # Detect low-light conditions
        is_low_light = mean_brightness < 80
        
        # Detect noisy conditions (high standard deviation)
        is_noisy = std_brightness > 50
        
        if is_low_light and is_noisy:
            return 'both'
        elif is_low_light:
            return 'low_light'
        elif is_noisy:
            return 'noisy'
        else:
            return 'none'
    
    def _enhance_low_light(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance low-light images
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        enhanced = image.copy()
        
        # Convert to LAB color space
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        l = self.clahe.apply(l)
        
        # Merge channels back
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Apply gamma correction
        enhanced = self._apply_gamma_correction(enhanced, self.gamma_correction)
        
        # Apply bilateral filter to reduce noise while preserving edges
        enhanced = cv2.bilateralFilter(enhanced, self.bilateral_d, 
                                     self.bilateral_sigma_color, 
                                     self.bilateral_sigma_space)
        
        return enhanced
    
    def _enhance_noisy(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance noisy images
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        enhanced = image.copy()
        
        # Apply Non-local Means Denoising
        enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 
                                                 self.denoise_strength, 
                                                 self.denoise_strength, 
                                                 7, 21)
        
        # Apply bilateral filter
        enhanced = cv2.bilateralFilter(enhanced, self.bilateral_d, 
                                     self.bilateral_sigma_color, 
                                     self.bilateral_sigma_space)
        
        # Apply slight sharpening
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
    
    def _enhance_both(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance both low-light and noisy images
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        # First enhance for noise
        enhanced = self._enhance_noisy(image)
        
        # Then enhance for low-light
        enhanced = self._enhance_low_light(enhanced)
        
        return enhanced
    
    def _apply_gamma_correction(self, image: np.ndarray, gamma: float) -> np.ndarray:
        """
        Apply gamma correction to image
        
        Args:
            image: Input image
            gamma: Gamma value
            
        Returns:
            Gamma-corrected image
        """
        # Build lookup table
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        
        # Apply gamma correction
        return cv2.LUT(image, table)
    
    def enhance_video_frame(self, frame: np.ndarray, enhancement_type: str = 'auto') -> np.ndarray:
        """
        Enhance a single video frame
        
        Args:
            frame: Input frame
            enhancement_type: Type of enhancement
            
        Returns:
            Enhanced frame
        """
        return self.enhance_image(frame, enhancement_type)
    
    def enhance_video(self, input_path: str, output_path: str, enhancement_type: str = 'auto') -> bool:
        """
        Enhance entire video file
        
        Args:
            input_path: Path to input video
            output_path: Path to output video
            enhancement_type: Type of enhancement
            
        Returns:
            True if successful
        """
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            logger.error(f"Error opening video file: {input_path}")
            return False
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        logger.info(f"Enhancing video: {input_path}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Enhance frame
            enhanced_frame = self.enhance_image(frame, enhancement_type)
            
            # Write enhanced frame
            writer.write(enhanced_frame)
            
            frame_count += 1
            if frame_count % 100 == 0:
                logger.info(f"Enhanced {frame_count} frames")
        
        # Cleanup
        cap.release()
        writer.release()
        
        logger.info(f"Video enhancement completed. Total frames: {frame_count}")
        return True
    
    def adjust_parameters(self, **kwargs):
        """
        Adjust enhancement parameters
        
        Args:
            **kwargs: Parameter name-value pairs
        """
        for param, value in kwargs.items():
            if hasattr(self, param):
                setattr(self, param, value)
                logger.info(f"Updated {param} to {value}")
            else:
                logger.warning(f"Unknown parameter: {param}")
        
        # Reinitialize CLAHE if clip limit or tile size changed
        if 'clahe_clip_limit' in kwargs or 'clahe_tile_size' in kwargs:
            self.clahe = cv2.createCLAHE(clipLimit=self.clahe_clip_limit, 
                                       tileGridSize=self.clahe_tile_size)


class AdaptiveEnhancer:
    """
    Adaptive enhancement that adjusts parameters based on image content
    """
    
    def __init__(self):
        self.base_enhancer = ImageEnhancer()
        self.adaptation_factor = 0.5
        
    def enhance_adaptive(self, image: np.ndarray) -> np.ndarray:
        """
        Adaptively enhance image based on content analysis
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        # Analyze image characteristics
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate adaptive parameters
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        # Adjust gamma based on brightness
        adaptive_gamma = 1.0 + (100 - mean_brightness) / 100 * 0.5
        
        # Adjust denoise strength based on noise level
        adaptive_denoise = int(5 + std_brightness / 10)
        
        # Adjust CLAHE clip limit based on contrast
        adaptive_clip_limit = 1.0 + std_brightness / 50
        
        # Apply adaptive parameters
        self.base_enhancer.adjust_parameters(
            gamma_correction=adaptive_gamma,
            denoise_strength=adaptive_denoise,
            clahe_clip_limit=adaptive_clip_limit
        )
        
        # Enhance image
        return self.base_enhancer.enhance_image(image, 'auto')


if __name__ == "__main__":
    # Example usage
    enhancer = ImageEnhancer()
    
    # Test with a sample image
    import os
    if os.path.exists("sample_image.jpg"):
        image = cv2.imread("sample_image.jpg")
        enhanced = enhancer.enhance_image(image, 'auto')
        
        # Save enhanced image
        cv2.imwrite("enhanced_image.jpg", enhanced)
        print("Image enhancement completed")
    else:
        print("No sample image found. Please provide a test image.")
