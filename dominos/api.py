from . import urls


import json
import requests

class DominosNGClient:

    def __init__(self):
        self.session = requests.session
        pass

    def findAddress(self, streetName, city):

        url = urls.URLS['SearchAddress']

        payload = {
            "countrycode" : "NG",
            "street" : streetName,
            "city" : city,
            "streetLimit" : 5
        }

        try:
            r = requests.get(url, params=payload, timeout=10)
        except Exception as e:
            raise e


        resp = json.loads(r.text)

        return resp['Addresses'] if resp['Addresses'] else None

    def findNearbyStoresFromLocation(self, latitude, longitude):

        url = urls.URLS['GetStores']

        payload = {
           "latitude" : latitude,
           "longitude" : longitude
        }

        headers = {
            "DPZ-Language" : "en",
            "DPZ-Market": "NIGERIA"
        }
        
        try:
            r = requests.get(url, params=payload, headers=headers, timeout=10)
        except Exception as e:
            raise e


        resp = json.loads(r.text)

        return resp["Stores"][:3]
     
    def findNearbyStoresFromAddress(self, ordertype, streetNo, streetName, city, DeliveryInstructions, AddressType, Neighbourhood="N/A", LocationName=None, UnitNumber=None):

        url = urls.URLS['GetStores']

        payload = {
            "regionCode" : "NG",
            "Region" : "NG",
            "type" : ordertype, 
            "DeliveryInstructions" : DeliveryInstructions,
            "Neighbourhood" : Neighbourhood,
            "g" : 1,
            "AddressType" : AddressType,
            "Type" : AddressType,
            "UnitType" : AddressType,
            "street" : f"{streetName} {streetNo}",
            "streetNumber" : streetNo,
            "streetName" : streetName,
            "streetAddress1" : streetName,
            "city" : city,
            "streetLimit" : 5,
            "LocationName" : LocationName,
            "UnitNumber" : UnitNumber,
            "isDefault" : "false"
        }

        headers = {
            "DPZ-Language" : "en",
            "DPZ-Market": "NIGERIA"
        }
        
        try:
            r = requests.get(url, params=payload, headers=headers, timeout=10)
        except Exception as e:
            raise e


        resp = json.loads(r.text)

        return resp["Stores"][:5]

    def storemenu(self, store_id):

        url = urls.URLS['GetStoreMenu'] % store_id
        print(url)

        payload = {
            "lang" : "en",
            "includeAssets" : "true"
        }
        
        try:
            r = requests.get(url, params=payload, timeout=10)
        except Exception as e:
            raise e


        resp = json.loads(r.text)
        return resp















"""


client = DominosNGClient()
print(client.findAddress("Providence Street", 'Lagos'))


print(client.findNearbyStores(
    ordertype="Delivery",
    streetNo=4,
    streetName="Charity Rd",
    city="Lagos",
    DeliveryInstructions="Ring the door bell",
    AddressType="House"
))

"""

