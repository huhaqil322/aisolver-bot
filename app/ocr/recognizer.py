from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image

from app.config.settings import get_settings

settings = get_settings()


class OCRRecognizer:
    def __init__(self) -> None:
        self.tesseract_cmd = settings.TESSERACT_CMD
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    async def recognize(
        self,
        image_path: Path,
        lang: str = "eng+rus",
        psm: int = 6,
    ) -> str:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(
            None, self._recognize_sync, image_path, lang, psm
        )
        return text.strip()

    def _recognize_sync(
        self, image_path: Path, lang: str, psm: int
    ) -> str:
        image = Image.open(image_path)
        config = f"--psm {psm} --oem 3 -c tessedit_char_whitelist=''"
        text = pytesseract.image_to_string(
            image, lang=lang, config=config
        )
        return text

    async def recognize_with_confidence(
        self, image_path: Path, lang: str = "eng+rus", psm: int = 6
    ) -> tuple[str, float]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._recognize_with_data_sync, image_path, lang, psm
        )
        return result

    def _recognize_with_data_sync(
        self, image_path: Path, lang: str, psm: int
    ) -> tuple[str, float]:
        image = Image.open(image_path)
        config = f"--psm {psm} --oem 3"
        data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)

        text_parts = []
        confidences = []
        for i, text in enumerate(data["text"]):
            conf = int(data["conf"][i])
            if text.strip() and conf > 0:
                text_parts.append(text)
                confidences.append(conf)

        text = " ".join(text_parts)
        avg_confidence = (
            sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
        )
        return text, avg_confidence

    async def recognize_formula(
        self, image_path: Path
    ) -> Optional[str]:
        if settings.mathpix_api_key:
            return await self._mathpix_recognition(image_path)
        return await self.recognize(image_path, psm=12)

    async def _mathpix_recognition(self, image_path: Path) -> Optional[str]:
        import aiohttp

        headers = {
            "app_id": settings.MATHPIX_APP_ID or "",
            "app_key": settings.mathpix_api_key or "",
            "Content-type": "application/json",
        }

        import base64

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "src": f"data:image/png;base64,{image_b64}",
            "formats": ["text", "latex_simplified"],
            "data_options": {"include_asciimath": True, "include_latex": True},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.mathpix.com/v3/text",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("latex_simplified") or data.get("text", "")
                return None
