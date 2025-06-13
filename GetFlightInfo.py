import requests
import os

NEOFLIGHT_API_URL = os.getenv("NEOFLIGHT_API_URL")

def fetch_flight_inventory(query):
    try:
        print("query given to api: ",query)
        headers = {"Content-Type": "application/json"}
        response = requests.post(NEOFLIGHT_API_URL, json=query, headers=headers, timeout=10)
        response.raise_for_status()
        resp = response.json()

        if(resp["status"] == "COMPLETED"):
            return  resp["fop"][:5]
        else:
            print("No flight options found", resp)
            return []
        
    except Exception as e:
        print(f"⚠️ NeoFlight API error: {e}")
        return {"error": "Could not retrieve flight options."}

    