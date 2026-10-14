import pygame
from telemetry.quality import QualityReport
from statistics_engine.descriptives import OnePassStats
from statistics_engine.quartiles import quartiles, outliers_iqr, percentile
from statistics_engine.frequency import histogram
from statistics_engine.correlation import PearsonAccumulator
from statistics_engine.extractors import iter_numeric, iter_sessions


class StatsScreen:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.font = app.font
        self.small_font = app.small_font
        self.tabs = ["Resumen", "Distribucion", "Relacion"]
        self.active_tab = 0
        self.var_index = 0
        self.pair_index = 0
        self.show_quality = False

        self.VARS = [
            ("Puntaje", "SESSION_END", "score"),
            ("Duracion", "SESSION_END", "duration"),
            ("Dano", "DAMAGE_TAKEN", "amount"),
        ]

        self.PAIRS = [
            ("Duracion", "Puntaje", "duration", "score"),
            ("Dano", "Nivel", "damage_total", "level"),
        ]

    def run(self):
        while True:
            self.app.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
                    elif event.key == pygame.K_LEFT:
                        self.active_tab = (self.active_tab - 1) % len(self.tabs)
                    elif event.key == pygame.K_RIGHT:
                        self.active_tab = (self.active_tab + 1) % len(self.tabs)
                    elif event.key == pygame.K_UP:
                        if self.active_tab == 0:
                            self.var_index = (self.var_index - 1) % len(self.VARS)
                        elif self.active_tab == 2:
                            self.pair_index = (self.pair_index - 1) % len(self.PAIRS)
                    elif event.key == pygame.K_DOWN:
                        if self.active_tab == 0:
                            self.var_index = (self.var_index + 1) % len(self.VARS)
                        elif self.active_tab == 2:
                            self.pair_index = (self.pair_index + 1) % len(self.PAIRS)
                    elif event.key == pygame.K_q:
                        self.show_quality = not self.show_quality

            self.draw()
            if self.show_quality:
                self.draw_quality_overlay()

    def load_values(self, event_type, param, default=0.0):
        values = []
        for x in iter_numeric("logs", event_type, param, default):
            values.append(x)
        return values

    def load_sessions(self):
        return list(iter_sessions("logs"))

    def draw(self):
        self.screen.fill((20, 20, 30))

        # Pestañas
        tab_w = self.app.width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            x = i * tab_w
            color = (80, 80, 120) if i == self.active_tab else (40, 40, 60)
            pygame.draw.rect(self.screen, color, (x, 0, tab_w, 40))
            text = self.small_font.render(tab, True, (255, 255, 255))
            self.screen.blit(text, (x + tab_w // 2 - text.get_width() // 2, 12))

        if self.active_tab == 0:
            self._draw_summary()
        elif self.active_tab == 1:
            self._draw_distribution()
        elif self.active_tab == 2:
            self._draw_correlation()

        hint = self.small_font.render(
            "LEFT/RIGHT: tabs | UP/DOWN: cambiar variable/par | Q: calidad datos | ESC: menu",
            True, (150, 150, 150)
        )
        self.screen.blit(hint, (10, self.app.height - 25))
        pygame.display.flip()

    def _draw_summary(self):
        label, event_type, param = self.VARS[self.var_index]
        values = self.load_values(event_type, param)
        title = self.font.render(f"Resumen: {label}", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))

        if not values:
            msg = self.font.render("Sin datos", True, (200, 200, 200))
            self.screen.blit(msg, (40, 110))
            return

        stats = OnePassStats()
        for v in values:
            stats.add(v)
        q = quartiles(values)
        p90 = percentile(values, 90)

        lines = [
            f"n          = {stats.n}",
            f"suma       = {stats.sum:.2f}",
            f"media      = {stats.mean:.2f}",
            f"mediana    = {q['median']:.2f}",
            f"std        = {stats.std:.2f}",
            f"CV         = {stats.cv:.2f}%",
            f"min        = {stats.min}",
            f"max        = {stats.max}",
            f"P90        = {p90:.2f}",
        ]

        for i, line in enumerate(lines):
            text = self.font.render(line, True, (200, 230, 255))
            self.screen.blit(text, (60, 110 + i * 30))

    def _draw_distribution(self):
        values = self.load_values("SESSION_END", "score")
        title = self.font.render("Distribucion del puntaje", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))

        if not values:
            msg = self.font.render("Sin datos de puntaje", True, (200, 200, 200))
            self.screen.blit(msg, (40, 110))
            return

        q = quartiles(values)
        outliers = outliers_iqr(values)
        bins = histogram(values, k=8)

        # Dibujar histograma
        chart_x, chart_y = 60, 110
        chart_w = self.app.width - 120
        chart_h = 220

        max_count = max(b["count"] for b in bins) if bins else 1
        n_bins = len(bins)
        bin_w = chart_w / n_bins if n_bins else chart_w

        for i, b in enumerate(bins):
            h = (b["count"] / max_count) * chart_h if max_count else 0
            x = chart_x + i * bin_w
            y = chart_y + chart_h - h
            rect = pygame.Rect(x, y, bin_w - 4, h)
            pygame.draw.rect(self.screen, (100, 180, 255), rect)

        # Ejes
        pygame.draw.line(self.screen, (255, 255, 255),
                         (chart_x, chart_y + chart_h),
                         (chart_x + chart_w, chart_y + chart_h), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (chart_x, chart_y),
                         (chart_x, chart_y + chart_h), 2)

        # Escala X
        vmin = min(values)
        vmax = max(values)
        for i in range(5):
            ratio = i / 4
            val = vmin + ratio * (vmax - vmin)
            x = chart_x + ratio * chart_w
            label = self.small_font.render(f"{val/1000:.1f}k", True, (200, 200, 200))
            self.screen.blit(label, (int(x) - label.get_width() // 2, chart_y + chart_h + 8))

        # Diagrama de caja debajo
        box_y = chart_y + chart_h + 50
        box_h = 60
        scale_w = chart_w

        def scale(v):
            if vmax == vmin:
                return chart_x + scale_w / 2
            return chart_x + (v - vmin) / (vmax - vmin) * scale_w

        q1x = scale(q["q1"])
        medx = scale(q["median"])
        q3x = scale(q["q3"])

        # Bigotes: min a max no atípicos
        non_outliers = [v for v in values if v not in outliers]
        low_whisker = min(non_outliers) if non_outliers else q["q1"]
        high_whisker = max(non_outliers) if non_outliers else q["q3"]
        lw = scale(low_whisker)
        hw = scale(high_whisker)

        pygame.draw.line(self.screen, (255, 255, 255), (lw, box_y + box_h // 2),
                         (hw, box_y + box_h // 2), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (lw, box_y + 10), (lw, box_y + box_h - 10), 2)
        pygame.draw.line(self.screen, (255, 255, 255), (hw, box_y + 10), (hw, box_y + box_h - 10), 2)

        box_rect = pygame.Rect(q1x, box_y + 10, q3x - q1x, box_h - 20)
        pygame.draw.rect(self.screen, (100, 200, 255), box_rect)
        pygame.draw.line(self.screen, (255, 0, 0), (medx, box_y + 10), (medx, box_y + box_h - 10), 3)

        # Atípicos
        for o in outliers:
            ox = scale(o)
            pygame.draw.circle(self.screen, (255, 100, 100), (int(ox), box_y + box_h // 2), 6)

        # Leyenda
        legend = [
            f"Q1={q['q1']:.0f}  Mediana={q['median']:.0f}  Q3={q['q3']:.0f}",
            f"IQR={q['q3']-q['q1']:.0f}  Atipicos: {len(outliers)}"
        ]
        for i, line in enumerate(legend):
            text = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (chart_x, box_y + box_h + 15 + i * 20))

    def _draw_correlation(self):
        sessions = self.load_sessions()
        label_x, label_y, key_x, key_y = self.PAIRS[self.pair_index]
        title = self.font.render(f"Relacion: {label_x} vs {label_y}", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))

        xs = []
        ys = []
        for s in sessions:
            try:
                xs.append(float(s[key_x]))
                ys.append(float(s[key_y]))
            except (ValueError, KeyError):
                continue

        if len(xs) < 2:
            msg = self.font.render("Se necesitan al menos 2 sesiones", True, (200, 200, 200))
            self.screen.blit(msg, (40, 110))
            return

        acc = PearsonAccumulator()
        for x, y in zip(xs, ys):
            acc.add(x, y)
        r = acc.correlation()

        # Diagrama de dispersión
        chart_x, chart_y = 80, 110
        chart_w = self.app.width - 160
        chart_h = 280

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        def sx(v):
            if max_x == min_x:
                return chart_x + chart_w / 2
            return chart_x + (v - min_x) / (max_x - min_x) * chart_w

        def sy(v):
            if max_y == min_y:
                return chart_y + chart_h / 2
            return chart_y + chart_h - (v - min_y) / (max_y - min_y) * chart_h

        # Ejes
        pygame.draw.line(self.screen, (255, 255, 255),
                         (chart_x, chart_y + chart_h), (chart_x + chart_w, chart_y + chart_h), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (chart_x, chart_y), (chart_x, chart_y + chart_h), 2)

        for x, y in zip(xs, ys):
            pygame.draw.circle(self.screen, (255, 200, 100), (int(sx(x)), int(sy(y))), 5)

        # Texto de correlación
        interp = "correlacion muy fuerte" if abs(r) > 0.9 else \
                 "correlacion fuerte" if abs(r) > 0.7 else \
                 "correlacion moderada" if abs(r) > 0.4 else "correlacion debil"
        sign = "positiva" if r >= 0 else "negativa"

        lines = [
            f"n = {acc.n}",
            f"r = {r:.5f}",
            f"{interp} {sign}",
            "",
            "Interpretacion: a mayor valor de la primera",
            "variable tiende a observarse un mayor valor",
            "de la segunda, aunque la correlacion no implica",
            "causalidad."
        ]

        for i, line in enumerate(lines):
            text = self.small_font.render(line, True, (200, 230, 255))
            self.screen.blit(text, (chart_x, chart_y + chart_h + 30 + i * 22))

    def draw_quality_overlay(self):
        report = QualityReport("logs").inspect()
        overlay = pygame.Surface((self.app.width, self.app.height))
        overlay.set_alpha(230)
        overlay.fill((10, 10, 20))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("CALIDAD DE DATOS (Q para cerrar)", True, (255, 255, 255))
        self.screen.blit(title, (40, 60))

        lines = str(report).split("\n")
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (200, 230, 255))
            self.screen.blit(text, (60, 110 + i * 30))

        pygame.display.flip()
