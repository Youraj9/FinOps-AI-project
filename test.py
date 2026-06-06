import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("API KEY:", os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say hello")
    print("Response:", response.text)
except Exception as e:
    print("ERROR:", e)
