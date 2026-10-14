import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tools.experiment_a import run_experiment_a
from tools.experiment_b import run_experiment_b
from tools.experiment_c import run_experiment_c


def _format_machine():
    import platform
    return (
        f"Python {platform.python_version()}\n"
        f"Sistema: {platform.system()} {platform.release()}\n"
        f"Procesador: {platform.processor()}\n"
        f"Maquina: {platform.machine()}"
    )


def main():
    os.makedirs("results", exist_ok=True)

    results_a = run_experiment_a()
    results_b = run_experiment_b()
    results_c = run_experiment_c()

    # CSV resumen
    csv_path = os.path.join("results", "experiments_summary.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("experimento,eventos,tamanio_kb,buffer,tiempo_s,eventos_s,us_linea,"
                "mem_perezosa_kb,mem_lista_kb\n")
        for r in results_b:
            f.write(f"B,{r['events']},{r['size_kb']:.1f},,"
                    f"{r['read_time']:.6f},{r['events_per_sec']:.1f},"
                    f"{r['us_per_line']:.2f},,\n")
        for r in results_c:
            f.write(f"C,{r['events']},,,{r['time_lazy']:.6f},,,"
                    f"{r['mem_lazy_kb']:.1f},{r['mem_full_kb']:.1f}\n")
        for r in results_a:
            f.write(f"A,{r['events']},,{r['buffer_size']},{r['time_seconds']:.6f},"
                    f"0,0,,\n")

    # TXT resumen
    txt_path = os.path.join("results", "experiments_summary.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("RESUMEN DE EXPERIMENTOS\n")
        f.write("=" * 60 + "\n\n")
        f.write(_format_machine() + "\n\n")

        f.write("Experimento A: tiempo de escritura vs buffer (100k eventos)\n")
        f.write(f"{'Buffer':>10} {'Tiempo (s)':>12}\n")
        for r in results_a:
            f.write(f"{r['buffer_size']:>10} {r['time_seconds']:>12.4f}\n")
        f.write("\n")

        f.write("Experimento B: rendimiento de lectura\n")
        f.write(f"{'Eventos':>10} {'Tamanio KB':>12} {'Tiempo s':>12} "
                f"{'Ev/s':>12} {'us/linea':>12}\n")
        for r in results_b:
            f.write(f"{r['events']:>10} {r['size_kb']:>12.1f} {r['read_time']:>12.4f} "
                    f"{r['events_per_sec']:>12.1f} {r['us_per_line']:>12.2f}\n")
        f.write("\n")

        f.write("Experimento C: memoria perezosa vs lista completa\n")
        f.write(f"{'Eventos':>10} {'T. lazy s':>12} {'Mem lazy KB':>14} "
                f"{'T. full s':>12} {'Mem full KB':>14}\n")
        for r in results_c:
            f.write(f"{r['events']:>10} {r['time_lazy']:>12.4f} {r['mem_lazy_kb']:>14.1f} "
                    f"{r['time_full']:>12.4f} {r['mem_full_kb']:>14.1f}\n")

    print(f"\nResumen guardado en {csv_path} y {txt_path}")


if __name__ == "__main__":
    main()
