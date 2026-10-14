import os
import glob


def iter_events(log_dir="logs"):
    """
    Recorre todos los archivos events_*.log en log_dir en orden
    y entrega eventos validos uno a uno (generador puro).
    """
    if not os.path.isdir(log_dir):
        return

    pattern = os.path.join(log_dir, "events_*.log")
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:           # lectura perezosa linea por linea
                event = parse_line(line)
                if event is not None:
                    yield event


def parse_line(line):
    """
    Parsea una linea de bitacora.
    Formato: timestamp|session_id|event_type|clave=valor;clave=valor
    Devuelve un dict o None si la linea es corrupta/incompleta.
    """
    if not line or not line.strip():
        return None

    # No usar strip() completo para no alterar valores con espacios
    line = line.rstrip("\n").rstrip("\r")
    if not line:
        return None

    parts = line.split("|")
    if len(parts) != 4:
        return None

    timestamp_str, session_id, event_type, param_str = parts

    try:
        timestamp = float(timestamp_str)
    except ValueError:
        return None

    if not session_id or not event_type:
        return None

    params = {}
    if param_str:
        for pair in param_str.split(";"):
            if not pair:
                continue
            if "=" not in pair:
                continue
            key, value = pair.split("=", 1)
            if key:
                params[key] = value

    return {
        "timestamp": timestamp,
        "session_id": session_id,
        "event_type": event_type,
        "params": params,
    }
