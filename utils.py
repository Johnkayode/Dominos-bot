import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

def geocode(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    payload = {
            "address": address,
            "key": os.getenv("GOOGLE_API_KEY")
    }

    try:
        r = requests.get(url, params=payload, timeout=10)
    except Exception as e:
        raise e

    resp = json.loads(r.text)

    if resp['results']:

        return {
            "address": resp['results']['formatted_address'],
            "latitude": resp['results']['geometry']['location']['lat'],
            "longitude": resp['results']['geometry']['location']['lng']
        }

    return None
        