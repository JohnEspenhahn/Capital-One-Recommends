import requests
import json

merchants_cache = { }
apiKey = '731357383e6050a3ea9a49fb6b02b87f'

def getGeojson(custID):
    geocodes = [ ]
    for accID in getAccounts(custID):
        for purchase in getPurchases(accID):
            merchant = getMerchant(purchase['merchant_id'])
            geocodes.append({
                'latitude': str(merchant['geocode']['lat']),
                'longitude': str(merchant['geocode']['lng'])
            })

    # Clear cache and return
    merchants_cache.clear();
    return { 'items': geocodes }


def getAccounts(custID):
    url = 'http://api.reimaginebanking.com/customers/{}/accounts?key={}'.format(custID,apiKey)
    print url
    response = requests.get(url, headers={'content-type':'application/json'})
    accounts = json.loads(response.text)

    accIDs = [ ]
    for account in accounts:
        accIDs.append(account['_id'])

    return accIDs


def getPurchases(accID):
    url = 'http://api.reimaginebanking.com/accounts/{}/purchases?key={}'.format(accID,apiKey)
    print url
    response = requests.get(url, headers={'content-type':'application/json'})
    return json.loads(response.text)


def getMerchant(merchantID):
    if merchants_cache.has_key(merchantID):
        return merchants_cache[merchantID]
    else:
        url = 'http://api.reimaginebanking.com/merchants/{}?key={}'.format(merchantID,apiKey)
        print url

        response = requests.get(url, headers={'content-type':'application/json'})
        m = json.loads(response.text)
        merchants_cache[merchantID] = m

        return m