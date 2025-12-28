import base64
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def extract_data_from_image(image_bytes):
    """
    Sends image to Gemini to extract test names and values[cite: 83].
    """
    llm_vision = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """
    Analyze this medical report image and extract the test names and values.
    RULES:
    1. Return ONLY valid JSON.
    2. Structure: {"test_name": "value", "test_name_2": "value"}
    3. Normalize test names to snake_case.
    4. Ignore reference ranges/units.
    """

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
        ]
    )

    try:
        response = llm_vision.invoke([message])
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Vision Error: {e}")
        return None