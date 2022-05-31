import json
import tempfile
import time
import uuid
import shutil
import os.path
import threading
import subprocess
from tempfile import mkdtemp
import db_solution
import db.device
import smtplib
from email.mime.text import MIMEText

_tasks: dict = {}
_stops: dict = {}


def notify(device: db.device.Device, res : bool) -> None:
    if device.email:
        host = 'smtp.qq.com'
        port = 465
        pwd = 'pcxubuaviqtthcfe'
        sender = '1548767361@qq.com'
        receiver = device.email

        body = f'<p>Dear User of {device.uuid}:</p>'
        if res:
            body += '<p>&nbsp;&nbsp;&nbsp;&nbsp;We are glad to notify you that your training on the cloud ' \
                    'has finished and your personal model has benn genrated as expected.</p>'
            body += '<p>&nbsp;&nbsp;&nbsp;&nbsp;You can login the online system and deploy the model on your model.</p>'
            body += '<p>&nbsp;&nbsp;&nbsp;&nbsp;Wish you have a good experience!</p>'
        else:
            body += '<p>&nbsp;&nbsp;&nbsp;&nbsp;We are sorry to notify you that your training on the cloud failed for' \
                    'some unexpected reason.</p>'
            body += '<p>&nbsp;&nbsp;&nbsp;&nbsp;Please login on the online system to retry or contact our company</p>'
            body += '<p>&nbsp;&nbsp;&nbsp;&nbsp;Thanks for your support!</p>'
        msg = MIMEText(body, 'html')
        msg['subject'] = 'Training Result Notification from DSD'
        msg['from'] = sender
        msg['to'] = receiver
        try:
            s = smtplib.SMTP_SSL(host, port)
            s.login(sender, pwd)
            s.sendmail(sender, receiver, msg.as_string())
            print(f'Sending email to {device.email}, notifying new model for {device.uuid}')
        except:
            print(f'Send email to {device.email} failed')

    else:
        print(f'{device.uuid} \'s email is empty, failed to notify')


def __train(device: db.device.Device, info: dict, stop: threading.Event) -> None:
    print(f'Starting training for {device.uuid}')

    calibration = device.calibration
    new_model_dir = tempfile.mkdtemp()
    new_model = os.path.join(new_model_dir, 'model')
    base_model = db_solution.get_base_model(info['name'])
    base_model = info['base'] if base_model is None else base_model
    print('input model in the al: ', base_model)
    entry_point = info['entrypoint']['train']
    entry_point.append(calibration)
    entry_point.append(new_model)
    entry_point.append(base_model)

    proc = subprocess.Popen(
        entry_point,
        cwd='al'
    )
    while not stop.is_set():
        try:
            if proc.wait(5) is not None:
                break
        except subprocess.TimeoutExpired:
            pass
    else:
        print(f'Terminating running train process of {device.uuid}')
        while proc.poll() is None:
            proc.terminate()
            time.sleep(1)
            proc.kill()
    if proc.returncode == 0:
        print(f'Finished training for {device.uuid}')
        device.model[info['name']] = new_model
        # threading.Thread(target=notify, args=(device,True)).start()
        notify(device, True)
    else:
        print(f'Training for {device.uuid} failed returning {proc.returncode}')
        # threading.Thread(target=notify, args=(device, False)).start()
        notify(device, False)

    shutil.rmtree(new_model_dir)


def _train(duuid, info) -> None:
    device = db.device.get(duuid)
    if device.uuid in _tasks:
        while _tasks[device.uuid].is_alive():
            print(
                f'Training for {device.uuid} is still running! Terminating first...')
            _stops[device.uuid].set()
            time.sleep(5)
    _stops[device.uuid] = threading.Event()
    _tasks[device.uuid] = threading.Thread(
        name=str(device.uuid),
        target=__train,
        args=(device, info, _stops[device.uuid])
    )
    _tasks[device.uuid].start()


def run_train(duuid, algo) -> None:
    with open('al/algo.json', 'r') as f:
        algo_list = json.load(f)
    info = algo_list[algo]
    pos_dir = os.path.abspath('./al')
    info['base'] = info['base'].replace('$ALGO', pos_dir)
    print("base path: ", info['base'])
    info['entrypoint']['train'] = [x.replace('$ALGO', pos_dir) for x in info['entrypoint']['train']]

    threading.Thread(target=_train, args=(duuid, info)).start()
