import base64
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_core.messages import HumanMessage


def extract_data_from_image(image_bytes):
    """
    Extracts structured medical data from a lab report image using Gemini Vision.
    Explicitly handles Gemini quota exhaustion and invalid AI responses.
    """

    llm_vision = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
You are a medical data extraction engine.

TASK:
Extract structured data from the provided medical report image.

STRICT RULES:
1. Return ONLY valid JSON. No markdown, no explanation.
2. If a field is missing or unclear, use null.
3. DO NOT guess or infer missing data.
4. DO NOT provide medical interpretation or advice.
5. DO NOT rename tests beyond simple normalization.
6. Numeric values must be numbers, not strings.

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
- Extract ALL tests visible in the report.
- Normalize test_name to snake_case.
- Preserve units exactly as written.
- Reference range should be a string (e.g., "12.0 - 15.5 g/dL").
"""

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}"
                }
            },
        ]
    )

    try:
        response = llm_vision.invoke([message])

        raw_content = response.content.strip()

        # Safety cleanup (Gemini sometimes wraps JSON)
        if raw_content.startswith("```"):
            raw_content = (
                raw_content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        return {
            "success": True,
            "source": "gemini_vision",
            "data": json.loads(raw_content)
        }

    except ChatGoogleGenerativeAIError as e:
        error_msg = str(e)

        # 🔥 Explicit quota / rate-limit handling
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            return {
                "success": False,
                "error": "QUOTA_EXHAUSTED",
                "message": "Gemini Vision quota exhausted. Please retry after some time."
            }

        return {
            "success": False,
            "error": "GEMINI_VISION_ERROR",
            "message": "Gemini Vision failed to extract data."
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "INVALID_AI_RESPONSE",
            "message": "Gemini Vision returned invalid JSON."
        }

    except Exception as e:
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": str(e)
        }
