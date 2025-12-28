import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def configure_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")
    
    genai.configure(api_key=api_key)
    
    # Configure specific model settings [cite: 153]
    generation_config = {
        "temperature": 0.1, # Low temperature for factual data extraction
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }
    
    return genai, generation_config