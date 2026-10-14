import unittest
from statistics_engine.descriptives import OnePassStats
from statistics_engine.quartiles import quartiles, iqr, percentile, outliers_iqr, outliers_z
from statistics_engine.correlation import PearsonAccumulator


class TestValidationSet(unittest.TestCase):
    SCORES = [1200, 1500, 1500, 1800, 2100, 2400, 2400, 3000, 3600, 9000]

    def test_descriptives(self):
        stats = OnePassStats()
        for x in self.SCORES:
            stats.add(x)
        self.assertEqual(stats.n, 10)
        self.assertAlmostEqual(stats.sum, 28500.0, places=2)
        self.assertAlmostEqual(stats.mean, 2850.0, places=2)
        self.assertEqual(stats.min, 1200)
        self.assertEqual(stats.max, 9000)
        self.assertAlmostEqual(stats.range, 7800.0, places=2)
        self.assertAlmostEqual(stats.variance, 5205000.0, places=2)
        self.assertAlmostEqual(stats.std, 2281.45, places=2)
        self.assertAlmostEqual(stats.cv, 80.05, places=2)

    def test_quartiles(self):
        q = quartiles(self.SCORES)
        self.assertAlmostEqual(q["median"], 2250.00, places=2)
        self.assertAlmostEqual(q["q1"], 1500.00, places=2)
        self.assertAlmostEqual(q["q3"], 3000.00, places=2)
        self.assertAlmostEqual(iqr(self.SCORES), 1500.00, places=2)
        self.assertAlmostEqual(percentile(self.SCORES, 90), 3600.00, places=2)

    def test_outliers(self):
        self.assertEqual(outliers_iqr(self.SCORES), [9000])
        self.assertEqual(outliers_z(self.SCORES, threshold=3), [])

    def test_pearson(self):
        acc = PearsonAccumulator()
        times = [2, 4, 6, 8, 10, 12]
        scores = [800, 1400, 1900, 2600, 3000, 3700]
        for t, s in zip(times, scores):
            acc.add(t, s)
        self.assertEqual(acc.n, 6)
        self.assertAlmostEqual(acc.sum_x, 42.0, places=2)
        self.assertAlmostEqual(acc.sum_y, 13400.0, places=2)
        self.assertAlmostEqual(acc.sum_xy, 113800.0, places=2)
        self.assertAlmostEqual(acc.correlation(), 0.99834, places=5)


if __name__ == "__main__":
    unittest.main()
