import os

SAMPLE = [
    "1717000012.412|S0007|SESSION_START|player=ana;difficulty=normal\n",
    "\n",  # vacía
    "1717000031.640|S0007|ENEMY_KILL|type=slime;wave=1\n",
    "linea_sin_formato\n",  # corrupta
    "1717000045.900|S0007|DAMAGE_TAKEN|amount=12;source=slime\n",
    "1717000090.000|S0007|PLAYER_DEATH|cause=slime;level=4\n",
    "1717000090.010|S0007|SESSION_END|score=3200;level=4;duration=77.6;result=death\n",
    "1717000100.000|S0008|SESSION_START|player=pepe;difficulty=hard\n",
    "mal|campo|extra|otro|mas\n",  # 5 campos
    "no_es_timestamp|S0008|ENEMY_KILL|type=slime;wave=1\n",  # timestamp inválido
    "1717000110.000|S0008|DAMAGE_TAKEN|amount=;source=fall\n",  # valor vacío
]


def main():
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "events_corrupt_test.log")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(SAMPLE)
    print(f"Bitácora corrupta generada en {path}")


if __name__ == "__main__":
    main()
