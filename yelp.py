import argparse
import json
import pprint
import sys
import urllib
import urllib2
import oauth2

# Yelp data
API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'food'
SEARCH_LIMIT = 2
SEARCH_PATH = '/v2/search/'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = 'NB9Z72ayUw6JWUjbVuZBIw'
CONSUMER_SECRET = 'w0zAkRvnuiFRfTpG6Qaz3XE89cc'
TOKEN = 'Xd__19Muq2_vEYOYt9liLw2tf0Fo919r'
TOKEN_SECRET = 'cBlN_onasaVu8NCNLJZf2Ew6ldc'

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print(u'Querying {0} ...'.format(url))

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(sw_latitude, sw_longitude, ne_latitude, ne_longitude, term=DEFAULT_TERM):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        sw_latitude (float): The sw corner
        sw_longitude (float): The sw corner
        ne_latitude (float): The ne corner
        ne_longitude (float): The ne corner
    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'bounds': str(sw_latitude) + ',' + str(sw_longitude) + '|' + str(ne_latitude) + ',' + str(ne_longitude),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)