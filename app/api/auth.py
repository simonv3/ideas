import hmac
import hashlib

secrets = {
        "test signature": {"secret":"MqaVh3nOiB9V4SmqEFIe366VJypec57s", "key": "dWfpeYdsAi-RPAcA"},
        "sencha": {"secret":"MqaVh3nOiR3V4SmqEFIe366VJypec57s", "key":"aWfpeYdOzO-ihfaA"},
        #client # /users/1/ideas/ = 94d902d872e54d9b6d9c33fd9c9f25b2f3bdb7b4
        #client # /REGISTER/simon/simon/ = 66c63264209c39b0fb51010540d379cf48cab2a4
        #client # /login/simon/simon = 9dd9af0c34f79d0a189f8825af8dc954d607400f
        #client # /idea/1/An Idea/ = 80e48a103cd6c84d9fb574c9020dbbcb67ec2b00
        #client # /idea/post/ = 1e93e8925d38fcca0ff47626b4738a5573bb1abb
        "wired in": {"secret":"T4OkQoi4MtETNk4E5XZRegwP6cxENhQo", "key": "GmZLYRiIqY-OZOaw"},
        #client # /users/<id>/ideas/ = 07f12a1cf78314995b357e2e149bc7e6c3809945
        }

def key_check(apikey, apisignature, query):
    try:
        secret = get_secret(apikey)
    except KeyError:
        return False
    try:
        server_sig = hmac.new(secret, query, hashlib.sha1).hexdigest()

    except TypeError:
        return False
    if apisignature == server_sig:
        return True
    else:
        return False

def get_secret(api_key):
    global secrets
    for pair in secrets.values():
        if pair['key'] == api_key:
            return pair['secret']
        
    return None


