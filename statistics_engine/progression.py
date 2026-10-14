def level_funnel(sessions):
    counts = {}
    for s in sessions:
        level = int(s.get("level", 1))
        counts[level] = counts.get(level, 0) + 1

    if not counts:
        return []

    max_level = max(counts.keys())
    total = sum(counts.values())
    result = []
    previous = None

    for level in range(1, max_level + 1):
        count = counts.get(level, 0)
        survival = (count / total * 100) if total > 0 else 0.0
        abandonment = 0.0
        if previous is not None and previous > 0:
            abandonment = ((previous - count) / previous) * 100
        result.append({
            "level": level,
            "sessions": count,
            "survival": survival,
            "abandonment": abandonment,
        })
        previous = count

    return result
