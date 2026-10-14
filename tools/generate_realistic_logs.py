import os
import sys
import glob
import random

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from telemetry.writer import EventLogWriter


PLAYERS = ["ana", "ben", "carlos", "diana", "eva"]
DIFFICULTIES = ["easy", "normal", "hard"]
DEATH_CAUSES = ["fall", "slime", "arrow", "boss"]


def clear_logs(log_dir="logs"):
    os.makedirs(log_dir, exist_ok=True)
    for path in glob.glob(os.path.join(log_dir, "events_*.log")):
        os.remove(path)


def generate_sessions(n_sessions=30, log_dir="logs"):
    clear_logs(log_dir)
    writer = EventLogWriter(log_dir=log_dir, buffer_size=10)

    timestamp = 1_700_000_000.0

    for i in range(1, n_sessions + 1):
        sid = f"S{i:06d}"
        writer.session_id = sid

        player = random.choice(PLAYERS)
        difficulty = random.choice(DIFFICULTIES)
        writer.log("SESSION_START", {
            "player": player,
            "difficulty": difficulty,
        })

        session_start = timestamp
        score = 0
        level = 1
        alive = True

        difficulty_actions = {
            "easy": (30, 120),
            "normal": (20, 100),
            "hard": (10, 80),
        }
        min_actions, max_actions = difficulty_actions[difficulty]
        n_actions = random.randint(min_actions, max_actions)

        for _ in range(n_actions):
            timestamp += random.uniform(0.3, 2.5)

            r = random.random()
            if r < 0.55:
                score += random.randint(10, 60)
                writer.log("ENEMY_KILL", {
                    "type": random.choice(["slime", "goblin", "bat"]),
                    "wave": level,
                })
            elif r < 0.75:
                writer.log("DAMAGE_TAKEN", {
                    "amount": random.randint(1, 15),
                    "source": random.choice(DEATH_CAUSES),
                })
            else:
                level += 1
                writer.log("LEVEL_UP", {
                    "level": level,
                    "time": round(timestamp - session_start, 1),
                })

            if random.random() < 0.04:
                writer.log("PLAYER_DEATH", {
                    "cause": random.choice(DEATH_CAUSES),
                    "level": level,
                })
                # Siempre cerrar la sesion, aunque el resultado sea death
                writer.log("SESSION_END", {
                    "score": score,
                    "level": level,
                    "duration": round(timestamp - session_start, 1),
                    "result": "death",
                })
                alive = False
                break

        if alive:
            duration = round(timestamp - session_start, 1)
            result = "win" if level >= 5 else random.choice(["quit", "win"])
            writer.log("SESSION_END", {
                "score": score,
                "level": level,
                "duration": duration,
                "result": result,
            })

    writer.close()
    print(f"Generadas {n_sessions} sesiones en {log_dir}/")


if __name__ == "__main__":
    generate_sessions(30)
