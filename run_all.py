import json
import os

from src.simulate_sdtm_datasets import simulate
from src.validation_rules import run_validation
from src.validation_summary import summarize_validation
from src.resolution_timing import compare_resolution_time


def main():
    data = simulate()
    dm, ae, lb = data["dm"], data["ae"], data["lb"]

    flags = run_validation(dm, ae, lb)
    summary_report = summarize_validation(flags, data["true_discrepancies"])
    timing = compare_resolution_time(dm, ae, lb)

    summary = {"n_subjects": len(dm), "n_ae_records": len(ae), "n_lb_records": len(lb),
               "validation": summary_report, "resolution_timing": timing}

    os.makedirs("results", exist_ok=True)
    with open("results/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
