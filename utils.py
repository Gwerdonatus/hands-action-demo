# utils.py
import json
import os

def load_config(path="config.json"):
    here = os.path.dirname(__file__)
    cfg_path = os.path.join(here, path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)
