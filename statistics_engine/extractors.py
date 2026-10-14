from telemetry.reader import iter_events


def iter_numeric(log_dir, event_type, param, default=0.0):
    for event in iter_events(log_dir):
        if event["event_type"] != event_type:
            continue
        raw = event["params"].get(param, str(default))
        try:
            yield float(raw)
        except ValueError:
            continue


def iter_categorical(log_dir, event_type, param):
    for event in iter_events(log_dir):
        if event["event_type"] != event_type:
            continue
        value = event["params"].get(param)
        if value is not None:
            yield value


def iter_sessions(log_dir):
    sessions = {}
    for event in iter_events(log_dir):
        sid = event["session_id"]
        et = event["event_type"]
        p = event["params"]

        if sid not in sessions:
            sessions[sid] = {
                "session_id": sid,
                "player": p.get("player", "unknown"),
                "difficulty": p.get("difficulty", "unknown"),
                "score": 0.0,
                "level": 1,
                "duration": 0.0,
                "result": "unknown",
                "deaths": 0,
                "damage_total": 0.0,
            }

        if et == "SESSION_END":
            try:
                sessions[sid]["score"] = float(p.get("score", 0))
                sessions[sid]["level"] = int(p.get("level", 1))
                sessions[sid]["duration"] = float(p.get("duration", 0))
            except ValueError:
                pass
            sessions[sid]["result"] = p.get("result", "unknown")
        elif et == "DAMAGE_TAKEN":
            try:
                sessions[sid]["damage_total"] += float(p.get("amount", 0))
            except ValueError:
                pass
        elif et == "PLAYER_DEATH":
            sessions[sid]["deaths"] += 1

    return sessions.values()
