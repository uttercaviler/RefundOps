from google import genai
from google.genai import types
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY not found in environment variables!")
    import sys
    sys.exit(1)

client = genai.Client(api_key=GOOGLE_API_KEY)

def get_flight_data(email_text):
    print("BRAIN: Reading email...", flush=True)
    
    # Prompt specifically asks for the Airline Name now
    prompt = f"""
    You are a data extraction agent.
    Extract the following details from this email. Return ONLY a single JSON object (not an array).
    
    Required format (must be an object, not an array):
    {{
        "pnr": "ABC123",
        "airline": "Air India",
        "customer_name": "John Doe"
    }}
    
    Fields to extract:
    - pnr (string) -> The booking reference (usually 6 chars)
    - airline (string) -> Example: "Indigo", "Air India", "Vistara"
    - customer_name (string) -> The full name of the passenger/customer
    
    Email Text:
    "{email_text}"
    
    Return ONLY the JSON object, nothing else.
    """
    
    # SIMPLIFIED: Using the standard efficient model directly.
    # No complex loops, no long waits.
    model_name = "gemini-2.5-flash"
    
    print(f"BRAIN: Using model {model_name}...", flush=True)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        result = json.loads(response.text)
        
        # If result is a list, take the first item
        if isinstance(result, list):
            result = result[0] if len(result) > 0 else None
            
        return result

    except Exception as e:
        # One single quick retry if quota is hit, just in case
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
             print("Brain: Quota hit. Retrying once in 2s...", flush=True)
             time.sleep(2)
             try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return json.loads(response.text)
             except Exception as retry_e:
                 print(f"Brain Error (Retry failed): {retry_e}", flush=True)
                 return None
        
        print(f"Brain Error: {e}", flush=True)
        return None