import os
import sys
import time
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tools.synthetic_logs import generate_synthetic_log


BUFFER_SIZES = [1, 10, 100, 1000]
N_EVENTS = 100_000
OUTPUT_DIR = "results"


def run_experiment_a():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []

    print("Experimento A: tiempo de escritura vs tamano de buffer")
    print("=" * 60)
    print(f"{'Buffer':>10} {'Eventos':>10} {'Tiempo (s)':>12}")
    print("-" * 60)

    for buf in BUFFER_SIZES:
        log_dir = f"data/experiments/exp_a_buf_{buf}"
        t0 = time.perf_counter()
        written = generate_synthetic_log(
            log_dir=log_dir,
            n_events=N_EVENTS,
            buffer_size=buf,
            seed=42,
        )
        elapsed = time.perf_counter() - t0

        results.append({
            "buffer_size": buf,
            "events": written,
            "time_seconds": elapsed,
        })
        print(f"{buf:>10} {written:>10} {elapsed:>12.4f}")

    plot_path = os.path.join(OUTPUT_DIR, "experiment_a.png")
    draw_buffer_plot(results, plot_path)
    return results


def draw_buffer_plot(results, path):
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    screen.fill((255, 255, 255))

    margin = 80
    chart_w = width - 2 * margin
    chart_h = height - 2 * margin

    # Ejes
    pygame.draw.line(screen, (0, 0, 0),
                     (margin, height - margin),
                     (width - margin, height - margin), 2)
    pygame.draw.line(screen, (0, 0, 0),
                     (margin, margin),
                     (margin, height - margin), 2)

    times = [r["time_seconds"] for r in results]
    max_time = max(times) if times else 1.0

    def x_scale(buf):
        log_min = math.log10(1)
        log_max = math.log10(1000)
        log_b = math.log10(buf)
        return margin + (log_b - log_min) / (log_max - log_min) * chart_w

    def y_scale(t):
        return height - margin - (t / max_time) * chart_h

    # Linea y puntos
    for i, r in enumerate(results):
        x = x_scale(r["buffer_size"])
        y = y_scale(r["time_seconds"])
        pygame.draw.circle(screen, (220, 50, 50), (int(x), int(y)), 8)
        if i > 0:
            x_prev = x_scale(results[i - 1]["buffer_size"])
            y_prev = y_scale(results[i - 1]["time_seconds"])
            pygame.draw.line(screen, (50, 100, 200), (x_prev, y_prev), (x, y), 2)

    font = pygame.font.SysFont("monospace", 14)

    # Etiquetas X
    for r in results:
        x = x_scale(r["buffer_size"])
        label = font.render(str(r["buffer_size"]), True, (0, 0, 0))
        screen.blit(label, (int(x) - label.get_width() // 2, height - margin + 12))

    # Etiquetas Y
    for i in range(5):
        t = max_time * i / 4
        y = y_scale(t)
        label = font.render(f"{t:.3f}s", True, (0, 0, 0))
        screen.blit(label, (10, int(y) - 7))

    title = font.render(
        "Experimento A: tiempo de escritura vs tamano de buffer (100k eventos)",
        True, (0, 0, 0)
    )
    screen.blit(title, (margin, 30))

    x_label = font.render("Tamano de buffer (linea logaritmica)", True, (0, 0, 0))
    screen.blit(x_label, (width // 2 - x_label.get_width() // 2, height - 30))

    y_label = font.render("Tiempo (s)", True, (0, 0, 0))
    screen.blit(y_label, (15, height // 2))

    pygame.display.flip()
    pygame.image.save(screen, path)

    # Procesar eventos brevemente para evitar congelamiento
    for _ in range(5):
        pygame.event.pump()

    pygame.quit()
    print(f"\nGrafico guardado en {path}")


if __name__ == "__main__":
    run_experiment_a()
