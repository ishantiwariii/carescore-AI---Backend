from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langchain_core.prompts import PromptTemplate
import os

from services.reference_resolver import resolve_test_reference


def generate_health_explanation(confirmed_data, deviations):
    """
    Generates user-friendly explanation of results.
    Explicitly handles Gemini quota exhaustion.
    """

    gender = confirmed_data.get("patient", {}).get("gender", "").lower()

    enriched_tests = []

    for test in confirmed_data.get("tests", []):
        reference = resolve_test_reference(test, gender)

        enriched_tests.append({
            "test_name": test["test_name"],
            "value": test["value"],
            "unit": test["unit"],
            "reference_range": reference,
            "status": deviations.get(test["test_name"])
        })

    llm_text = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    template = """
You are a medical assistant.

Explain the following blood test results in simple, patient-friendly language.

Data:
{data}

Rules:
- Use the provided reference ranges only
- Explain abnormal values generally
- No diagnosis
- No treatment plans
- Keep the explanation under 150 words
"""

    prompt = PromptTemplate(
        input_variables=["data"],
        template=template
    )

    chain = prompt | llm_text

    try:
        response = chain.invoke({
            "data": enriched_tests
        })

        return {
            "success": True,
            "source": "gemini",
            "content": response.content
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
            "message": "Gemini failed to generate explanation."
        }

    except Exception as e:
        return {
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": str(e)
        }
