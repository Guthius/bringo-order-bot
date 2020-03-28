import json
import requests
import jwt
import time
import random

BRINGO_EMAIL = ""
BRINGO_PASSWORD = ""

# Checks whether the given JWT token is still valid...
def is_auth_token_expired(token):
    p = jwt.decode(token, verify=False)
    return p['exp'] < int(time.time())

# Authenticate...
r = requests.post('https://apis.bringo.ro/shop-api/v1/ro/customers/login', data={'email': BRINGO_EMAIL, 'password': BRINGO_PASSWORD})
if r.status_code == 200:
    auth_info = r.json()
    total_items = 0

    # Check whether there are items ready to order in the shopping cart.
    r = requests.get('https://apis.bringo.ro/shop-api/v1/en/carts/', headers={'Authorization': 'Bearer %s' % auth_info['token']})
    if r.status_code != 200:
        print('Failed to retrieve the contents of your cart')
        exit()
    else:
        cart_data = r.json()
        total_items = len(cart_data['items'])
        if total_items == 0:
            print('There is nothing to order, your cart is empty')
            exit()

    # Start trying to place th eorder.
    attempts = 0
    print('Attempting to place the order for {} items...'.format(total_items))
    while True:
        attempts = attempts + 1

        # when the token has expired we need to request a new one...
        if is_auth_token_expired(auth_info['token']):
            print('The authorization token has expired, refreshing...')
            r = requests.post('https://apis.bringo.ro/shop-api/v1/ro/customers/login', data={'email': BRINGO_EMAIL, 'password': BRINGO_PASSWORD})
            if r.status_code == 200:
                print('Succesfully refreshed the authorization token')
                auth_info = r.json()
            else:
                print('Failed to refresh authorization token, stopping...')
                break

        # Try to place the order...
        print('Attempting to place order...')
        r = requests.put('https://apis.bringo.ro/shop-api/v1/en/checkouts/complete', headers={'Authorization': 'Bearer %s' % auth_info['token']})
        if r.status_code == 200:
            print('Your order has been placed after %d attempt(s)!' % attempts)

        delay = random.randint(5, 10)
        print('Failed to place order, retrying in %d seconds' % delay)
        time.sleep(delay)

# If we got a 403 then login has failed...
elif r.status_code == 403:
    res = r.json()
    print(res['message'])
    print('Failed to login, stopping...')
