import os
import sys
import glob
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from telemetry.writer import EventLogWriter


PLAYERS = ["ana", "ben", "carlos", "diana", "eva", "frank", "gina", "hugo"]
DIFFICULTIES = ["easy", "normal", "hard"]
CAUSES = ["fall", "slime", "arrow_trap", "boss"]
ENEMIES = ["slime", "goblin", "bat", "boss"]


def _clear_dir(log_dir):
    os.makedirs(log_dir, exist_ok=True)
    for path in glob.glob(os.path.join(log_dir, "events_*.log")):
        os.remove(path)


def generate_synthetic_log(log_dir, n_events, buffer_size=100,
                           max_size_bytes=10 * 1024 * 1024, seed=42):
    """
    Genera una bitacora sintetica con aproximadamente n_events eventos.
    Devuelve el numero real de eventos escritos.
    """
    random.seed(seed)
    _clear_dir(log_dir)

    writer = EventLogWriter(
        log_dir=log_dir,
        buffer_size=buffer_size,
        max_size_bytes=max_size_bytes,
    )

    events_written = 0
    session_counter = 0
    timestamp = 1_000_000_000.0

    while events_written < n_events:
        session_counter += 1
        sid = f"S{session_counter:06d}"
        writer.session_id = sid

        player = random.choice(PLAYERS)
        difficulty = random.choice(DIFFICULTIES)
        writer.log("SESSION_START", {
            "player": player,
            "difficulty": difficulty,
        })
        events_written += 1
        if events_written >= n_events:
            break

        session_start_time = timestamp
        score = 0
        level = 1
        n_actions = random.randint(10, 200)

        alive = True
        for _ in range(n_actions):
            if events_written >= n_events:
                alive = False
                break

            timestamp += random.uniform(0.1, 2.0)

            action = random.random()
            if action < 0.60:
                enemy = random.choice(ENEMIES)
                score += random.randint(10, 100)
                writer.log("ENEMY_KILL", {"type": enemy, "wave": level})
            elif action < 0.80:
                amount = random.randint(1, 20)
                source = random.choice(CAUSES)
                writer.log("DAMAGE_TAKEN", {"amount": amount, "source": source})
            else:
                level += 1
                writer.log("LEVEL_UP", {
                    "level": level,
                    "time": round(timestamp - session_start_time, 1),
                })

            events_written += 1

            if random.random() < 0.02:
                writer.log("PLAYER_DEATH", {
                    "cause": random.choice(CAUSES),
                    "level": level,
                })
                writer.log("SESSION_END", {
                    "score": score,
                    "level": level,
                    "duration": round(timestamp - session_start_time, 1),
                    "result": "death",
                })
                events_written += 2
                alive = False
                break


        if alive and events_written < n_events:
            duration = round(timestamp - session_start_time, 1)
            writer.log("SESSION_END", {
                "score": score,
                "level": level,
                "duration": duration,
                "result": random.choice(["win", "death", "quit"]),
            })
            events_written += 1

    writer.close()
    return events_written


if __name__ == "__main__":
    n = generate_synthetic_log("data/experiments/synthetic_100k", n_events=100000)
    print(f"Eventos escritos: {n}")
