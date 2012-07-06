import hmac
import hashlib

secrets = {
        "test signature": {"sig":"MqaVh3nOiB9V4SmqEFIe366VJypec57s", "key": "dWfpeYdsAi-RPAcA"},#client key = 94d902d872e54d9b6d9c33fd9c9f25b2f3bdb7b4
        "wyred": {"sig":"MqaVh3nOiB9V4SmqEFIe366VJypec57s", "key": "dWfpeYdsAi-RPAcA"},#client key = 94d902d872e54d9b6d9c33fd9c9f25b2f3bdb7b4
        
        }

def key_check(apikey, apisignature, query):
    try:
        secret = get_secret(apikey)
    except KeyError:
        return False
    
    server_sig = hmac.new(secret, query, hashlib.sha1).hexdigest()

    if apisignature == server_sig:
        return True
    else:
        return False

def get_secret(api_key):
    global secrets

    for pair in secrets.values():
        if pair['key'] == api_key:
            return pair['sig']
        
    return None


