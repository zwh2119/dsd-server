
import os
import sqlite3

WORK_DIR = os.getenv('DSD_DATABASE')

if WORK_DIR is None:
    WORK_DIR = './data'

WORK_DIR = os.path.abspath(WORK_DIR)

DB_PATH = os.path.join(WORK_DIR, 'db.sqlite3')

BASE_MODEL = 'base.mdl'
BASE_MODEL = os.path.join(WORK_DIR, BASE_MODEL)

DEVICE = 'device'
DEVICE = os.path.join(WORK_DIR, DEVICE)

MODEL = os.path.join(DEVICE, '%s', '%s.mdl')

CALIBRATION = 'calibration'
CALIBRATION = os.path.join(DEVICE, '%s', CALIBRATION)

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(DEVICE, exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.set_trace_callback(print)

conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(255) PRIMARY KEY NOT NULL,
        password VARCHAR(255) NOT NULL
    );
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        uuid VARCHAR(255) PRIMARY KEY NOT NULL,
        email VARCHAR(255),
        calibration VARCHAR(255)
    );
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS model (
        uuid VARCHAR(255) NOT NULL,
        al VARCHAR(255) NOT NULL,
        path VARCHAR(255) DEFAULT NULL,
        primary key(uuid,al)
    );
''')

conn.commit()
