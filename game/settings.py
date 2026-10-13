import json
import os

CONFIG_PATH = "config.json"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return _default_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def _default_config():
    return {
        "player": "ana",
        "volume": 80,
        "difficulty": "normal",
        "screen_width": 800,
        "screen_height": 600,
    }







