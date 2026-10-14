import math
from statistics_engine.descriptives import OnePassStats

def _median_sorted(sorted_data):
    n = len(sorted_data)
    if n == 0:
        return 0.0
    if n % 2 == 1:
        return sorted_data[n // 2]
    return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2.0


def quartiles(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 0:
        return {"median": 0.0, "q1": 0.0, "q3": 0.0}

    median = _median_sorted(sorted_data)

    if n % 2 == 0:
        lower = sorted_data[: n // 2]
        upper = sorted_data[n // 2 :]
    else:
        lower = sorted_data[: n // 2]
        upper = sorted_data[n // 2 + 1 :]

    return {
        "median": median,
        "q1": _median_sorted(lower),
        "q3": _median_sorted(upper),
    }


def iqr(data):
    q = quartiles(data)
    return q["q3"] - q["q1"]


def percentile(data, p):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n == 0:
        return 0.0
    rank = math.ceil(p / 100.0 * n)
    rank = min(rank, n)
    return sorted_data[rank - 1]


def outliers_iqr(data):
    q = quartiles(data)
    iqr_val = q["q3"] - q["q1"]
    lower = q["q1"] - 1.5 * iqr_val
    upper = q["q3"] + 1.5 * iqr_val
    return [x for x in data if x < lower or x > upper]


def outliers_z(data, threshold=3):
    stats = OnePassStats()
    for x in data:
        stats.add(x)
    if stats.std == 0:
        return []
    return [x for x in data if abs((x - stats.mean) / stats.std) > threshold]
