import base64
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_core.messages import HumanMessage


def _safe_json_parse(text: str):
    """
    Attempts to parse JSON with minimal cleanup.
    If this fails, AI is considered failed.
    """
    text = text.strip()

    if text.startswith("```"):
        text = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.replace("\n", " ").strip().rstrip(",")
        return json.loads(cleaned)


def extract_data_from_image(image_bytes: bytes, mime_type: str):
    """
    Extracts structured medical data from a lab report image using Gemini Vision.

    HARD RULE:
    - If AI fails, return success=False (no manual fallback).
    """

    llm_vision = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        top_p=1.0,
        top_k=1,
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
You are a medical data extraction engine.

TASK:
Extract structured data from the provided medical report image.

RULES:
1. Output valid JSON only (no markdown, no explanation).
2. If a field is unclear, use null.
3. Do NOT guess missing values.
4. Do NOT provide medical interpretation.
5. Normalize test_name to snake_case.
6. Numeric values should be numbers when possible.

OUTPUT FORMAT:
{
  "patient": {
    "name": null,
    "age": null,
    "gender": "unknown"
  },
  "lab": {
    "name": null
  },
  "tests": [
    {
      "test_name": "",
      "value": null,
      "unit": null,
      "reference_range": null
    }
  ]
}

IMPORTANT:
- Extract ALL visible tests.
- Preserve units exactly as written.
- Reference range must be a string.
"""

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_b64}"
                }
            },
        ]
    )

    try:
        response = llm_vision.invoke([message])
        raw_content = response.content.strip()

        
        print("RAW GEMINI OUTPUT:", raw_content)

        parsed = _safe_json_parse(raw_content)

        return {
            "success": True,
            "source": "gemini_vision",
            "data": parsed,
        }

    except ChatGoogleGenerativeAIError as e:
        error_msg = str(e)

        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            return {
                "success": False,
                "error": "QUOTA_EXHAUSTED",
                "message": "Gemini Vision quota exhausted.",
            }

        return {
            "success": False,
            "error": "GEMINI_VISION_ERROR",
            "message": error_msg,
        }

    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "INVALID_AI_RESPONSE",
            "message": f"Invalid JSON from Gemini: {e}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": str(e),
        }
