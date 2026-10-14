from statistics_engine.descriptives import OnePassStats


def compare_by_difficulty(sessions):
    groups = {"easy": OnePassStats(), "normal": OnePassStats(), "hard": OnePassStats()}

    for s in sessions:
        diff = s.get("difficulty", "unknown")
        if diff in groups:
            groups[diff].add(s.get("score", 0))

    result = {}
    for diff, stats in groups.items():
        result[diff] = {
            "count": stats.n,
            "mean": stats.mean,
            "std": stats.std,
        }

    easy_mean = result.get("easy", {}).get("mean", 0)
    hard_mean = result.get("hard", {}).get("mean", 0)
    if easy_mean != 0:
        result["mean_difference"] = hard_mean - easy_mean
        result["mean_difference_pct"] = (result["mean_difference"] / easy_mean) * 100

    return result
