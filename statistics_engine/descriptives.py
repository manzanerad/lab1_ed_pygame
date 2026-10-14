import math


class OnePassStats:
    def __init__(self):
        self.n = 0
        self.sum = 0.0
        self.mean = 0.0
        self.m2 = 0.0
        self.min = None
        self.max = None

    def add(self, x):
        x = float(x)
        self.n += 1
        self.sum += x

        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.m2 += delta * delta2

        if self.min is None or x < self.min:
            self.min = x
        if self.max is None or x > self.max:
            self.max = x

    @property
    def variance(self):
        if self.n < 2:
            return 0.0
        return self.m2 / (self.n - 1)

    @property
    def std(self):
        return self.variance ** 0.5

    @property
    def cv(self):
        if self.mean == 0:
            return 0.0
        return (self.std / self.mean) * 100

    @property
    def range(self):
        if self.min is None or self.max is None:
            return 0.0
        return self.max - self.min
