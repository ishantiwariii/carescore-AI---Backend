import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_core.messages import HumanMessage


def calculate_care_score(enriched_tests: list):
    """
    Uses Gemini to evaluate test deviations and calculate CareScore (0–100).
    Explicitly handles Gemini quota exhaustion.
    """

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
You are a medical analysis engine.

Your task:
1. For each test, compare value with its reference range.
2. Classify it as one of:
   - "low"
   - "normal"
   - "high"
3. Apply scoring rules:
   - normal → 0 penalty
   - low or high → -10 points
4. Start from 100 points.
5. Final score cannot go below 0.

Rules:
- Use ONLY provided reference ranges
- No diagnosis
- No explanations
- Return ONLY valid JSON

Input Tests:
{json.dumps(enriched_tests, indent=2)}

Output JSON format:
{{
  "score": number,
  "deviations": {{
    "test_name": "low | normal | high"
  }}
}}
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])

        content = (
            response.content
            .strip()
            .replace("```json", "")
            .replace("```", "")
        )

        return {
            "success": True,
            "source": "gemini",
            "data": json.loads(content)
        }

    except ChatGoogleGenerativeAIError as e:
        error_msg = str(e)

       
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            return {
                "success": False,
                "error": "QUOTA_EXHAUSTED",
                "message": "Gemini API quota exhausted. Please retry after some time."
            }

        return {
            "success": False,
            "error": "GEMINI_ERROR",
            "message": "Gemini failed to calculate care score."
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "INVALID_AI_RESPONSE",
            "message": "Gemini returned invalid JSON."
        }

    except Exception as e:
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": str(e)
        }
