class FrequencyTable:
    def __init__(self):
        self.counts = {}

    def add(self, value):
        self.counts[value] = self.counts.get(value, 0) + 1

    def rows(self):
        total = sum(self.counts.values())
        rows = []
        cumulative = 0.0
        for value in sorted(self.counts.keys()):
            count = self.counts[value]
            relative = count / total if total > 0 else 0.0
            cumulative += relative
            rows.append({
                "value": value,
                "count": count,
                "relative": relative,
                "cumulative": cumulative,
            })
        return rows

    def mode(self):
        if not self.counts:
            return None
        return max(self.counts.items(), key=lambda item: item[1])[0]

    def total(self):
        return sum(self.counts.values())


def histogram(data, k=8):
    values = list(data)
    if not values:
        return []
    values.sort()
    n = len(values)
    min_v = values[0]
    max_v = values[-1]
    if min_v == max_v:
        return [{"low": min_v, "high": max_v, "count": n, "bin": 0}]

    width = (max_v - min_v) / k
    bins = [
        {
            "bin": i,
            "low": min_v + i * width,
            "high": min_v + (i + 1) * width,
            "count": 0,
        }
        for i in range(k)
    ]

    for v in values:
        idx = int((v - min_v) / width)
        if idx >= k:
            idx = k - 1
        bins[idx]["count"] += 1

    return bins
