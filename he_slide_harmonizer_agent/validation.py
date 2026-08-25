"""
Stain Vector Validation for HE Slide Harmonizer Agent.
Validate extracted stain vectors against expected ranges for H&E.
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class StainVectorValidation:
    """Validation result for stain vectors."""
    valid: bool
    failures: List[str]
    hematoxylin_vector: List[float]
    eosin_vector: List[float]
    quality_grade: str


class StainVectorValidator:
    """Validate hematoxylin and eosin stain vectors against expected hue ranges."""

    def validate_stain_vectors(self, vectors: dict) -> dict:
        """Validate hematoxylin and eosin vectors against expected hue ranges.
        H: hue 240-270 (blue dominance), E: hue 0-30 (red dominance)."""
        failures = []
        h_vector = vectors.get("hematoxylin", [0, 0, 0])
        e_vector = vectors.get("eosin", [0, 0, 0])

        # Check hematoxylin hue (simplified: check dominant channel is blue)
        if len(h_vector) >= 3:
            if h_vector[2] < h_vector[0] or h_vector[2] < h_vector[1]:
                failures.append("Hematoxylin vector does not show expected blue dominance")

        # Check eosin hue (dominant channel is red)
        if len(e_vector) >= 3:
            if e_vector[0] < e_vector[1] or e_vector[0] < e_vector[2]:
                failures.append("Eosin vector does not show expected red dominance")

        # Check vector magnitude
        h_magnitude = sum(v ** 2 for v in h_vector) ** 0.5
        e_magnitude = sum(v ** 2 for v in e_vector) ** 0.5
        if h_magnitude < 0.1:
            failures.append("Hematoxylin vector magnitude too low; possible staining failure")
        if e_magnitude < 0.1:
            failures.append("Eosin vector magnitude too low; possible staining failure")

        quality = "Excellent" if not failures else "Acceptable" if len(failures) == 1 else "Poor"

        return {
            "valid": len(failures) == 0,
            "failures": failures,
            "hematoxylin_vector": h_vector,
            "eosin_vector": e_vector,
            "quality_grade": quality,
            "h_magnitude": round(h_magnitude, 4),
            "e_magnitude": round(e_magnitude, 4),
        }

    def validate_hematoxylin_eosin_ratio(self, h_intensity: float, e_intensity: float) -> dict:
        """Validate the H/E intensity ratio is within expected bounds."""
        ratio = h_intensity / e_intensity if e_intensity > 0 else float("inf")
        if 0.3 <= ratio <= 3.0:
            status = "Normal"
        elif ratio < 0.3:
            status = "Eosin-dominant; possible over-counterstain"
        else:
            status = "Hematoxylin-dominant; possible over-staining"

        return {
            "h_intensity": h_intensity,
            "e_intensity": e_intensity,
            "ratio": round(ratio, 3),
            "status": status,
            "acceptable": 0.3 <= ratio <= 3.0,
        }
