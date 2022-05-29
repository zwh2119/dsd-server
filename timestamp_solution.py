import hashlib
import hmac
from hashlib import sha1
import time
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
import os


def get_timestamp():
    return int(time.time())


def get_secret():
    if not os.path.isfile('secret.key'):
        key = SigningKey.generate()
        with open('secret.key', 'wb') as f:
            f.write(key.encode())
        with open('secret.pub', 'wb') as f:
            f.write(key.verify_key.encode())
        print("has no secret key")
    with open('secret.key', 'rb') as f:

        return SigningKey(f.read())


def hmac_sha1(key, code):
    hmac_code = hmac.new(key.encode(), code.encode(), sha1)
    return hmac_code.hexdigest()


def create_signed_timestamp(ts_time=0):
    ts = str(ts_time if ts_time != 0 else get_timestamp())
    # print(ts)
    secret = get_secret()
    # print(secret.encode())
    sig = hmac.new(secret.encode(), ts.encode(), hashlib.sha1).hexdigest()
    return ts + ':' + sig


def check_signed_timestamp(ts):
    [timestamp, hs_give] = ts.split(':')

    time_now = get_timestamp()
    if time_now > timestamp + 60 * 60:
        return False

    hs_offer = hmac_sha1(str(timestamp), get_secret())
    if hs_offer != hs_give:
        return False

    return True


def verify(data: str, sig: str, pub: str = None) -> bool:
    if pub:
        verify_key = VerifyKey(pub.encode(), encoder=HexEncoder)
    else:
        verify_key = get_secret().verify_key
    try:
        verify_key.verify(data.encode(), HexEncoder().decode(sig.encode()))
        return True
    except:
        return False


def check_authentication(auth, devid):
    print("uuid:", devid)
    try:
        t, tsig, sig, pubkey, cert = auth.split(':')
        print("cert:", cert)
    except:
        # print(1)
        return False
    ts = t + ':' + tsig
    print(ts)
    if create_signed_timestamp(int(t)) != ts:
        # print(create_signed_timestamp(int(t)))
        # print(ts)
        print(1)
        return False
    if int(t) + 60 * 60 < time.time():
        print(2)
        return False
    if not verify(ts, sig, pubkey):
        print(3)
        return False
    if not verify(pubkey + str(devid), cert):
        print(4)
        return False

    return True


def check_signature(file, sig, devid):
    try:
        sig, pubkey, cert = sig.split(':')
    except:
        print(0)
        return False
    hash = hash_file(file)
    print("cloud hash file:",hash)
    if not verify(hash, sig, pubkey):
        print(1)
        return False
    if not verify(pubkey + str(devid), cert):
        print(2)
        return False
    return True


def hash_file(file: str) -> str:
    h = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            chunk = f.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_signature(file):
    return sign(hash_file(file))


def sign(data: str) -> str:
    return get_secret().sign(data.encode(), encoder=HexEncoder).signature.decode()


if __name__ == '__main__':
    pass
    # x = create_signed_timestamp()
    # x = x.split(':')[0]
    # create_signed_timestamp(x)
    # create_signed_timestamp(x)
    # pubkey = '497aef49f01a5466fc41ef1ddce337669bb0d8394fa79f2d0041aea5dd14b9f8'
    # uuid = 'b6ef61bf-facf-4878-bd6f-d271324fa0e7'
    # cert = '7db469265897c8575cf49ec41792764cfbd36dd120ec3a2b92e9f82c000cf5242071eabe5ffd24cd0b83cb151a8226afc3ce921cfd76b26071c4f2fb41ee1b0e'
    # print(verify(pubkey+uuid, cert))