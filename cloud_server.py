import shutil
import tarfile
import tempfile
import beaker.session
from bottle import *
from beaker.middleware import SessionMiddleware
import hmac
from hashlib import sha1
import json
import timestamp_solution
import db_solution
import os
import run_train

cloud_server = Bottle()

session_opts = {
    'session.type': 'file',  # 以文件的方式保存session
    'session.cookie_expires': 3600,  # session过期时间为3600秒
    'session.data_dir': './sessions',  # session存放路径
    'session.auto': True,
    'session.samesite': 'None',
    'session.secure' : True

}


def get_error(code, text):
    response.status = code
    response.content_type = 'application/json'
    response.body = json.dumps({'error': text})
    return response


def get_success(dict_content=None):

    response.status = 200
    if dict_content is None:
        response.body = 'success'
    else:
        response.content_type = 'application/json'
        response.body = json.dumps(dict_content)
    return response


# @cloud_server.hook('after_request')
# def enable_cors():
#     response.headers['Access-Control-Allow-Origin'] = request.headers.get("Origin")
#     response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,PATCH,HEAD,CONNECT,OPTIONS,TRACE'
#     response.headers['Access-Control-Allow-Headers'] = 'Origin,Content-Type,Accept,User-Agent,Cookie,Authorization,X-Auth-Token,X-Requested-With'
#
#     response.headers['Access-Control-Allow-Credentials'] = "true"
#     response.headers['Allow-Control-Expose-Headers'] = 'Signature'



# @cloud_server.hook('before_request')
# def validate():
#     REQUEST_METHOD = request.environ.get('REQUEST_METHOD')
#     HTTP_ACCESS_CONTROL_REQUEST_METHOD = request.environ.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD')
#     if REQUEST_METHOD == 'OPTIONS' :
#         response.status = 200
#         return response



@cloud_server.get('/api/timestamp')
def get_signed_timestamp():
    return timestamp_solution.create_signed_timestamp()


