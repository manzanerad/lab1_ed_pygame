import os
import sys
import time
import tracemalloc

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from telemetry.reader import iter_events
from tools.synthetic_logs import generate_synthetic_log


SIZES = [5_000, 50_000, 100_000]


def _read_lazy(log_dir):
    """Consume el generador sin guardar nada."""
    for _ in iter_events(log_dir):
        pass


def _read_full(log_dir):
    """Carga todos los eventos en una lista."""
    return list(iter_events(log_dir))


def _measure_memory(func, log_dir):
    tracemalloc.start()
    func(log_dir)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, peak


def _measure_time(func, log_dir):
    t0 = time.perf_counter()
    func(log_dir)
    return time.perf_counter() - t0


def run_experiment_c():
    print("\nExperimento C: lectura perezosa vs carga completa")
    print("=" * 95)
    print(f"{'Eventos':>10} {'T. perezoso (s)':>16} {'Mem. perezosa (KB)':>20} "
          f"{'T. lista (s)':>14} {'Mem. lista (KB)':>18}")
    print("-" * 95)

    results = []
    for n in SIZES:
        log_dir = f"data/experiments/exp_c_{n}"
        generate_synthetic_log(log_dir, n_events=n, seed=42)

        t_lazy = _measure_time(_read_lazy, log_dir)
        _, peak_lazy = _measure_memory(_read_lazy, log_dir)

        t_full = _measure_time(_read_full, log_dir)
        _, peak_full = _measure_memory(_read_full, log_dir)

        results.append({
            "events": n,
            "time_lazy": t_lazy,
            "mem_lazy_kb": peak_lazy / 1024,
            "time_full": t_full,
            "mem_full_kb": peak_full / 1024,
        })
        print(f"{n:>10} {t_lazy:>16.4f} {peak_lazy / 1024:>20.1f} "
              f"{t_full:>14.4f} {peak_full / 1024:>18.1f}")

    return results


if __name__ == "__main__":
    run_experiment_c()
