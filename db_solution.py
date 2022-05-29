import json
import uuid
import re
import sys
sys.path.append(r"D:\dsd-server-module-of-jokers\src\dsdServer")
import db.device
import db.admin
import db.model


def check_uuidv4(test_uuid, version=4):
    try:
        if uuid.UUID(test_uuid).version == version:
            one_device = db.device.get(test_uuid, create=False)
            if one_device is None:
                return False
        return True
    except ValueError:
        return False


def check_email_address(email):
    if len(email) > 254:
        return False
    try:
        res = re.match(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email) is not None
    except:
        return False
    return res

def set_email(test_uuid, email_account=None):
    one_device = db.device.get(test_uuid)
    try:
        one_device.email = email_account
        return True
    except:
        return False


def get_email(test_uuid):
    one_device = db.device.get(test_uuid)
    return one_device.email


def get_calibration(test_uuid):
    one_device = db.device.get(test_uuid)
    return one_device.calibration


def set_calibration(test_uuid, new_calibration=None):
    one_device = db.device.get(test_uuid)
    one_device.calibration = new_calibration


def get_model(test_uuid, algo):
    one_device = db.device.get(test_uuid)
    return one_device.model[algo]


def set_model(test_uuid, algo, new_model=None):
    one_device = db.device.get(test_uuid)
    one_device.model[algo] = new_model


def remove_device(test_uuid):
    db.device.remove(test_uuid)


def get_base_model(algo):
    return db.device.get(uuid.UUID(int=0)).model[algo]


def set_base_model(algo, base_model_path):
    db.device.get(uuid.UUID(int=0)).model[algo] = base_model_path


def check_admin_info(username, password):
    return db.admin.check(username, password)


def get_device(duuid) -> db.device.Device:
    return db.device.get(duuid)


def check_algo(algo):
    try:
        with open('al/algo.json', 'r') as f:
            al_list = json.load(f)
            return algo in al_list.keys()
    except:
        return False

