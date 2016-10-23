from hashlib import sha1
import hmac
import time

def get_unix_time():
    return str(int(time.time()))

def get_login_signature(username, password, timestamp, secret_key=None):
    msg = "username={username}&password={password}&timestamp={timestamp}".format(username=username, password=password,
                                                                                 timestamp=timestamp)
    if secret_key:
        return hmac.new(secret_key, msg, sha1).digest().encode('hex')
    else:
        return hmac.new(password, msg, sha1).digest().encode('hex')

def get_access_signature(token, timestamp, secret_key):
    msg = "token={token}&timestamp={timestamp}".format(token=token, timestamp=timestamp)
    return hmac.new(secret_key, msg, sha1).digest().encode('hex')
