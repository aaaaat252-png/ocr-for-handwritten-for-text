"""
Example script demonstrating the OCR system usage.
Shows how to use the inference system for recognizing handwritten text.
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from preprocessing import ImagePreprocessor
from feature_extraction import FeatureExtractor
from inference import OCRSystem
from train import DataLoader


def example_1_recognize_single_image():
    """Example 1: Recognize text from a single image."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Recognize Text from Single Image")
    print("="*70)
    
    # Initialize OCR system
    model_path = 'models/ocr_model_svm.pkl'
    ocr = OCRSystem(model_path, feature_method='pixel')
    
    # Set label mapping (0-9 for digits)
    label_map = {i: str(i) for i in range(10)}
    ocr.set_label_mapping(label_map)
    
    # Create a sample digit image for demonstration
    sample_img_path = 'sample_digit.png'
    create_sample_image(sample_img_path)
    
    # Recognize
    print(f"\nProcessing image: {sample_img_path}")
    result = ocr.recognize_text_from_image(sample_img_path)
    
    print(f"[OK] Recognized text: '{result['text']}'")
    print(f"[OK] Average confidence: {result['confidence']:.2%}")
    print(f"[OK] Number of characters: {result['n_characters']}")
    
    if result.get('characters'):
        print(f"[OK] Per-character details:")
        for char, conf in result['characters']:
            print(f"    - '{char}': {conf:.2%} confidence")


def example_2_batch_processing():
    """Example 2: Batch process multiple images."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Processing Multiple Images")
    print("="*70)
    
    # Initialize OCR system
    model_path = 'models/ocr_model_svm.pkl'
    ocr = OCRSystem(model_path)
    ocr.set_label_mapping({i: str(i) for i in range(10)})
    
    # Create sample images
    sample_paths = []
    for i in range(3):
        path = f'sample_digit_{i}.png'
        create_sample_image(path)
        sample_paths.append(path)
    
    # Batch recognize
    print(f"\nProcessing {len(sample_paths)} images...")
    results = ocr.batch_recognize(sample_paths)
    
    print(f"\n[OK] Batch processing complete!")
    for result in results:
        if 'error' in result:
            print(f"  [{result['path']}] ERROR: {result['error']}")
        else:
            print(f"  [{result['path']}] Text: '{result['text']}' ({result['confidence']:.1%})")
    
    # Cleanup
    for path in sample_paths:
        Path(path).unlink(missing_ok=True)


def example_3_model_comparison():
    """Example 3: Compare different models."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Model Comparison (SVM vs Random Forest)")
    print("="*70)
    
    # Load sample data
    data = DataLoader.prepare_dataset(test_size=0.95, val_size=0)  # Small test set
    X_test = data['X_test'][:10]
    y_test = data['y_test'][:10]
    
    # Initialize OCR systems
    models = ['svm', 'rf']
    model_paths = {
        'svm': 'models/ocr_model_svm.pkl',
        'rf': 'models/ocr_model_rf.pkl'
    }
    
    for model_name in models:
        print(f"\n[OK] Testing {model_name.upper()} model")
        model_path = model_paths[model_name]
        
        # Evaluate
        from model import OCRModelTrainer
        trainer = OCRModelTrainer()
        trainer.load_model(model_path)
        
        predictions, confidences = trainer.predict_with_confidence(X_test)
        accuracy = np.mean(predictions == y_test)
        avg_confidence = np.mean(confidences)
        
        print(f"  - Accuracy: {accuracy:.2%}")
        print(f"  - Avg confidence: {avg_confidence:.2%}")


def example_4_preprocessing_pipeline():
    """Example 4: Show preprocessing pipeline steps."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Image Preprocessing Pipeline")
    print("="*70)
    
    # Create sample image
    sample_path = 'sample_preprocessing.png'
    create_sample_image(sample_path)
    
    preprocessor = ImagePreprocessor()
    
    print(f"\nProcessing image: {sample_path}")
    
    # Step-by-step processing
    image = preprocessor.load_image(sample_path)
    print(f"[OK] Step 1 - Load image: shape={image.shape}")
    
    gray = preprocessor.to_grayscale(image)
    print(f"[OK] Step 2 - Convert to grayscale: shape={gray.shape}")
    
    binary = preprocessor.apply_thresholding(gray, method='adaptive')
    print(f"[OK] Step 3 - Apply thresholding: shape={binary.shape}, unique values={np.unique(binary)}")
    
    denoised = preprocessor.reduce_noise(binary)
    print(f"[OK] Step 4 - Reduce noise: shape={denoised.shape}")
    
    normalized = preprocessor.normalize(denoised)
    print(f"[OK] Step 5 - Normalize & resize: shape={normalized.shape}, range=[{normalized.min():.2f}, {normalized.max():.2f}]")
    
    print(f"\n[OK] Preprocessing complete!")
    print(f"  Original: {image.shape} | Final: {normalized.shape}")
    
    # Cleanup
    Path(sample_path).unlink(missing_ok=True)


def example_5_model_info():
    """Example 5: Inspect trained model information."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Model Information")
    print("="*70)
    
    model_path = 'models/ocr_model_svm.pkl'
    ocr = OCRSystem(model_path)
    
    info = ocr.get_system_info()
    
    print(f"\n[OK] OCR System Information:")
    print(f"  - Model path: {info['model_path']}")
    print(f"  - Feature method: {info['feature_method']}")
    print(f"  - Preprocessor target size: {info['preprocessor_target_size']}")
    print(f"  - Label mapping classes: {info['label_mapping_size']}")
    
    model_info = info['model_info']
    print(f"\n[OK] Trained Model Details:")
    print(f"  - Model type: {model_info['model_type']}")
    print(f"  - Classes: {model_info['classes']}")
    print(f"  - Number of classes: {model_info['n_classes']}")
    print(f"  - Training history: {model_info['training_history']}")


def create_sample_image(filepath):
    """Create a sample digit image for demonstration."""
    # Create a simple image with a digit 5
    image = np.ones((64, 64, 3), dtype=np.uint8) * 255  # White background
    cv2.circle(image, (32, 32), 15, (0, 0, 0), -1)  # Black circle
    cv2.imwrite(filepath, image)


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("OCR SYSTEM - USAGE EXAMPLES")
    print("="*70)
    
    try:
        example_1_recognize_single_image()
        example_2_batch_processing()
        example_3_model_comparison()
        example_4_preprocessing_pipeline()
        example_5_model_info()
        
        print("\n" + "="*70)
        print("SUCCESS: ALL EXAMPLES COMPLETED!")
        print("="*70)
        print("\nFor more information, see README.md")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup sample images
        for path in Path('.').glob('sample_*.png'):
            path.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
