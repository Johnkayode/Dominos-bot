import os
import json
import requests

from dominos.api import DominosNGClient

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
            "address": resp['results'][0]['formatted_address'],
            "latitude": resp['results'][0]['geometry']['location']['lat'],
            "longitude": resp['results'][0]['geometry']['location']['lng']
        }

    return None



