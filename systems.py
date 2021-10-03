import sys
import os
import json

FILE_SETTINGS_JSON = "settings.json"

class SystemsData:
    _instance = None
    inited = False

    def __init__(self):
        if False == SystemsData.inited:
            path = os.path.abspath(__file__)
            path = os.path.dirname(path)
            path_jfile = os.path.join(path, FILE_SETTINGS_JSON)
            with open(path_jfile) as f:
                self._json_dict = json.load(f)
            SystemsData.inited = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def json_dict(self):
        return self._json_dict

    def get_idms(self):
        return self._json_dict.keys()

def main():
    sysdat = SystemsData()

    print(sysdat.json_dict)
    print(sysdat.get_idms())
    return

if __name__ == "__main__":
    main()