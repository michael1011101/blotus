from hashlib import sha1
import hmac
import time

def get_unix_time():
    return str(int(time.time()))

def get_login_signature(username, secret_key, timestamp):
    msg = "username={username}&password={password}&timestamp={timestamp}".format(username=username, password=secret_key,
                                                                                 timestamp=timestamp)
    return hmac.new(secret_key, msg, sha1).digest().encode('hex')

def get_access_signature(token, timestamp, secret_key):
    msg = "token={token}&timestamp={timestamp}".format(token=token, timestamp=timestamp)
    return hmac.new(secret_key, msg, sha1).digest().encode('hex')