@cloud_server.post('/api/device/<uuid>/email')
def set_contact_email(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

        if not db_solution.check_uuidv4(uuid):
            return get_error(404, 'Invalid uuidv4')

    email_json = request.json

    if email_json is None:
        return get_error(400, 'Invalid email address')

    email_account = email_json['email']
    print(email_account)

    if email_account is None:
        return get_error(400, 'Invalid email address')

    if not db_solution.check_email_address(email_account):
        return get_error(400, 'Invalid email address')

    if not db_solution.set_email(uuid, email_account):
        return get_error(400, 'Invalid email address')

    return get_success()


@cloud_server.get('/api/device/<uuid>/email')
def get_contact_email(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    email_account = db_solution.get_email(uuid)
    if email_account is None:
        return get_error(404, 'No valid email address set')

    return get_success({'email': email_account})


@cloud_server.delete('/api/device/<uuid>/email')
def clear_contact_email(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    db_solution.set_email(test_uuid=uuid)

    return get_success()


@cloud_server.route('/api/device/<uuid>/calibration', method='HEAD')
def check_calibration_available(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4.')

    if db_solution.get_calibration(uuid) is None:
        return get_error(404, 'No data collected.')
    else:
        return get_success()


@cloud_server.get('/api/device/<uuid>/calibration')
def download_calibration_data(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:
        return get_error(401, 'No administration authority')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    file = db_solution.get_calibration(uuid)
    if file is None:
        return get_error(404, 'No data collected')

    pos_dir = tempfile.mkdtemp()
    pos_path = os.path.join(pos_dir, 'calibration.tar.gz')

    with tarfile.open(pos_path, 'w:gz') as tf:
        for one_motion in os.listdir(file):
            tf.add(name=os.path.join(file, one_motion), arcname=one_motion)

    download_file = static_file('calibration.tar.gz', root=pos_dir, download=True, mimetype='application/x-tar+gzip')

    return download_file


@cloud_server.put('/api/device/<uuid>/calibration')
def upload_calibration_data(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')


    file = request.files.get('calibration')
    if file is None:
        print('file is None!')
        return get_error(400, 'Invalid request content')
    file_name = file.filename
    file_dir = tempfile.mkdtemp()
    file_path = os.path.join(file_dir, 'calibration.tar.gz')
    sig = request.headers.get('Signature')
    file_type = request.content_type
    # if file_type != 'application/x-tar+gzip':
    #     return get_error(400, 'Invalid request content type')

    file.save(file_path, overwrite=True)
    print("sig:",sig)
    print("file:",file_path)
    print("uuid:", uuid)
    if not timestamp_solution.check_signature(file_path, sig, uuid):
        return get_error(400, 'Invalid file signature')


    try:
        with tarfile.open(file_path) as tf:
            tf.extractall(file_dir)
        os.unlink(file_path)
    except:
        return get_error(400, 'Invalid file content')

    # os.system('tar  xzvf  /tmp/{}  -C  /tmp/'.format(file_name))

    db_solution.set_calibration(uuid, file_dir)
    shutil.rmtree(file_dir)

    # run_train.run_train(uuid)

    # os.system('python ./al/train.py {} {}'.format(db_solution.get_calibration(uuid), '/tmp/model'))

    # db_solution.set_model(uuid, '/tmp/model')
    # os.unlink('/tmp/model')
    return get_success()


@cloud_server.delete('/api/device/<uuid>/calibration')
def clear_calibration_data(uuid):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    db_solution.set_calibration(uuid)

    return get_success()


@cloud_server.route('/api/device/<uuid>/model/<algo>', method='HEAD')
def check_device_model_version(uuid, algo):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    model_path = db_solution.get_model(uuid)
    if model_path is not None:
        statinfo = os.stat(model_path)
        response.set_header('Content-Length', statinfo.st_size)
        response.set_header('Last-Modified', statinfo.st_mtime)
    else:
        del response.headers['Last-Modified']
    return response


@cloud_server.get('/api/device/<uuid>/model/<algo>')
def download_device_model(uuid, algo):

    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    model_path = db_solution.get_model(uuid, algo)
    if model_path is not None:
        file = model_path
        statinfo = os.stat(model_path)
        response.set_header('Content-Length', statinfo.st_size)
        response.set_header('Last-Modified', statinfo.st_mtime)
    else:
        del response.headers['Last-Modified']
        file = db_solution.get_base_model(algo)

    if file is None:
        return get_error(404, 'No base model')
    # response.add_header('Signature', timestamp_solution.get_signature(file))
    file_name = os.path.split(file)[1]
    path = os.path.split(file)[0]

    download_file = static_file(file_name, root=path, download=True, mimetype='application/octet-stream')
    download_file.add_header('Signature', timestamp_solution.get_signature(file))

    return download_file


@cloud_server.post('/api/device/<uuid>/model/<algo>')
def train_algo(uuid, algo):

    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    run_train.run_train(uuid, algo)


@cloud_server.put('/api/device/<uuid>/model/<algo>')
def upload_model(uuid, algo):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:
        return get_error(401, 'No administration authority')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    file_type = request.headers.get('Content-Type')

    file_upload = request.files.get('model')

    if file_upload is None:
        return get_error(400, 'Invalid request content')

    pos_dir = tempfile.mkdtemp()
    file_path = os.path.join(pos_dir, 'model')
    file_upload.save(file_path, overwrite=True)

    name = file_upload.filename

    db_solution.set_model(uuid, algo, file_path)

    shutil.rmtree(pos_dir)

    return get_success()


@cloud_server.delete('/api/device/<uuid>/model/<algo>')
def clear_cloud_model(uuid, algo):

    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    db_solution.set_model(uuid, algo)

    return get_success()


@cloud_server.delete('/api/device/<uuid>/model')
def clear_all_model(uuid):

    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    with open('al/algo.json', 'r') as f:
        algo_list = json.load(f)
    for algo in algo_list.keys():
        db_solution.set_model(uuid, algo)
    return get_success()


@cloud_server.delete('/api/device/<uuid>')
def clear_device(uuid):

    session = request.environ.get('beaker.session')
    if session.get('usr') is None:

        auth = request.headers.get('Authorization')
        if auth is None or not timestamp_solution.check_authentication(auth, uuid):
            return get_error(401, 'Invalid authorization')

    if not db_solution.check_uuidv4(uuid):
        return get_error(404, 'Invalid uuidv4')

    db_solution.remove_device(uuid)
    return get_success()


'''此端口已废弃'''
# @cloud_server.delete('/api/device/<uuid>')
# def ban_device(uuid):
#     session = request.environ.get('beaker.session')
#     if session.get('usr') is None:
#         return get_error(401, 'No administration authority')
#
#     if not db_solution.check_uuidv4(uuid):
#         return get_error(404, 'Invalid uuidv4')
#
#     is_ban = request.json
#     if is_ban is None or is_ban['ban']:
#         return get_error(400, 'Invalid request content')
#
#     if is_ban['ban']:
#         db_solution.remove_device(uuid)
#     return get_success()


# @cloud_server.route('/session', method='OPTIONS')
# def pre_deal():
#     response.status = 200
#     return response


@cloud_server.post('/api/session', method='POST')
def login():
    # username = request.query.get('username')
    # password = request.params.get('password')
    if request.json is None:
        return get_error(403, 'Admin login failed')
    username = request.json['username']
    password = request.json['password']
    print(username)
    print(password)


    # print(request.json)
    #
    # print(username)
    #
    # print(request.query.get('username'))
    # print(request.forms.get('username'))
    # print(request.params.get('username'))
    # print(request.POST.get('username', ''))
    # print(request.POST.get('password', ''))
    # print(request.environ['REQUEST_FORM'])
    if db_solution.check_admin_info(username, password):
        session = request.environ.get('beaker.session')
        session['usr'] = username

        session.save()

        return get_success()
    else:
        return get_error(403, 'Admin login failed')


@cloud_server.delete('/api/session')
def logout():
    session = request.environ.get('beaker.session')
    session.delete()
    session.save()
    return get_success()


@cloud_server.get('/api/models')
def get_all_algo():
    with open('al/algo.json', 'r') as f:
        algo_list = json.load(f)
    return get_success(algo_list)


@cloud_server.get('/api/model/<algo>')
def download_base_model(algo):

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    # algo_list = json.load('al/algo.json')
    #
    # model_file = algo_list[al]['base']

    model_file = db_solution.get_base_model(algo)

    file_name = os.path.split(model_file)[1]
    path = os.path.split(model_file)[0]

    download_file = static_file(file_name, root=path, download=True, mimetype='application/octet-stream')
    return download_file


@cloud_server.put('/api/model/<algo>')
def upload_base_model(algo):
    session = request.environ.get('beaker.session')
    if session.get('usr') is None:
        return get_error(401, 'No administration authority')

    if not db_solution.check_algo(algo):
        return get_error(404, 'Algorithm not found')

    file_type = request.headers.get('Content-Type')
    # if file_type.split(';')[0] is None or file_type != 'multipart/form-data':
    #     return get_error(400, 'Invalid request content')

    file = request.files.get('model')
    if file is None:
        return get_error(400, 'Invalid request content')
    file_name = file.filename

    pos_dir = tempfile.mkdtemp()
    pos_path = os.path.join(pos_dir, 'model')

    file.save(pos_path, overwrite=True)
    # os.system('tar  xzvf  /tmp/{}  -C  /tmp/'.format(file_name))

    db_solution.set_base_model(algo, pos_path)
    shutil.rmtree(pos_dir)

    return get_success()


# 下面两个为测试端口，可随意修改用于测试

@cloud_server.get('/test')
def test():
    print(request.headers.get('content-type'))


@cloud_server.post('/test')
def tt():
    session = request.environ.get('beaker.session')
    session['usr'] = 'username'

    session.save()


app = SessionMiddleware(cloud_server, session_opts)


if __name__ == '__main__':

    run(app=app, host='0.0.0.0', port=8080, debug=True)
