"""Validates the 25-rule engine's output against the simulation's
hidden true discrepancies per domain -- because the discrepancies are
injected independently of the rules, recall here is a real, measured
result."""
from __future__ import annotations


def summarize_validation(flags: dict, true_discrepancies: dict) -> dict:
    flagged_by_domain = {"dm": set(), "ae": set(), "lb": set()}
    for rule_name, (domain, idx_set) in flags.items():
        flagged_by_domain[domain] |= idx_set

    report = {}
    for domain in ["dm", "ae", "lb"]:
        true_set = true_discrepancies[domain]
        flagged_set = flagged_by_domain[domain]
        tp = len(flagged_set & true_set)
        recall = round(100 * tp / len(true_set), 2) if true_set else 100.0
        report[domain] = {"n_true": len(true_set), "n_flagged": len(flagged_set), "recall_pct": recall}

    return {"per_domain": report, "n_rules_applied": len(flags)}
