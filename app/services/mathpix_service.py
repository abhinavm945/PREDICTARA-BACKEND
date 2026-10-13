import requests
import json
from typing import Dict, Any, Optional
from app.core.config import settings

class MathpixService:
    def __init__(self):
        self.app_id = settings.MATHPIX_APP_ID
        self.app_key = settings.MATHPIX_APP_KEY
        self.endpoint = "https://api.mathpix.com/v3/text"

    def process_image(self, base64_image: str) -> Dict[str, Any]:
        """
        Sends handwritten rough work to Mathpix API to extract mathematical expressions,
        LaTeX steps, and confidence scores. Falls back gracefully if credentials are not configured.
        """
        if not self.app_id or not self.app_key:
            # Fallback mock OCR parsing simulating real handwritten rough work
            return {
                "status": "mock_success",
                "latex": r"\frac{1}{4} + \frac{2}{3} = \frac{3}{7}",
                "text": "Rough work handwritten step: 1/4 + 2/3 = (1+2)/(4+3) = 3/7",
                "confidence": 0.94,
                "detected_error": "Direct addition across numerators and denominators without finding LCD",
                "is_mock": True
            }

        headers = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "Content-type": "application/json"
        }

        # Mathpix payload
        payload = {
            "src": f"data:image/jpeg;base64,{base64_image}" if not base64_image.startswith("data:") else base64_image,
            "formats": ["text", "latex_styled"],
            "data_options": {
                "include_asciimath": True,
                "include_latex": True
            }
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "latex": data.get("latex_styled", ""),
                    "text": data.get("text", ""),
                    "confidence": data.get("confidence", 0.9),
                    "is_mock": False
                }
            else:
                return {
                    "status": "error",
                    "error": response.text,
                    "is_mock": True,
                    "latex": r"\text{Mathpix API error: fallback OCR applied}"
                }
        except Exception as e:
            return {
                "status": "exception",
                "error": str(e),
                "is_mock": True,
                "latex": r"\text{Connection error, simulated step extracted}"
            }

mathpix_service = MathpixService()
