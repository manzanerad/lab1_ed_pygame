import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from telemetry.reader import iter_events
from tools.synthetic_logs import generate_synthetic_log


SIZES = [5_000, 50_000, 100_000]


def run_experiment_b():
    print("\nExperimento B: rendimiento de lectura")
    print("=" * 80)
    print(f"{'Eventos':>10} {'Tamanio (KB)':>14} {'T. lectura (s)':>16} "
          f"{'Eventos/s':>12} {'us/linea':>12}")
    print("-" * 80)

    results = []
    for n in SIZES:
        log_dir = f"data/experiments/exp_b_{n}"
        generate_synthetic_log(log_dir, n_events=n, seed=42)

        # Tamanio aproximado en KB
        total_bytes = sum(
            os.path.getsize(os.path.join(log_dir, f))
            for f in os.listdir(log_dir)
            if f.endswith(".log")
        )
        size_kb = total_bytes / 1024

        t0 = time.perf_counter()
        count = 0
        for _ in iter_events(log_dir):
            count += 1
        elapsed = time.perf_counter() - t0

        events_per_sec = count / elapsed if elapsed > 0 else 0
        us_per_line = (elapsed / count) * 1_000_000 if count > 0 else 0

        results.append({
            "events": n,
            "size_kb": size_kb,
            "read_time": elapsed,
            "events_per_sec": events_per_sec,
            "us_per_line": us_per_line,
        })
        print(f"{n:>10} {size_kb:>14.1f} {elapsed:>16.4f} "
              f"{events_per_sec:>12.1f} {us_per_line:>12.2f}")

    return results


if __name__ == "__main__":
    run_experiment_b()
