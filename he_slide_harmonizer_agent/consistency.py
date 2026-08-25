"""
Cross-Scanner Consistency Scoring for HE Slide Harmonizer Agent.
Compute per-scanner stain uniformity metrics for benchmarking.
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict
import math


@dataclass
class ScannerStats:
    """Per-scanner stain statistics."""
    scanner: str
    h_mean: float
    e_mean: float
    h_cv: float
    e_cv: float
    slide_count: int


def compute_cross_scanner_consistency(slides: list) -> dict:
    """Compute per-scanner mean stain intensity and coefficient of variation.
    Slides list: [{'scanner': str, 'h_intensity': float, 'e_intensity': float}]"""
    scanner_data = defaultdict(lambda: {"h": [], "e": []})
    for s in slides:
        scanner_data[s["scanner"]]["h"].append(s.get("h_intensity", 0))
        scanner_data[s["scanner"]]["e"].append(s.get("e_intensity", 0))

    stats = {}
    for scanner, data in scanner_data.items():
        h_vals = data["h"]
        e_vals = data["e"]
        h_mean = sum(h_vals) / len(h_vals) if h_vals else 0
        e_mean = sum(e_vals) / len(e_vals) if e_vals else 0

        h_stdev = math.sqrt(sum((v - h_mean) ** 2 for v in h_vals) / (len(h_vals) - 1)) if len(h_vals) > 1 else 0
        e_stdev = math.sqrt(sum((v - e_mean) ** 2 for v in e_vals) / (len(e_vals) - 1)) if len(e_vals) > 1 else 0

        h_cv = (h_stdev / h_mean * 100) if h_mean > 0 else 0
        e_cv = (e_stdev / e_mean * 100) if e_mean > 0 else 0

        stats[scanner] = {
            "h_mean": round(h_mean, 2),
            "e_mean": round(e_mean, 2),
            "h_cv": round(h_cv, 1),
            "e_cv": round(e_cv, 1),
            "slide_count": len(h_vals),
        }

    all_cvs = [s["h_cv"] + s["e_cv"] for s in stats.values()]
    consistency_score = 100 - (sum(all_cvs) / len(all_cvs) if all_cvs else 0)
    outlier_scanners = [k for k, v in stats.items() if v["h_cv"] > 15 or v["e_cv"] > 15]

    return {
        "scanner_stats": stats,
        "consistency_score": round(max(0, consistency_score), 1),
        "outlier_scanners": outlier_scanners,
        "total_scanners": len(stats),
        "total_slides": len(slides),
    }


class ConsistencyTracker:
    """Track cross-scanner consistency over time."""

    def __init__(self):
        self.history: List[dict] = []

    def record_consistency(self, slides: list) -> dict:
        result = compute_cross_scanner_consistency(slides)
        self.history.append(result)
        return result

    def get_trend(self) -> dict:
        if len(self.history) < 2:
            return {"trend": "Insufficient data", "data_points": len(self.history)}

        scores = [h["consistency_score"] for h in self.history]
        recent = scores[-1]
        baseline = scores[0]
        change = recent - baseline

        return {
            "current_score": recent,
            "baseline_score": baseline,
            "change": round(change, 1),
            "trend": "Improving" if change > 2 else "Declining" if change < -2 else "Stable",
            "data_points": len(scores),
        }
