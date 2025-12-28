from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os

def generate_health_explanation(confirmed_data, deviations):
    """
    Generates user-friendly explanation of results[cite: 87].
    """
    llm_text = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    template = """
    You are a medical assistant. Explain these blood test results.
    Data: {data}
    Deviations: {deviations}
    
    Guidelines:
    1. Be professional and clear.
    2. Explain what "abnormal" values mean generally.
    3. Suggest lifestyle improvements.
    4. NO DIAGNOSIS.
    5. Keep it under 150 words.
    """

    prompt = PromptTemplate(input_variables=["data", "deviations"], template=template)
    chain = prompt | llm_text
    
    response = chain.invoke({
        "data": str(confirmed_data),
        "deviations": str(deviations)
    })
    
    return response.content