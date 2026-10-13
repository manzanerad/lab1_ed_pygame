import os
import glob

def parse_line(line):
    if not line or not line.strip():
        return None
        
    line = line.strip()

    parts = line.split('|')
    if len(parts) != 4:
        return None

    timestamp_str, session_id, event_type, params_str = parts

    try:
        timestamp = float(timestamp_str)
    except ValueError:
        return None

    params = {}
    if params_str.strip():
        pairs = params_str.split(';')
        for pair in pairs:
            if not pair.strip():
                continue
            if '=' not in pair:
                continue

            kv = pair.split('=', 1)
            if len(kv) != 2:
                continue
                
            key, val = kv[0].strip(), kv[1].strip()
            if not key:
                continue

            parsed_val = val
            try:
                if '.' in val:
                    parsed_val = float(val)
                else:
                    parsed_val = int(val)
            except ValueError:
                pass

            params[key] = parsed_val

    return {
        "timestamp": timestamp,
        "session_id": session_id.strip(),
        "event_type": event_type.strip(),
        "params": params
    }


def iter_events(log_dir):
    if not os.path.exists(log_dir):
        return

    log_files = sorted(glob.glob(os.path.join(log_dir, "events_*.log")))
    
    for path in log_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    event = parse_line(line)
                    if event is not None:
                        yield event
        except Exception:
            continue

def generate_data_quality_report(log_dir):
    files_processed = 0
    lines_read = 0
    valid_events = 0
    corrupt_lines = 0

    sessions_started = set()
    sessions_ended = set()
    
    if os.path.exists(log_dir):
        log_files = sorted(glob.glob(os.path.join(log_dir, "events_*.log")))
        files_processed = len(log_files)

        for path in log_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        lines_read += 1

                        if not line.strip():
                            corrupt_lines += 1
                            continue

                        event = parse_line(line)
                        if event is None:
                            corrupt_lines += 1
                        else:
                            valid_events += 1
                            ev_type = event["event_type"]
                            s_id = event["session_id"]
                            
                            if ev_type == "SESSION_START":
                                sessions_started.add(s_id)
                            elif ev_type == "SESSION_END":
                                sessions_ended.add(s_id)
            except Exception:
                continue
    
    incomplete_sessions = len(sessions_started - sessions_ended)

    valid_pct = (valid_events / lines_read * 100) if lines_read > 0 else 0
    corrupt_pct = (corrupt_lines / lines_read * 100) if lines_read > 0 else 0

    report = f"""--- REPORTE DE CALIDAD DE DATOS ---
Archivos procesados:      {files_processed}
Lineas leidas:            {lines_read:,}
Eventos validos:          {valid_events:,} ({valid_pct:.2f}%)
Lineas corruptas:         {corrupt_lines:,} ({corrupt_pct:.2f}%)
Sesiones incompletas:     {incomplete_sessions} (SESSION_START sin SESSION_END)
------------------------------------"""
    
    return report