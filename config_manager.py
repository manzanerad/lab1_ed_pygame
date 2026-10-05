import json
import os

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "player": "ana",
    "volume": 80,
    "difficulty": "normal"
}

def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG, path)
        return DEFAULT_CONFIG.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                cfg.setdefault(key, value)
            return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(cfg, path=CONFIG_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
