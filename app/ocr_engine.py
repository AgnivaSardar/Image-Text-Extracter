import os

os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("FLAGS_enable_pir_api", "0")
os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

from paddleocr import PaddleOCR
import cv2
import numpy as np

MAX_IMAGE_SIDE = 1024

# Initialize model only once
ocr = PaddleOCR(
    device='cpu',
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name='PP-OCRv5_mobile_det',
    text_recognition_model_name='en_PP-OCRv5_mobile_rec',
    text_det_limit_side_len=960,
    cpu_threads=10,
)


def _resize_for_speed(img):
    height, width = img.shape[:2]
    longest_side = max(height, width)
    if longest_side <= MAX_IMAGE_SIDE:
        return img

    scale = MAX_IMAGE_SIDE / float(longest_side)
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)


def _collect_text(result):
    tokens = []

    for page in result or []:
        if isinstance(page, dict):
            rec_texts = page.get("rec_texts") or []
            tokens.extend(str(text) for text in rec_texts if text)
            continue

        for word_info in page or []:
            if not isinstance(word_info, (list, tuple)) or len(word_info) < 2:
                continue
            text_info = word_info[1]
            if isinstance(text_info, (list, tuple)) and text_info:
                tokens.append(str(text_info[0]))

    return " ".join(tokens).strip()

def extract_text(image_input):
    # Support both file paths and numpy arrays
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            return "Error: Image not readable"
    else:
        img = image_input

    img = _resize_for_speed(img)

    # Convert BGR to RGB (VERY IMPORTANT)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Run OCR directly (NO GRAYSCALE)
    result = ocr.ocr(img)
    return _collect_text(result)


def _warmup_ocr():
    dummy = np.full((64, 256, 3), 255, dtype=np.uint8)
    ocr.ocr(dummy)


_warmup_ocr()