import shutil
from turtle import update
from db import conn, MODEL, CALIBRATION
import os
from uuid import UUID
from typing import Union


class Model:
    def __init__(self, uuid):
        self.uuid = uuid

    def __setitem__(self, algo, path):
        if path is None:
            if self[algo] and os.path.exists(self[algo]):
                os.remove(self[algo])
        else:
            if self[algo] is None:
                conn.execute(f"INSERT INTO model VALUES (?, ?, ?)", (self.uuid, algo, MODEL % (self.uuid, algo)))
                conn.commit()
            
            if not os.path.exists(os.path.dirname(self[algo])):
                os.makedirs(os.path.dirname(self[algo]))
            shutil.copyfile(path, self[algo])


    def __getitem__(self, algo):
        c = conn.execute(f"SELECT * FROM model WHERE uuid = ? AND algo = ?", (self.uuid, algo))
        result = c.fetchone()
        if result is None: return None
        else: return result[2]

class Device:
    def __init__(self, uuid) -> None:
        self._uuid = uuid

    @property
    def uuid(self) -> UUID:
        return UUID(self._uuid, version=4)

    @property
    def email(self) -> str:
        c = conn.execute(
            "SELECT email FROM devices WHERE uuid = ?", (self._uuid,))
        return c.fetchone()[0]

    @email.setter
    def email(self, value: str) -> None:
        if value and len(value) > 254:
            raise ValueError("Too long email !")
        c = conn.execute("UPDATE devices SET email = ? WHERE uuid = ?",
                         (value, self._uuid))
        conn.commit()

    @property
    def model(self) -> str:
        return Model(self._uuid)

    @property
    def calibration(self) -> str:
        c = conn.execute(
            "SELECT calibration FROM devices WHERE uuid = ?", (self._uuid,))
        return c.fetchone()[0]

    @calibration.setter
    def calibration(self, value: str) -> None:
        if value is None:
            shutil.rmtree(self.calibration)
        else:
            if not os.path.exists(self.calibration):
                os.makedirs(self.calibration)

            shutil.rmtree(self.calibration, ignore_errors=True)
            shutil.copytree(value, self.calibration)


def exists(devid: Union[str, UUID]) -> bool:
    devid = UUID(str(devid), version=4).hex
    c = conn.execute("SELECT * FROM devices WHERE uuid = ?", (devid,))
    return c.fetchone() is not None


def get(uuid: Union[str, UUID]) -> Device:

    uuid = UUID(str(uuid), version=4).hex
    c = conn.cursor()
    c.execute("SELECT * FROM devices WHERE uuid = ?", (uuid,))
    row = c.fetchone()

    if row is None:
        conn.execute("INSERT INTO devices (uuid, email, calibration) VALUES (?,?,?) ",
                     (uuid, None, CALIBRATION % uuid))
        conn.commit()
        row = (uuid, None, CALIBRATION % uuid)
        os.makedirs(CALIBRATION % uuid)

    return Device(row[0])

def remove(uuid: Union[str, UUID]) -> None:
    uuid = UUID(str(uuid), version=4).hex
    conn.execute("DELETE FROM devices WHERE uuid = ?", (uuid,))
    conn.commit()

    dir = CALIBRATION % uuid
    if dir and os.path.exists(dir):
        shutil.rmtree(dir)

    dir = MODEL % uuid
    if dir and os.path.exists(dir):
        os.remove(dir)