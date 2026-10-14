class PearsonAccumulator:
    def __init__(self):
        self.n = 0
        self.sum_x = 0.0
        self.sum_y = 0.0
        self.sum_x2 = 0.0
        self.sum_y2 = 0.0
        self.sum_xy = 0.0

    def add(self, x, y):
        x = float(x)
        y = float(y)
        self.n += 1
        self.sum_x += x
        self.sum_y += y
        self.sum_x2 += x * x
        self.sum_y2 += y * y
        self.sum_xy += x * y

    def correlation(self):
        if self.n < 2:
            return 0.0
        numerator = self.n * self.sum_xy - self.sum_x * self.sum_y
        denominator = (
            (self.n * self.sum_x2 - self.sum_x ** 2) *
            (self.n * self.sum_y2 - self.sum_y ** 2)
        ) ** 0.5
        if denominator == 0:
            return 0.0
        return numerator / denominator
