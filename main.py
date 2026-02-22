import requests
import os
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Railway will pull this from the Variables tab
GEOCODIO_API_KEY = os.getenv("GEOCODIO_API_KEY")

@app.get("/check_zip_coverage")
async def check_zip(zip_code: str):
    zip_code = zip_code.strip()
    
    if not GEOCODIO_API_KEY:
        return {"status": "error", "message": "Server configuration error."}

    # Geocodio API Call
    url = f"https://api.geocod.io/v1.9/geocode?q={zip_code}&api_key={GEOCODIO_API_KEY}"
    
    try:
        response = requests.get(url).json()
    except Exception:
        return {"status": "error", "message": "I'm having trouble checking that right now."}

    # API Level Errors
    if "error" in response:
        return {"status": "invalid", "message": "Zip code is invalid"}
        
    results = response.get("results", [])
    if results:
        address_components = results[0].get("address_components", {})
        city = address_components.get("city", "")
        formatted_address = results[0].get("formatted_address", "")
        
        # Logic to determine if location is in NYC
        is_nyc = "New York" in city or "New York" in formatted_address
        
        if is_nyc:
            return {
                "eligible": True,
                "status": "success",
                "message": f"Yes, zip code {zip_code} is within our service area."
            }
        else:
            return {
                "eligible": False,
                "status": "outside_area",
                "message": f"I'm sorry, zip code {zip_code} is outside of our service area."
            }
    
    # Final fallback if no results are returned
    return {"status": "not_found", "message": "Zip code is invalid"}
