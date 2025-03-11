import os
import json
from enum import Enum


class Scopes(Enum):
    FileWrite = ""
    FileRead = ""


def _generate_scopes() -> Scopes:
    path = os.getcwd() + "/scopes.json"
    with open(path, "r") as f:
        data = json.loads(f.read())

    class Scopes(Enum):
        FileWrite = data["FileWrite"]
        FileRead = data["FileRead"]

    return Scopes


Scopes = _generate_scopes()
