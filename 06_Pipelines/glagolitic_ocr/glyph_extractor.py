"""
Glyph Extraction for Glagolitic OCR

Segments individual characters from preprocessed manuscript images.
"""

from pathlib import Path

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class GlyphExtractor:
    """
    Extracts individual glyphs from manuscript images.

    Uses contour detection to find and segment characters.
    """

    def __init__(self, config=None):
        """
        Initialize the glyph extractor.

        Args:
            config: Optional configuration dictionary with:
                - min_height: Minimum glyph height in pixels (default: 10)
                - max_height: Maximum glyph height in pixels (default: 200)
                - min_width: Minimum glyph width in pixels (default: 5)
                - max_width: Maximum glyph width in pixels (default: 150)
                - min_aspect: Minimum aspect ratio width/height (default: 0.1)
                - max_aspect: Maximum aspect ratio width/height (default: 3.0)
                - padding: Padding around extracted glyphs (default: 2)
        """
        self.config = config or {}
        self.min_height = self.config.get('min_height', 10)
        self.max_height = self.config.get('max_height', 200)
        self.min_width = self.config.get('min_width', 5)
        self.max_width = self.config.get('max_width', 150)
        self.min_aspect = self.config.get('min_aspect', 0.1)
        self.max_aspect = self.config.get('max_aspect', 3.0)
        self.padding = self.config.get('padding', 2)

    def find_contours(self, binary_image):
        """
        Find contours in binary image.

        Args:
            binary_image: Preprocessed binary image (white text on black)

        Returns:
            List of contours
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required")

        contours, hierarchy = cv2.findContours(
            binary_image,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours

    def filter_contours(self, contours):
        """
        Filter contours by size and aspect ratio.

        Removes noise (too small) and large blobs (decorations, stains).

        Args:
            contours: List of contours from findContours

        Returns:
            List of (contour, bounding_box) tuples that pass filter
        """
        valid = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Size filters
            if h < self.min_height or h > self.max_height:
                continue
            if w < self.min_width or w > self.max_width:
                continue

            # Aspect ratio filter
            aspect = w / h
            if aspect < self.min_aspect or aspect > self.max_aspect:
                continue

            valid.append((contour, (x, y, w, h)))

        return valid

    def sort_glyphs(self, glyph_boxes, line_threshold=10):
        """
        Sort glyphs in reading order (left-to-right, top-to-bottom).

        Args:
            glyph_boxes: List of (contour, (x, y, w, h)) tuples
            line_threshold: Y-distance threshold for same-line grouping

        Returns:
            Sorted list
        """
        if not glyph_boxes:
            return []

        # Group by approximate Y position (lines)
        lines = []
        for item in glyph_boxes:
            _, (x, y, w, h) = item
            center_y = y + h // 2

            # Find existing line
            placed = False
            for line in lines:
                if line:
                    _, (_, ly, _, lh) = line[0]
                    line_center = ly + lh // 2
                    if abs(center_y - line_center) < line_threshold:
                        line.append(item)
                        placed = True
                        break

            if not placed:
                lines.append([item])

        # Sort lines by Y position
        lines.sort(key=lambda line: line[0][1][1])

        # Sort glyphs within each line by X position
        for line in lines:
            line.sort(key=lambda item: item[1][0])

        # Flatten
        sorted_glyphs = []
        for line in lines:
            sorted_glyphs.extend(line)

        return sorted_glyphs

    def extract_glyph_image(self, image, bbox):
        """
        Extract a single glyph image from the source.

        Args:
            image: Source image
            bbox: Bounding box (x, y, w, h)

        Returns:
            Cropped glyph image with padding
        """
        x, y, w, h = bbox
        img_h, img_w = image.shape[:2]

        # Apply padding
        x1 = max(0, x - self.padding)
        y1 = max(0, y - self.padding)
        x2 = min(img_w, x + w + self.padding)
        y2 = min(img_h, y + h + self.padding)

        return image[y1:y2, x1:x2]

    def extract(self, binary_image):
        """
        Extract all glyphs from a binary image.

        Args:
            binary_image: Preprocessed binary image

        Returns:
            List of dictionaries with glyph data:
                - image: Cropped glyph image
                - bbox: (x, y, w, h)
                - contour: Original contour
                - index: Position in reading order
        """
        # Find contours
        contours = self.find_contours(binary_image)

        # Filter
        valid = self.filter_contours(contours)

        # Sort in reading order
        sorted_glyphs = self.sort_glyphs(valid)

        # Extract images
        results = []
        for i, (contour, bbox) in enumerate(sorted_glyphs):
            glyph_img = self.extract_glyph_image(binary_image, bbox)
            results.append({
                'image': glyph_img,
                'bbox': bbox,
                'contour': contour,
                'index': i
            })

        return results

    def save_glyphs(self, glyphs, output_dir, prefix='glyph'):
        """
        Save extracted glyphs as individual image files.

        Args:
            glyphs: List from extract()
            output_dir: Directory to save images
            prefix: Filename prefix

        Returns:
            List of saved file paths
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved = []
        for glyph in glyphs:
            filename = f"{prefix}_{glyph['index']:04d}.png"
            filepath = output_path / filename
            cv2.imwrite(str(filepath), glyph['image'])
            saved.append(str(filepath))

        return saved

    def visualize_extraction(self, original_image, glyphs, output_path=None):
        """
        Create visualization of extracted glyphs.

        Draws bounding boxes and indices on the original image.

        Args:
            original_image: Source image (grayscale or color)
            glyphs: List from extract()
            output_path: Optional path to save visualization

        Returns:
            Annotated image
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required")

        # Convert to color if needed
        if len(original_image.shape) == 2:
            vis = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
        else:
            vis = original_image.copy()

        # Draw bounding boxes
        for glyph in glyphs:
            x, y, w, h = glyph['bbox']
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.putText(
                vis,
                str(glyph['index']),
                (x, y - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3,
                (0, 0, 255),
                1
            )

        if output_path:
            cv2.imwrite(str(output_path), vis)

        return vis

    def get_statistics(self, glyphs):
        """
        Calculate statistics about extracted glyphs.

        Args:
            glyphs: List from extract()

        Returns:
            Dictionary with statistics
        """
        if not glyphs:
            return {'count': 0}

        heights = [g['bbox'][3] for g in glyphs]
        widths = [g['bbox'][2] for g in glyphs]
        aspects = [w / h for w, h in zip(widths, heights)]

        return {
            'count': len(glyphs),
            'height': {
                'min': min(heights),
                'max': max(heights),
                'mean': sum(heights) / len(heights)
            },
            'width': {
                'min': min(widths),
                'max': max(widths),
                'mean': sum(widths) / len(widths)
            },
            'aspect_ratio': {
                'min': min(aspects),
                'max': max(aspects),
                'mean': sum(aspects) / len(aspects)
            }
        }


if __name__ == '__main__':
    print("Glyph Extractor")
    print("=" * 50)

    if not CV2_AVAILABLE:
        print("\nOpenCV not installed. Install with:")
        print("  pip install opencv-python numpy")
        exit(1)

    # Create test image with some glyph-like shapes
    print("\nCreating test image...")
    img = np.zeros((100, 300), dtype=np.uint8)

    # Draw some rectangles as fake glyphs
    cv2.rectangle(img, (20, 20), (40, 60), 255, -1)
    cv2.rectangle(img, (50, 25), (75, 55), 255, -1)
    cv2.rectangle(img, (85, 20), (100, 60), 255, -1)
    cv2.rectangle(img, (120, 22), (145, 58), 255, -1)

    extractor = GlyphExtractor()

    print("Extracting glyphs...")
    glyphs = extractor.extract(img)

    print(f"\nExtracted {len(glyphs)} glyphs")

    stats = extractor.get_statistics(glyphs)
    print(f"\nStatistics:")
    print(f"  Count: {stats['count']}")
    print(f"  Height: {stats['height']['min']}-{stats['height']['max']} "
          f"(mean: {stats['height']['mean']:.1f})")
    print(f"  Width: {stats['width']['min']}-{stats['width']['max']} "
          f"(mean: {stats['width']['mean']:.1f})")

    print("\nGlyph extractor ready.")
