from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from app.config.settings import get_settings
from app.ocr.preprocessor import ImagePreprocessor
from app.ocr.recognizer import OCRRecognizer

settings = get_settings()


class OCRResult:
    def __init__(
        self,
        text: str,
        confidence: float,
        language: str = "eng",
        is_handwritten: bool = False,
        formulas: list[str] | None = None,
        processed_path: Optional[Path] = None,
    ) -> None:
        self.text = text
        self.confidence = confidence
        self.language = language
        self.is_handwritten = is_handwritten
        self.formulas = formulas or []
        self.processed_path = processed_path

    @property
    def is_reliable(self) -> bool:
        return self.confidence > 0.6

    @property
    def needs_review(self) -> bool:
        return self.confidence < 0.4


class OCRPipeline:
    def __init__(self) -> None:
        self.preprocessor = ImagePreprocessor()
        self.recognizer = OCRRecognizer()
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def process(
        self,
        image_data: bytes,
        filename: Optional[str] = None,
        lang: str = "eng+rus",
    ) -> OCRResult:
        ext = Path(filename or "image.png").suffix if filename else ".png"
        temp_filename = f"{uuid.uuid4()}{ext}"
        temp_path = self.upload_dir / temp_filename

        try:
            with open(temp_path, "wb") as f:
                f.write(image_data)

            processed_path = self.upload_dir / f"processed_{temp_filename}"

            processed = await self.preprocessor.preprocess(temp_path)
            import cv2

            cv2.imwrite(str(processed_path), processed)

            text, confidence = await self.recognizer.recognize_with_confidence(
                processed_path, lang=lang
            )

            formula_text = await self.recognizer.recognize_formula(processed_path)

            is_handwritten = confidence < 0.7

            formulas = []
            if formula_text:
                formulas.append(formula_text)

            return OCRResult(
                text=text,
                confidence=confidence,
                language=lang,
                is_handwritten=is_handwritten,
                formulas=formulas,
                processed_path=processed_path,
            )

        except Exception as e:
            raise RuntimeError(f"OCR processing failed: {e}") from e

        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

    async def process_from_path(
        self, image_path: Path, lang: str = "eng+rus"
    ) -> OCRResult:
        with open(image_path, "rb") as f:
            image_data = f.read()
        return await self.process(image_data, image_path.name, lang)
