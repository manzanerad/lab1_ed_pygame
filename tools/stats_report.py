import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from statistics_engine.descriptives import OnePassStats
from statistics_engine.quartiles import quartiles, outliers_iqr, outliers_z
from statistics_engine.frequency import FrequencyTable
from statistics_engine.correlation import PearsonAccumulator
from statistics_engine.extractors import iter_numeric, iter_categorical, iter_sessions
from statistics_engine.groups import compare_by_difficulty
from statistics_engine.progression import level_funnel


def print_stats(name, stream):
    stats = OnePassStats()
    values = []
    for x in stream:
        stats.add(x)
        values.append(x)
    print(f"\n=== {name} ===")
    print(f"n={stats.n}, suma={stats.sum:.2f}, media={stats.mean:.2f}")
    print(f"min={stats.min}, max={stats.max}, rango={stats.range:.2f}")
    print(f"var={stats.variance:.2f}, std={stats.std:.2f}, CV={stats.cv:.2f}%")
    if values:
        q = quartiles(values)
        print(f"mediana={q['median']:.2f}, Q1={q['q1']:.2f}, Q3={q['q3']:.2f}")
        print(f"atipicos IQR: {outliers_iqr(values)}")
        print(f"atipicos z>3: {outliers_z(values, 3)}")


def main():
    log_dir = "logs"

    print_stats("PUNTAJE", iter_numeric(log_dir, "SESSION_END", "score", 0))
    print_stats("DURACION", iter_numeric(log_dir, "SESSION_END", "duration", 0))
    print_stats("DAÑO TOTAL", (s["damage_total"] for s in iter_sessions(log_dir)))

    print("\n=== CAUSA DE MUERTE ===")
    ft = FrequencyTable()
    for cause in iter_categorical(log_dir, "PLAYER_DEATH", "cause"):
        ft.add(cause)
    for row in ft.rows():
        print(f"{row['value']:12s}  n={row['count']:4d}  "
              f"f={row['relative']*100:5.1f}%  F={row['cumulative']*100:6.1f}%")
    print(f"Moda: {ft.mode()}")

    print("\n=== EMBUDO DE NIVELES ===")
    sessions = list(iter_sessions(log_dir))
    for row in level_funnel(sessions):
        print(f"Nivel {row['level']}: "
              f"sesiones={row['sessions']}, "
              f"supervivencia={row['survival']:.1f}%, "
              f"abandono={row['abandonment']:.1f}%")

    print("\n=== COMPARACION POR DIFICULTAD ===")
    diff = compare_by_difficulty(sessions)
    for d in ["easy", "normal", "hard"]:
        if d in diff:
            print(f"{d}: n={diff[d]['count']}, "
                  f"media={diff[d]['mean']:.2f}, std={diff[d]['std']:.2f}")
    if "mean_difference" in diff:
        print(f"Diferencia hard-easy: {diff['mean_difference']:.2f} puntos "
              f"({diff['mean_difference_pct']:.2f}%)")

    print("\n=== CORRELACION: DURACION vs PUNTAJE ===")
    acc = PearsonAccumulator()
    for s in sessions:
        acc.add(s["duration"], s["score"])
    print(f"n={acc.n}, r={acc.correlation():.5f}")


if __name__ == "__main__":
    main()
