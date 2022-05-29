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

_tasks: dict = {}
_stops: dict = {}


def notify(device: db.device.Device) -> None:
    if device.email:
        print(
            f'Sending email to {device.email}, notifying new model for {device.uuid}')


def __train(device: db.device.Device, info: dict, stop: threading.Event) -> None:
    print(f'Starting training for {device.uuid}')

    calibration = device.calibration
    new_model_dir = tempfile.mkdtemp()
    new_model = os.path.join(new_model_dir, 'model')
    base_model = db_solution.get_base_model(info['name'])
    base_model = info['base'] if base_model is None else base_model
    entry_point = info['entry_point']['train']
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
        device.model = new_model
        threading.Thread(target=notify, args=(device,)).start()
    else:
        print(f'Training for {device.uuid} failed returning {proc.returncode}')

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
    with open('al/al.json', 'r') as f:
        algo_list = json.load(f)
    info = algo_list[algo]
    pos_dir = os.path.abspath('./al')
    info['base'] = info['base'].replace('$ALGO', pos_dir)
    info['entrypoint']['train'] = [x.replace('$ALGO', pos_dir) for x in info['entrypoint']['train']]

    threading.Thread(target=_train, args=(duuid, info)).start()
