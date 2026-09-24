import os
import time

from dotenv import load_dotenv
from google import genai

from backend.schemas import DocumentRequest


load_dotenv()


class GeminiService:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

        self.configured = bool(self.api_key)

        self.client = None

        if self.configured:
            self.client = genai.Client(
                api_key=self.api_key
            )

    def generate_document(
        self,
        request: DocumentRequest,
    ) -> str:

        if not self.configured:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        prompt = f"""
Create a professional legal document.

Document type:
{request.document_type}

Parties:
{request.parties}

Terms:
{request.terms}

Effective date:
{request.effective_date}

Jurisdiction:
{request.jurisdiction}

Additional instructions:
{request.additional_instructions}

Write the document clearly and professionally.
Do not invent important facts that were not provided.
"""

        try:

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            content = getattr(
                response,
                "text",
                None,
            )

            if not content:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return content.strip()

        except Exception as error:

            raise RuntimeError(
                f"Gemini generation failed: {error}"
            ) from error


gemini_service = GeminiService()