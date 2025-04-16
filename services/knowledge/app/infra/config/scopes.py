import os
import json
from enum import Enum


class Scopes(Enum):
    DivisionWrite = ""
    DivisionRead = ""
    CardWrite = ""
    CardRead = ""
    DishWrite = ""
    DishRead = ""


def _generate_scopes() -> Scopes:
    path = os.getcwd() + "/scopes.json"
    with open(path, "r") as f:
        data = json.loads(f.read())

    class Scopes(Enum):
        DivisionWrite = data["DivisionWrite"]
        DivisionRead = data["DivisionRead"]
        CardWrite = data["CardWrite"]
        CardRead = data["CardRead"]
        DishWrite = data["DishWrite"]
        DishRead = data["DishRead"]

    return Scopes


Scopes = _generate_scopes()
