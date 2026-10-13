"""Regression tests for audit integrity, cross-platform paths and CSV flags."""
import csv
from pathlib import Path
import pytest
from agents.base import AuditTrail, SecurityException
from cli import _parse_csv_bool, _validate_safe_path
from he_slide_harmonizer_agent.cli import _parse_csv_bool as _clinical_bool
from slide_harmonizer import _parse_csv_bool as _legacy_bool


def test_hmac_tampering_is_rejected():
    trail = AuditTrail(secret_key="fixture-test-secret")
    trail.log("test", "system", "OK", {"status": "SUCCESS"})
    trail.log("test", "system", "NEXT", {"status": "SUCCESS"})
    assert trail.verify_integrity()
    copy = trail.get_trail()
    copy[0]["actor"] = "different"
    assert trail.verify_integrity(), "Callers must not mutate the internal ledger"
    trail.logs[0]["actor"] = "different"
    assert not trail.verify_integrity(), "HMAC must detect modified signed fields"


def test_hmac_current_hash_tampering_is_rejected():
    trail = AuditTrail(secret_key="fixture-test-secret")
    trail.log("test", "system", "OK", {"value": 1})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_path_rejects_windows_absolute_and_sibling_prefix(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert _validate_safe_path("a.csv") == tmp_path / "a.csv"
    with pytest.raises(SecurityException):
        _validate_safe_path("C:/Windows/system.ini")
    with pytest.raises(SecurityException):
        _validate_safe_path(str(tmp_path.parent / (tmp_path.name + "_sibling") / "out.csv"))
    with pytest.raises(SecurityException):
        _validate_safe_path("../escape.csv")


@pytest.mark.parametrize("value, expected", [
    ("TRUE", True), (" yes ", True), ("1", True), ("false", False),
    ("NO", False), ("0", False), ("", False), (True, True), (False, False)
])
def test_csv_boolean_values(value, expected):
    for parse in (_parse_csv_bool, _clinical_bool, _legacy_bool):
        assert parse(value) is expected


def test_invalid_csv_boolean_is_rejected():
    for parse in (_parse_csv_bool, _clinical_bool, _legacy_bool):
        with pytest.raises(ValueError):
            parse("maybe")


def test_batch_reads_bundled_sample_style(tmp_path, monkeypatch):
    from cli import main
    monkeypatch.chdir(tmp_path)
    sample = tmp_path / "sample.csv"
    sample.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "ONE,SYNTH-01,35,14,False,NORMAL\n"
        "TWO,SYNTH-02,12,4,True,NORMAL\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", "sample.csv", "-o", "out.csv"]) == 0
    with (tmp_path / "out.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]["overall_urgency"] == "ELEVATED_RISK"
    assert rows[1]["overall_urgency"] == "CRITICAL_STAT_PANIC"
