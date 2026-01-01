import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def calculate_care_score(enriched_tests: list):
    """
    Uses Gemini to evaluate test deviations and calculate CareScore (0–100).
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

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip().replace("```json", "").replace("```", "")

    return json.loads(content)
