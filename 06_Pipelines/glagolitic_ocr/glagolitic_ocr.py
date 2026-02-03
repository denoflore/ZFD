#!/usr/bin/env python3
"""
Glagolitic OCR Pipeline

Main pipeline for processing manuscript images and recognizing
Glagolitic characters with mapping to EVA transcription.

Usage:
    python glagolitic_ocr.py <image_path> [--output <dir>]
    python glagolitic_ocr.py --test
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Local imports
from character_reference import (
    GLAGOLITIC_ALPHABET,
    VOYNICH_RELEVANT_CHARS,
    transliterate_to_eva,
    transliterate_to_croatian
)
from image_processor import ManuscriptImageProcessor
from glyph_extractor import GlyphExtractor

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class GlagoliticOCR:
    """
    Main OCR pipeline for Glagolitic manuscripts.

    Combines image preprocessing, glyph extraction, and character
    recognition with EVA mapping for Voynich comparison.
    """

    def __init__(self, config=None):
        """
        Initialize the OCR pipeline.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.processor = ManuscriptImageProcessor(config)
        self.extractor = GlyphExtractor(config)

        # Recognition will use template matching by default
        self.templates = {}
        self.recognition_method = 'template'  # or 'features', 'neural'

    def load_templates(self, template_dir):
        """
        Load reference character templates for template matching.

        Args:
            template_dir: Directory containing template images
                         Named as {unicode_name}.png or {character}.png
        """
        if not CV2_AVAILABLE:
            return

        template_path = Path(template_dir)
        if not template_path.exists():
            print(f"Warning: Template directory not found: {template_dir}")
            return

        for img_path in template_path.glob('*.png'):
            name = img_path.stem
            template = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if template is not None:
                self.templates[name] = template

        print(f"Loaded {len(self.templates)} character templates")

    def classify_glyph(self, glyph_image):
        """
        Classify a single glyph image.

        Args:
            glyph_image: Extracted glyph image (grayscale)

        Returns:
            Tuple of (character, confidence) or (None, 0.0)
        """
        if not self.templates:
            return None, 0.0

        best_match = None
        best_score = 0.0

        # Normalize glyph size
        target_height = 50
        h, w = glyph_image.shape[:2]
        scale = target_height / h
        resized = cv2.resize(
            glyph_image,
            (int(w * scale), target_height)
        )

        for name, template in self.templates.items():
            # Resize template to match
            t_h, t_w = template.shape[:2]
            t_scale = target_height / t_h
            t_resized = cv2.resize(
                template,
                (int(t_w * t_scale), target_height)
            )

            # Ensure same width for comparison
            min_w = min(resized.shape[1], t_resized.shape[1])
            g_crop = resized[:, :min_w]
            t_crop = t_resized[:, :min_w]

            # Template matching
            result = cv2.matchTemplate(
                g_crop, t_crop,
                cv2.TM_CCOEFF_NORMED
            )
            _, score, _, _ = cv2.minMaxLoc(result)

            if score > best_score:
                best_score = score
                best_match = name

        return best_match, best_score

    def process_image(self, image_path, output_dir=None):
        """
        Full OCR pipeline for a manuscript image.

        Args:
            image_path: Path to input image
            output_dir: Optional directory for output files

        Returns:
            Dictionary with OCR results
        """
        if not CV2_AVAILABLE:
            raise ImportError("OpenCV required. Install with: pip install opencv-python numpy")

        start_time = datetime.now()
        image_path = Path(image_path)

        print(f"\nProcessing: {image_path.name}")
        print("-" * 50)

        # Load and preprocess
        print("Loading image...")
        image = self.processor.load(str(image_path))

        print("Preprocessing...")
        preprocessed = self.processor.preprocess(image)

        # Segment lines
        print("Segmenting lines...")
        lines = self.processor.segment_lines(preprocessed)
        print(f"  Found {len(lines)} text lines")

        # Extract glyphs
        print("Extracting glyphs...")
        all_glyphs = []
        line_results = []

        for line_idx, (y1, y2) in enumerate(lines):
            line_image = preprocessed[y1:y2, :]
            glyphs = self.extractor.extract(line_image)

            # Adjust glyph positions to full image coordinates
            for g in glyphs:
                x, y, w, h = g['bbox']
                g['bbox'] = (x, y + y1, w, h)
                g['line'] = line_idx

            all_glyphs.extend(glyphs)

            line_results.append({
                'line': line_idx,
                'y_range': (y1, y2),
                'glyph_count': len(glyphs)
            })

        print(f"  Extracted {len(all_glyphs)} glyphs total")

        # Classify glyphs
        print("Classifying glyphs...")
        classified = []

        for glyph in all_glyphs:
            char, confidence = self.classify_glyph(glyph['image'])

            # Get EVA mapping if available
            eva = None
            croatian = None
            if char and char in GLAGOLITIC_ALPHABET:
                eva = GLAGOLITIC_ALPHABET[char].get('eva')
                croatian = GLAGOLITIC_ALPHABET[char].get('croatian')

            classified.append({
                'index': glyph['index'],
                'line': glyph.get('line', 0),
                'bbox': glyph['bbox'],
                'glagolitic': char,
                'confidence': confidence,
                'eva': eva,
                'croatian': croatian
            })

        # Build results
        results = {
            'source': str(image_path),
            'timestamp': start_time.isoformat(),
            'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'image_size': image.shape[:2],
            'lines': line_results,
            'glyphs': classified,
            'statistics': self.extractor.get_statistics(all_glyphs),
            'recognized_text': self._build_text(classified)
        }

        # Save outputs if directory specified
        if output_dir:
            self._save_outputs(results, preprocessed, all_glyphs, output_dir, image_path.stem)

        print(f"\nProcessing complete in {results['processing_time_ms']:.0f}ms")

        return results

    def _build_text(self, classified_glyphs):
        """Build text strings from classified glyphs."""
        # Group by line
        lines = {}
        for g in classified_glyphs:
            line = g.get('line', 0)
            if line not in lines:
                lines[line] = []
            lines[line].append(g)

        text_lines = []
        for line_idx in sorted(lines.keys()):
            line_glyphs = lines[line_idx]

            glagolitic = ''.join(g['glagolitic'] or '?' for g in line_glyphs)
            eva = ''.join(g['eva'] or '?' for g in line_glyphs)
            croatian = ''.join(g['croatian'] or '?' for g in line_glyphs)

            text_lines.append({
                'line': line_idx,
                'glagolitic': glagolitic,
                'eva': eva,
                'croatian': croatian
            })

        return text_lines

    def _save_outputs(self, results, preprocessed, glyphs, output_dir, prefix):
        """Save output files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save preprocessed image
        cv2.imwrite(
            str(output_path / f"{prefix}_preprocessed.png"),
            preprocessed
        )

        # Save visualization
        vis = self.extractor.visualize_extraction(
            preprocessed, glyphs,
            output_path / f"{prefix}_visualization.png"
        )

        # Save extracted glyphs
        glyph_dir = output_path / f"{prefix}_glyphs"
        self.extractor.save_glyphs(glyphs, glyph_dir, prefix)

        # Save JSON results
        json_results = {
            k: v for k, v in results.items()
            if k != 'glyphs' or not isinstance(v, list) or not any('image' in g for g in v if isinstance(g, dict))
        }
        # Clean up non-serializable data
        if 'glyphs' in json_results:
            json_results['glyphs'] = [
                {k: v for k, v in g.items() if k != 'image'}
                for g in results['glyphs']
            ]

        with open(output_path / f"{prefix}_results.json", 'w') as f:
            json.dump(json_results, f, indent=2, default=str)

        print(f"  Saved outputs to: {output_path}")


def run_test():
    """Run a simple test of the pipeline."""
    print("=" * 60)
    print("GLAGOLITIC OCR PIPELINE - TEST MODE")
    print("=" * 60)

    if not CV2_AVAILABLE:
        print("\nERROR: OpenCV not installed")
        print("Install with: pip install opencv-python numpy")
        return 1

    # Create synthetic test image
    print("\nCreating synthetic test image...")
    img = np.ones((150, 400), dtype=np.uint8) * 255

    # Draw some glyph-like shapes
    cv2.rectangle(img, (20, 30), (50, 80), 0, -1)
    cv2.rectangle(img, (60, 35), (95, 75), 0, -1)
    cv2.rectangle(img, (105, 30), (130, 80), 0, -1)
    cv2.rectangle(img, (145, 32), (175, 78), 0, -1)

    cv2.rectangle(img, (20, 100), (45, 140), 0, -1)
    cv2.rectangle(img, (55, 95), (85, 145), 0, -1)
    cv2.rectangle(img, (95, 100), (125, 140), 0, -1)

    # Save test image
    test_path = Path('output/test_image.png')
    test_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(test_path), img)

    # Run pipeline
    print("\nRunning OCR pipeline...")
    ocr = GlagoliticOCR()
    results = ocr.process_image(test_path, 'output')

    # Print results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"\nImage size: {results['image_size']}")
    print(f"Lines found: {len(results['lines'])}")
    print(f"Glyphs extracted: {results['statistics']['count']}")

    if results['statistics']['count'] > 0:
        print(f"Glyph heights: {results['statistics']['height']['min']}-"
              f"{results['statistics']['height']['max']} px")

    print("\nTest completed successfully!")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Glagolitic OCR Pipeline'
    )
    parser.add_argument(
        'image',
        nargs='?',
        help='Path to manuscript image'
    )
    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output directory (default: output)'
    )
    parser.add_argument(
        '--templates', '-t',
        help='Directory containing character templates'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test mode with synthetic image'
    )

    args = parser.parse_args()

    if args.test:
        return run_test()

    if not args.image:
        parser.print_help()
        print("\nError: No image specified. Use --test for test mode.")
        return 1

    # Run pipeline
    ocr = GlagoliticOCR()

    if args.templates:
        ocr.load_templates(args.templates)

    try:
        results = ocr.process_image(args.image, args.output)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Lines: {len(results['lines'])}")
        print(f"Glyphs: {results['statistics']['count']}")

        if results['recognized_text']:
            print("\nRecognized text:")
            for line in results['recognized_text']:
                print(f"  Line {line['line']}: {line['glagolitic']}")
                if line['eva']:
                    print(f"    EVA: {line['eva']}")

        return 0

    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
