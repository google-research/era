from google import genai
import time
import random
import re
from typing import Protocol

class LLM(Protocol):
    def draw_sample(self, prompt: str) -> str:
        ... 

class GeminiLLM:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-image"):
        self.client = genai.Client(api_key=api_key, vertexai=False)
        self.model_name = model_name

    def draw_sample(self, prompt: str) -> str:
        full_prompt = f"""
You are an expert Data Scientist and Python programmer.
Your task is to write Python code to solve a machine learning problem.
Return ONLY the python code.

--- BEGIN PROMPT ---
{prompt}
--- END PROMPT ---
"""
        max_retries = 5
        base_delay = 5
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt
                )
                content = response.text
                
                # Clean up markdown code blocks if present
                content = re.sub(r'^```python\n', '', content, flags=re.MULTILINE)
                content = re.sub(r'^```\n', '', content, flags=re.MULTILINE)
                content = re.sub(r'\n```$', '', content, flags=re.MULTILINE)
                
                return content
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"  [!] Rate limited (429). Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    print(f"Gemini API Error: {e}")
                    raise e