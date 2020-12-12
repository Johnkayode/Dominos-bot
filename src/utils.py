import requests

def getproxies():
    proxies = requests.get(
        "http://pubproxy.com/api/proxy?format=json&type=http&limit=20&https=true&post=true&country=NG").json()
    return [i["ipPort"] for i in proxies["data"]]


def clean_address(address):

    address = address.rstrip().lstrip()
    address = address.replace(',','')
    adress = address.replace(' ','-')

    return address

def compare_address(customer_address, store_address):

    customer_address = customer_address.lower()
    store_address = store_address.lower()

    for unit in customer_address.split('-'):
        if unit in store_address.split('-'):
            return True
    return False
