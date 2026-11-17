import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.simulate_sdtm_datasets import simulate
from src.validation_rules import run_validation, build_rules
from src.validation_summary import summarize_validation
from src.resolution_timing import compare_resolution_time


def test_exactly_25_rules_defined():
    data = simulate()
    rules = build_rules(data["dm"], data["ae"], data["lb"])
    assert len(rules) == 25


def test_validation_catches_most_discrepancies_per_domain():
    data = simulate()
    flags = run_validation(data["dm"], data["ae"], data["lb"])
    summary = summarize_validation(flags, data["true_discrepancies"])
    for domain, r in summary["per_domain"].items():
        assert r["recall_pct"] >= 80.0, f"{domain}: {r}"


def test_three_domains_simulated():
    data = simulate()
    assert set(["dm", "ae", "lb"]).issubset(data.keys())
    assert len(data["dm"]) == 500


def test_automated_scan_is_faster_than_manual():
    data = simulate()
    timing = compare_resolution_time(data["dm"], data["ae"], data["lb"])
    assert timing["automated_time_sec"] < timing["manual_time_sec"]


def test_ae_date_order_rule_only_flags_genuine_violations():
    data = simulate()
    flags = run_validation(data["dm"], data["ae"], data["lb"])
    domain, idx_set = flags["ae_end_before_start"]
    ae = data["ae"]
    for idx in idx_set:
        assert ae.loc[idx, "AEENDTC"] < ae.loc[idx, "AESTDTC"]
