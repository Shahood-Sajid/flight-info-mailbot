import google.generativeai as genai
from google.generativeai import types
import os
import json
import re
from structured_responses import Response

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AFFILIATE_ID = os.getenv("AFFILIATE_ID")
ORG_ID = os.getenv("ORG_ID")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_gemini_response(prompt):
    print("LLM called for general email reply.")  # Logging LLM usage
    try:
        response = model.generate_content(f"Reply to the following email professionally:\n\n{prompt}")
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return "Sorry, I couldn't generate a response at this time."

def extract_flight_query(email_text):
    print("LLM called for extracting flight query.")  # Logging LLM usage
    prompt = """
    Get the details from the emails
    """
    try:
        response = model.generate_content([prompt, email_text],generation_config=types.GenerationConfig(response_mime_type='application/json',response_schema=Response))
        
        response_data = response.text.strip("```json").strip("```").strip()

        data = json.loads(response_data)

        print("json flight details fetched by gemini", data)

        payload = {
            "Segments": [
                {
                    "Origin": data.get("StOrigin"),
                    "Destination": data.get("Destination"),
                    "Date": data.get("Date"),
                    "Class": data.get("Class")
                }
            ],
            "TripType": str(data.get("TripType")),
            "AffiliateId": "2412310726013014383",
            "OrgId": "2212051818221653784",
            "Adult": data.get("Adult"),
            "Child": data.get("Child"),
            "Infant": data.get("Infant")
        }

        print("payload: ",payload)

        return payload

    except Exception as e:
        print(f"⚠️ Gemini flight extraction error: {e}")
        return None
    

def compose_flight_response(original_email, flight_data):

    print("flight results given by api: ", flight_data)
    print("LLM called for composing flight response.")  # Logging LLM usage
    prompt = f"""
    A user sent this email: "{original_email}"

    Based on this, here are flight options from the API:
    {flight_data}

    Write a professional reply summarizing the top 1–5 flight options including airline, price, and departure time.
    If no results found, politely inform the user.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini compose error: {e}")
        return "Sorry, we couldn't find suitable flight options at the moment."