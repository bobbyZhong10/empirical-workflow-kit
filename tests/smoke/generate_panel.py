"""Generate a deterministic panel and complete Python-to-R handoff contract."""

from __future__ import annotations

import hashlib
import random
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import yaml


ROOT = Path(__file__).resolve().parents[2]
SMOKE_DIR = ROOT / "tests" / "smoke"
DATA_VERSION = "smoke_panel_v2026_08_15"
QUARTERS = ["2024Q1", "2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]
COHORTS = (3, 4, 5, 6)
NEVER_TREATED_COHORT = 1000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_yaml(path: Path, value: dict) -> None:
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


def build_rows() -> list[dict[str, object]]:
    rng = random.Random(20260815)
    rows: list[dict[str, object]] = []
    firm_cohorts = [cohort for cohort in COHORTS for _ in range(2)] + [NEVER_TREATED_COHORT] * 4

    for firm_number, cohort in enumerate(firm_cohorts, start=1):
        firm_effect = (firm_number - 6.5) * 0.2
        for quarter_index, year_qtr in enumerate(QUARTERS, start=1):
            treated = int(cohort != NEVER_TREATED_COHORT and quarter_index >= cohort)
            event_time = quarter_index - cohort if cohort != NEVER_TREATED_COHORT else -99
            quarter_effect = (quarter_index - 4.5) * 0.1
            treatment_effect = 1.25 * treated + 0.08 * max(event_time, 0)
            outcome = round(10 + firm_effect + quarter_effect + treatment_effect + rng.normalvariate(0, 0.25), 6)
            rows.append(
                {
                    "firm_id": f"firm_{firm_number:02d}",
                    "year_qtr": year_qtr,
                    "treated": treated,
                    "event_time": event_time,
                    "outcome": outcome,
                    "cohort": cohort,
                    "quarter_index": quarter_index,
                }
            )
    return rows


def main() -> None:
    project_config_path = SMOKE_DIR / "handoff-fixture" / "research.yaml"
    project_config = yaml.safe_load(project_config_path.read_text(encoding="utf-8"))
    expected_identity = project_config["analysis_input_contract"]
    assert project_config["project_name"] == "smoke_panel_handoff"
    assert project_config["observation_unit"] == "firm-quarter"
    assert expected_identity == {
        "data_version": DATA_VERSION,
        "dataset_path": "tests/smoke/panel.parquet",
        "producing_script": "tests/smoke/generate_panel.py",
        "time_granularity": "quarter",
        "primary_key": ["firm_id", "year_qtr"],
    }

    rows = build_rows()
    assert len(rows) == 96
    assert len({(row["firm_id"], row["year_qtr"]) for row in rows}) == 96

    parquet_path = SMOKE_DIR / "panel.parquet"
    audit_dir = SMOKE_DIR / "audits"
    audit_path = audit_dir / f"{DATA_VERSION}.merge-audit.yaml"
    contract_path = SMOKE_DIR / "panel-contract.yaml"
    invalid_contract_path = SMOKE_DIR / "invalid-contract.yaml"
    invalid_identity_contract_path = SMOKE_DIR / "invalid-identity-contract.yaml"
    audit_dir.mkdir(parents=True, exist_ok=True)

    table = pa.table(
        {
            "firm_id": pa.array([row["firm_id"] for row in rows], type=pa.string()),
            "year_qtr": pa.array([row["year_qtr"] for row in rows], type=pa.string()),
            "treated": pa.array([row["treated"] for row in rows], type=pa.int32()),
            "event_time": pa.array([row["event_time"] for row in rows], type=pa.int32()),
            "outcome": pa.array([row["outcome"] for row in rows], type=pa.float64()),
            "cohort": pa.array([row["cohort"] for row in rows], type=pa.int32()),
            "quarter_index": pa.array([row["quarter_index"] for row in rows], type=pa.int32()),
        }
    )
    pq.write_table(table, parquet_path)

    audit = {
        "data_version": DATA_VERSION,
        "produced_at_utc": "2026-08-15T00:00:00Z",
        "producing_script": "tests/smoke/generate_panel.py",
        "output_dataset": {"path": "tests/smoke/panel.parquet", "row_count": len(rows)},
        "merge_steps": [
            {
                "merge_name": "simulated_firms_to_treatment_schedule",
                "join_type": "left",
                "left_source": {"name": "simulated_firms", "version": "2026-08-15", "input_row_count": 12},
                "right_source": {"name": "simulated_treatment_schedule", "version": "2026-08-15", "input_row_count": 12},
                "matched_left_row_count": 12,
                "unmatched_left_row_count": 0,
                "left_match_rate": 1.0,
                "output_row_count": len(rows),
                "unmatched_disposition": "No unmatched simulated firms.",
            }
        ],
    }
    write_yaml(audit_path, audit)

    contract = {
        "project_name": project_config["project_name"],
        "data_version": DATA_VERSION,
        "produced_at_utc": "2026-08-15T00:00:00Z",
        "producing_script": "tests/smoke/generate_panel.py",
        "dataset_path": "tests/smoke/panel.parquet",
        "data_hash": {"algorithm": "sha256", "value": sha256(parquet_path)},
        "source_versions": [{"source": "simulated_panel", "version": "2026-08-15", "retrieved_at_utc": "2026-08-15T00:00:00Z"}],
        "observation_unit": project_config["observation_unit"],
        "time_granularity": expected_identity["time_granularity"],
        "primary_key": {"columns": expected_identity["primary_key"], "is_unique": True, "duplicate_row_count": 0},
        "row_count": len(rows),
        "unit_count": {"field": "firm_id", "value": 12},
        "period_count": {"field": "year_qtr", "value": 8},
        "required_fields": ["firm_id", "year_qtr", "treated", "event_time", "outcome", "cohort", "quarter_index"],
        "field_types": {
            "firm_id": "string",
            "year_qtr": "string",
            "treated": "integer",
            "event_time": "integer",
            "outcome": "float",
            "cohort": "integer",
            "quarter_index": "integer",
        },
        "missingness": {field: {"count": 0, "share": 0.0} for field in table.column_names},
        "value_ranges": {
            "treated": {"minimum": 0, "maximum": 1},
            "event_time": {"minimum": -99, "maximum": 5},
            "cohort": {"minimum": 3, "maximum": NEVER_TREATED_COHORT},
            "quarter_index": {"minimum": 1, "maximum": 8},
            "year_qtr": {"allowed_pattern": "^[0-9]{4}Q[1-4]$"},
        },
        "merge_audit": {
            "path": "tests/smoke/audits/smoke_panel_v2026_08_15.merge-audit.yaml",
            "data_version": DATA_VERSION,
            "data_hash": {"algorithm": "sha256", "value": sha256(audit_path)},
        },
        "merge_rates": [
            {
                "merge_name": "simulated_firms_to_treatment_schedule",
                "left_row_count": 12,
                "matched_row_count": 12,
                "match_rate": 1.0,
                "unmatched_left_row_count": 0,
                "unmatched_disposition": "No unmatched simulated firms.",
            }
        ],
    }
    write_yaml(contract_path, contract)

    invalid_contract = dict(contract)
    invalid_contract["row_count"] = 95
    write_yaml(invalid_contract_path, invalid_contract)

    invalid_identity_contract = dict(contract)
    invalid_identity_contract["project_name"] = "wrong_project"
    write_yaml(invalid_identity_contract_path, invalid_identity_contract)


if __name__ == "__main__":
    main()
