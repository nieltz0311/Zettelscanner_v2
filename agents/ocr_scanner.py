import sys
import pytesseract
import cv2
import numpy as np
from typing import Dict, Any

class OCRScanner:
    def __init__(self):
        if sys.platform == "win32":
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        else:
            pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Bild vorverarbeiten für bessere OCR-Ergebnisse."""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return thresh

    def process(self, image_path: str) -> Dict[str, Any]:
        """Bild scannen und Text extrahieren."""
        processed_image = self.preprocess_image(image_path)
        text = pytesseract.image_to_string(processed_image, lang="deu+eng")
        return {"raw_text": text.strip()}
