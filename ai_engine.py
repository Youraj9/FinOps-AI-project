import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def extract_invoice_data(file_bytes, mime_type):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = """
        Analyze this document. 
        Step 1: Determine if this is actually a financial receipt or invoice.
        Step 2: If it IS NOT a receipt (e.g., a person's photo, a random document, a plain text file), return: {"Is_Receipt": false}.
        Step 3: If it IS a receipt, return exactly this JSON:
        {
            "Is_Receipt": true,
            "Vendor_Name": "Name",
            "Vendor_Email": "Email",
            "Subtotal": 0.00,
            "Tax": 0.00,
            "Grand_Total": 0.00,
            "Currency_Code": "ISO Code (USD, GBP, CNY, etc.)"
        }
        Return ONLY raw JSON. No markdown.
        """
        file_part = {"mime_type": mime_type, "data": file_bytes}
        response = model.generate_content([prompt, file_part])
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return None
