from . import urls


import json
import requests

class DominosNGClient:

    def __init__(self):
        self.session = requests.session
        pass

    def findAddress(self, streetName, city):

        '''
        This methods searches and confirms the user address
        '''


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
        '''
        This method returns a list of nearby stores given the location's latitude and longitude 
        '''

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
     
    def findNearbyStoresFromAddress(self, 
                ordertype, 
                streetNo, 
                streetName, 
                city, 
                DeliveryInstructions, 
                AddressType, 
                Neighbourhood="N/A", 
                LocationName=None, 
                UnitNumber=None
            ):

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
        '''
        This method returns the store menu
        '''

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

    def addToCart(self, store_id, store_city, store_street, latitude, longitude, product_code):


        payload =   {
                        "Order": {
                            "Address": {
                                "Coordinates": {
                                    "Latitude": latitude,
                                    "Longitude": longitude
                                },
                                "StoreID": store_id,
                                "City": store_city, #Labak estate
                                "StreetName": store_street    #Old Abeokuta Road
                            },
                            "Coupons": [],
                            "CustomerID": "",
                            "Email": "",
                            "Extension": "",
                            "FirstName": "",
                            "LastName": "",
                            "LanguageCode": "en",
                            "OrderChannel": "OLO",
                            "OrderID": "",
                            "OrderMethod": "Web",
                            "OrderTaker": None,
                            "Payments": [],
                            "Phone": "",
                            "PhonePrefix": "",
                            "Products": [
                                {
                                    "Code": product_code,
                                    "Qty": 1,
                                    "ID": 1,
                                    "isNew": True,
                                    "Options": {
                                        "D": {
                                            "1/1": "1"
                                        },
                                        "C": {
                                            "1/1": "1"
                                        },
                                        "I": {
                                            "1/1": "1"
                                        },
                                        "M": {
                                            "1/1": "1"
                                        },
                                        "N": {
                                            "1/1": "1"
                                        },
                                        "X": {
                                            "1/1": "1"
                                        }
                                    }
                                }
                            ],
                            "ServiceMethod": "Carryout",
                            "SourceOrganizationURI": "order.dominos.com",
                            "StoreID":  store_id, #51819
                            "Tags": {},
                            "Version": "1.0",
                            "NoCombine": True,
                            "Partners": {},
                            "HotspotsLite": False,
                            "OrderInfoCollection": []
                        }
                    }














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

