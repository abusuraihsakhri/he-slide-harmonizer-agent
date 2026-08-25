"""
Stain Intensity Reference Target for HE Slide Harmonizer Agent.
Establish gold-standard reference stain distributions and equalize slides to match.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import math


@dataclass
class ReferenceTarget:
    """Reference stain intensity distribution."""
    reference_h_mean: List[float]
    reference_e_mean: List[float]
    slide_count: int
    organ: str = "unknown"
    scanner: str = "unknown"


class StainReferenceAgent:
    """Manage reference stain distributions for harmonization."""

    def __init__(self):
        self.reference_library: Dict[str, ReferenceTarget] = {}

    def compute_reference_target(self, slides: list, organ: str = "unknown", scanner: str = "unknown") -> dict:
        """Compute reference stain intensity distribution from curated gold-standard slides."""
        h_stacks = [s["histogram_h"] for s in slides if "histogram_h" in s]
        e_stacks = [s["histogram_e"] for s in slides if "histogram_e" in s]

        if not h_stacks or not e_stacks:
            return {"error": "No valid histogram data", "slide_count": 0}

        # Compute mean histogram across slides
        h_len = min(len(h) for h in h_stacks)
        e_len = min(len(e) for e in e_stacks)
        h_mean = [sum(h[i] for h in h_stacks) / len(h_stacks) for i in range(h_len)]
        e_mean = [sum(e[i] for e in e_stacks) / len(e_stacks) for i in range(e_len)]

        key = f"{scanner}_{organ}"
        target = ReferenceTarget(
            reference_h_mean=h_mean,
            reference_e_mean=e_mean,
            slide_count=len(slides),
            organ=organ,
            scanner=scanner,
        )
        self.reference_library[key] = target

        return {
            "reference_h_mean": h_mean,
            "reference_e_mean": e_mean,
            "slide_count": len(slides),
            "organ": organ,
            "scanner": scanner,
            "library_key": key,
        }

    def get_reference(self, scanner: str, organ: str) -> Optional[dict]:
        key = f"{scanner}_{organ}"
        target = self.reference_library.get(key)
        if not target:
            return None
        return {
            "reference_h_mean": target.reference_h_mean,
            "reference_e_mean": target.reference_e_mean,
            "slide_count": target.slide_count,
            "organ": target.organ,
            "scanner": target.scanner,
        }

    def compute_color_distance(self, hist1: List[float], hist2: List[float]) -> float:
        """Compute Euclidean distance between two histograms."""
        if len(hist1) != len(hist2):
            min_len = min(len(hist1), len(hist2))
            hist1 = hist1[:min_len]
            hist2 = hist2[:min_len]
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(hist1, hist2)))

    def assess_harmonization_need(self, slide_histogram_h: List[float], slide_histogram_e: List[float],
                                    scanner: str, organ: str) -> dict:
        """Assess whether a slide needs harmonization based on reference distance."""
        ref = self.get_reference(scanner, organ)
        if not ref:
            return {"needs_harmonization": True, "reason": "No reference available", "distance": -1}

        h_dist = self.compute_color_distance(slide_histogram_h, ref["reference_h_mean"])
        e_dist = self.compute_color_distance(slide_histogram_e, ref["reference_e_mean"])
        total_dist = h_dist + e_dist

        return {
            "needs_harmonization": total_dist > 5.0,
            "h_distance": round(h_dist, 3),
            "e_distance": round(e_dist, 3),
            "total_distance": round(total_dist, 3),
            "severity": "High" if total_dist > 10 else "Moderate" if total_dist > 5 else "Low",
        }
