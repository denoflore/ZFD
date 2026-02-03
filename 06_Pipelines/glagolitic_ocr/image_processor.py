"""
Image Preprocessing for Glagolitic OCR

Handles manuscript image loading, preprocessing, and preparation
for character extraction.
"""

import os
from pathlib import Path

# Note: These imports require opencv-python and numpy
# Install with: pip install opencv-python numpy Pillow

try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Install with: pip install opencv-python numpy")


class ManuscriptImageProcessor:
    """
    Preprocessing pipeline for manuscript images.

    Converts manuscript images to binary format suitable for
    character extraction and OCR.
    """

    def __init__(self, config=None):
        """
        Initialize the image processor.

        Args:
            config: Optional configuration dictionary with:
                - threshold_block_size: Block size for adaptive thresholding (default: 11)
                - threshold_c: Constant for adaptive thresholding (default: 2)
                - morph_kernel_size: Kernel size for morphological ops (default: 2)
                - min_line_height: Minimum text line height in pixels (default: 20)
        """
        self.config = config or {}
        self.threshold_block_size = self.config.get('threshold_block_size', 11)
        self.threshold_c = self.config.get('threshold_c', 2)
        self.morph_kernel_size = self.config.get('morph_kernel_size', 2)
        self.min_line_height = self.config.get('min_line_height', 20)

    def load(self, image_path):
        """
        Load an image from path.

        Args:
            image_path: Path to image file (JPEG, PNG, TIFF)

        Returns:
            numpy array (BGR format) or None if failed
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required. Install with: pip install opencv-python")

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = cv2.imread(str(path))
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        return img

    def to_grayscale(self, image):
        """Convert image to grayscale."""
        if len(image.shape) == 2:
            return image  # Already grayscale
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def apply_threshold(self, gray_image):
        """
        Apply adaptive thresholding to create binary image.

        Uses Gaussian adaptive thresholding which works well
        for manuscript images with uneven illumination.
        """
        binary = cv2.adaptiveThreshold(
            gray_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.threshold_block_size,
            self.threshold_c
        )
        return binary

    def remove_noise(self, binary_image):
        """
        Apply morphological operations to remove noise.

        Uses closing operation to fill small gaps, followed by
        opening to remove small noise particles.
        """
        kernel = np.ones(
            (self.morph_kernel_size, self.morph_kernel_size),
            np.uint8
        )

        # Close small gaps
        closed = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        # Remove small noise
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

        return opened

    def deskew(self, image):
        """
        Correct image skew if present.

        Detects dominant line angle and rotates to correct.
        """
        # Find contours
        coords = np.column_stack(np.where(image > 0))

        if len(coords) < 100:
            return image  # Not enough points

        # Get minimum area rectangle
        angle = cv2.minAreaRect(coords)[-1]

        # Adjust angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only deskew if angle is significant
        if abs(angle) < 0.5:
            return image

        # Rotate
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    def preprocess(self, image, deskew_enabled=True):
        """
        Apply full preprocessing pipeline.

        Args:
            image: Input image (BGR or grayscale)
            deskew_enabled: Whether to apply deskew correction

        Returns:
            Preprocessed binary image
        """
        # Convert to grayscale
        gray = self.to_grayscale(image)

        # Apply thresholding
        binary = self.apply_threshold(gray)

        # Remove noise
        cleaned = self.remove_noise(binary)

        # Deskew if enabled
        if deskew_enabled:
            cleaned = self.deskew(cleaned)

        return cleaned

    def segment_lines(self, binary_image):
        """
        Detect and segment text lines.

        Uses horizontal projection profile to find line boundaries.

        Returns:
            List of (y_start, y_end) tuples for each line
        """
        # Calculate horizontal projection
        projection = np.sum(binary_image, axis=1)

        # Normalize
        projection = projection / projection.max() if projection.max() > 0 else projection

        # Find line regions (where projection > threshold)
        threshold = 0.1
        in_line = False
        lines = []
        line_start = 0

        for y, val in enumerate(projection):
            if val > threshold and not in_line:
                line_start = y
                in_line = True
            elif val <= threshold and in_line:
                if y - line_start >= self.min_line_height:
                    lines.append((line_start, y))
                in_line = False

        # Handle case where last line extends to bottom
        if in_line:
            lines.append((line_start, len(projection)))

        return lines

    def extract_line_images(self, image, lines):
        """
        Extract individual line images.

        Args:
            image: Full page image
            lines: List of (y_start, y_end) tuples

        Returns:
            List of line images
        """
        line_images = []
        for y_start, y_end in lines:
            line_img = image[y_start:y_end, :]
            line_images.append(line_img)
        return line_images

    def process_file(self, image_path, output_dir=None):
        """
        Full processing pipeline for a single file.

        Args:
            image_path: Path to input image
            output_dir: Optional directory to save processed images

        Returns:
            Dictionary with processing results
        """
        # Load
        image = self.load(image_path)

        # Preprocess
        preprocessed = self.preprocess(image)

        # Segment lines
        lines = self.segment_lines(preprocessed)

        # Extract line images
        line_images = self.extract_line_images(preprocessed, lines)

        results = {
            'source': str(image_path),
            'original_size': image.shape[:2],
            'num_lines': len(lines),
            'lines': lines,
            'line_images': line_images,
            'preprocessed': preprocessed
        }

        # Save if output directory specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            base_name = Path(image_path).stem

            # Save preprocessed image
            cv2.imwrite(
                str(output_path / f"{base_name}_preprocessed.png"),
                preprocessed
            )

            # Save line images
            for i, line_img in enumerate(line_images):
                cv2.imwrite(
                    str(output_path / f"{base_name}_line_{i:03d}.png"),
                    line_img
                )

        return results


def create_test_image():
    """Create a simple test image for development."""
    if not CV2_AVAILABLE:
        print("OpenCV not available")
        return None

    # Create blank white image
    img = np.ones((200, 400), dtype=np.uint8) * 255

    # Add some text-like shapes
    cv2.rectangle(img, (20, 30), (40, 60), 0, -1)
    cv2.rectangle(img, (50, 30), (70, 60), 0, -1)
    cv2.rectangle(img, (80, 30), (100, 60), 0, -1)

    cv2.rectangle(img, (20, 80), (40, 110), 0, -1)
    cv2.rectangle(img, (50, 80), (70, 110), 0, -1)

    return img


if __name__ == '__main__':
    print("Manuscript Image Processor")
    print("=" * 50)

    if not CV2_AVAILABLE:
        print("\nOpenCV not installed. Install with:")
        print("  pip install opencv-python numpy Pillow")
        exit(1)

    # Test with synthetic image
    print("\nCreating test image...")
    test_img = create_test_image()

    processor = ManuscriptImageProcessor()

    print("Applying preprocessing...")
    preprocessed = processor.preprocess(test_img, deskew_enabled=False)

    print("Segmenting lines...")
    lines = processor.segment_lines(preprocessed)

    print(f"\nFound {len(lines)} text lines:")
    for i, (y1, y2) in enumerate(lines):
        print(f"  Line {i}: y={y1} to y={y2} (height={y2-y1})")

    print("\nProcessor ready for manuscript images.")
