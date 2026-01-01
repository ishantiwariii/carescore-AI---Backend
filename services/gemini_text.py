from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os

from services.reference_resolver import resolve_test_reference

def generate_health_explanation(confirmed_data, deviations):
    """
    Generates user-friendly explanation of results.
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

    response = chain.invoke({
        "data": enriched_tests
    })

    return response.content
