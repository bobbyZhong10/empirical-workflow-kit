import os
from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def normalized_markdown_bullets(body):
    bullets = []
    current = []
    for line in body.splitlines():
        if line.startswith("- "):
            if current:
                bullets.append(" ".join(" ".join(current).split()))
            current = [line[2:]]
        elif current and (line.startswith("  ") or not line.strip()):
            if line.strip():
                current.append(line.strip())
        elif current:
            bullets.append(" ".join(" ".join(current).split()))
            current = []
    if current:
        bullets.append(" ".join(" ".join(current).split()))
    return bullets


def test_portable_research_contract():
    assert (ROOT / "RESEARCH_PROTOCOL.md").is_file()
    assert (ROOT / "research.example.yaml").is_file()
    body = read("RESEARCH_PROTOCOL.md")
    headings = (
        "## Purpose and scope",
        "## Source of truth and handoff",
        "## Roles",
        "## Authority levels",
        "## Mandatory pause",
        "## Stage interface",
        "## Checkpoints",
        "## Specification discipline",
        "## Runtime parity",
        "## Language",
        "## Delivery contract",
        "## Evidence records",
        "## Independent review",
    )
    assert [body.index(heading) for heading in headings] == sorted(
        body.index(heading) for heading in headings
    )
    normalized_body = " ".join(body.split())
    assert "portable operating contract" in normalized_body
    for phrase in (
        "Executor",
        "Copilot",
        "Quality auditor",
        "research.yaml",
        "decision-log.md",
        "Evidence card",
        "material design change",
        "failed identifying diagnostic",
        "post-result specification",
        "external publication or submission",
        "Raw data is never overwritten",
        "Research scripts are numbered and direct",
        "main specification",
        "estimation sample",
        "clustering level",
        "identifying strategy",
        "recorded decision before execution",
    ):
        assert phrase in normalized_body


def test_v21_spec_has_per_evaluation_post_hoc_and_figure_revalidation():
    body = read("docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md")
    assert "first_formal_batch_at" in body
    assert "target: {kind: claim_revision | reported_figure, id: ...}" in body
    assert "Checkpoint C reports post-hoc evaluations" in body


def test_v21_spec_locks_moot_live_support_inapplicability_and_semantic_coverage():
    body = read("docs/superpowers/specs/2026-08-15-claim-governance-v2.1-design.md")
    normalized = " ".join(body.split())
    assert "`moot` is derived only when an object to which the gate applies enters" in normalized
    assert '"live" means not withdrawn. Stale relations remain live' in normalized
    assert "`inapplicable` requires `applicability_reason`, `declared_by`, and `accepted_by`" in normalized
    assert "every used field must have exactly one valid semantic revision" in normalized


def test_writing_strength_types_publish_and_route_conditional_fields():
    design = read("docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md")
    types = design.split("## Type before strength", 1)[1].split(
        "## Assertion-site registry", 1
    )[0]
    normalized_types = " ".join(types.split())
    assert "Assertion type is prior to tier" in normalized_types
    assert "A tier is meaningful only when `assertion_type: world`" in normalized_types
    for assertion_type in (
        "world",
        "negative",
        "methodological",
        "discriminating",
        "model_internal",
    ):
        assert f"| `{assertion_type}` |" in types
    assert "`hypothesis` is also an accepted `assertion_type` value" in normalized_types
    assert "Every untiered site records `declared_tier: null`" in normalized_types
    assert (
        "requires `power_basis` naming the test, sample size, and minimum "
        "detectable effect" in normalized_types
    )
    assert "`rule out` is prohibited" in normalized_types
    methodological_row = next(
        " ".join(line.split())
        for line in types.splitlines()
        if line.startswith("| `methodological` |")
    )
    assert methodological_row == (
        "| `methodological` | A statement whose object is an estimator or method. "
        "It is untiered and excluded from empirical-strength summaries. |"
    )
    assert "must register that alternative explanation" in normalized_types
    assert "Low lexical strength is normal" in normalized_types
    assert "requires `as_modeled: true`" in normalized_types
    assert (
        "may use `significant` only when "
        "`underlying_precision.has_sampling_distribution` is true" in normalized_types
    )

    interface = design.split("## Assertion-site registry", 1)[1].split(
        "## Declaration and lexical enforcement", 1
    )[0]
    normalized_interface = " ".join(interface.split())
    for yaml_field in (
        "assertion_type: world",
        "declared_tier: T1",
        "qualifier_scope: sentence",
        "counterevidence_prominence: null",
        "underlying_precision:",
        "scope_declaration: null",
        "power_basis: null",
        "upgrade_justification: null",
        "alternative_explanation: null",
        "as_modeled: null",
    ):
        assert yaml_field in interface
    assert (
        "`qualifier_scope`: `sentence | paragraph | section | cross_reference`"
        in normalized_interface
    )
    assert (
        "`counterevidence_prominence`: `parenthetical | clause_appended | "
        "separate_contrastive_sentence | footnote | appendix`" in normalized_interface
    )
    assert (
        "an object containing `significant_at`, `has_sampling_distribution`, "
        "`n`, and `estimate_id`" in normalized_interface
    )
    assert (
        "`scope_declaration`: `null` for sentence scope; otherwise a mapping"
        in normalized_interface
    )
    assert "`power_basis`: required for `negative`, `null` for other types" in normalized_interface
    assert (
        "`upgrade_justification`: required when a `world` site's `declared_tier` "
        "is stronger than the same claim's results-site `declared_tier`"
        in normalized_interface
    )
    assert "`alternative_explanation`: required for `discriminating`" in normalized_interface
    assert "`null` or absent for every other type" in normalized_interface
    assert (
        "`as_modeled`: required with the literal value `true` for `model_internal`"
        in normalized_interface
    )
    assert "`null` or absent for all other types" in normalized_interface

    writing = read("skills/empirical-workflow/stages/stage7-writing.md")
    routed = " ".join(
        writing.split("## Automatic actions", 1)[1].split("## Required artifacts", 1)[0].split()
    )
    for field in (
        "`assertion_type`",
        "`declared_tier`",
        "`qualifier_scope`",
        "`counterevidence_prominence`",
        "`underlying_precision`",
        "`scope_declaration`",
        "`power_basis`",
        "`upgrade_justification`",
        "`alternative_explanation`",
        "`as_modeled`",
    ):
        assert field in routed
    assert "`alternative_explanation` only for discriminating sites" in routed
    assert "`as_modeled: true` only for model-internal sites" in routed
    assert "Compare `declared_tier` only among `world` sites for upgrade traces" in routed
    assert "untiered sites are excluded" in routed


def test_writing_strength_world_ladder_and_residual_severities():
    design = read("docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md")
    ladder = design.split("### World-only ladder", 1)[1].split(
        "## Assertion-site registry", 1
    )[0]
    assert [ladder.index(f"| `T{tier}` |") for tier in range(5)] == sorted(
        ladder.index(f"| `T{tier}` |") for tier in range(5)
    )
    for row in (
        "| `T0` | An unqualified causal commitment | 4 |",
        "| `T1` | A causal commitment constrained by a registered scope qualifier | 3 |",
        "| `T2` | A causal commitment accompanied by material counterevidence | 2 |",
        "| `T3` | Association, interpretation, or consistency with an account | 1 |",
        "| `T4` | Description without an effect or causal commitment | 0 |",
    ):
        assert row in ladder

    residual = design.split("## Residual rule", 1)[1].split(
        "## Cross-site checks", 1
    )[0]
    normalized = " ".join(residual.split())
    assert "overclaim_residual = lexical_tier_strength - evidence_strength" in normalized
    for evidence_input in (
        "claim assessment",
        "revision_reason: bounded_by_*",
        "gate status",
        "provenance",
        "underlying_precision",
    ):
        assert evidence_input in normalized
    assert "`overclaim_residual > 0` emits blocking `OVERCLAIM_RESIDUAL`" in normalized
    assert "`overclaim_residual < 0` emits informational `UNDERCLAIM_RESIDUAL`" in normalized
    assert "Only `world` sites participate" in normalized
    assert "low-strength language on a `discriminating` site is neutral" in normalized
    assert "Tier compliance is not a separate check" in normalized


def test_writing_strength_checks_bind_rules_codes_and_severities():
    design = read("docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md")
    checks = design.split("## Cross-site checks", 1)[1].split(
        "## Structural-estimation contract", 1
    )[0]
    normalized = " ".join(checks.split())
    assert "`revision_reason: bounded_by_*`" in normalized
    assert "`title`, `abstract`, and `conclusion`" in normalized
    assert "blocking `NARROWING_NOT_PROPAGATED`" in normalized
    assert "An `upgrade_justification` cannot override this finding" in normalized
    assert "at least a `separate_contrastive_sentence`" in normalized
    assert "footnote or appendix placement is insufficient" in normalized
    assert "blocking `COUNTEREVIDENCE_BURIED`" in normalized
    assert "within one sentence" in normalized
    for recovery in ("`However`", "`Nevertheless`", "`Overall`", "`Encouragingly`"):
        assert recovery in checks
    assert "reporting-only `IMMEDIATE_RECOVERY` at WARN level" in normalized
    assert "without a tier reduction" in normalized
    assert "compare `declared_tier` only among `world` assertion sites" in normalized
    assert "Untiered sites never enter this comparison" in normalized
    assert "Lexical drift remains part of declaration/residual strength enforcement" in normalized
    assert "`UPGRADE_TRACE_MISSING` at WARN level" in normalized
    assert "never BLOCK" in normalized
    assert "cannot waive another blocking rule" in normalized
    assert "Strengthening these high-visibility locations is not itself an error" in normalized


def test_writing_strength_scope_scan_structural_and_stage_boundaries():
    design = read("docs/superpowers/specs/2026-08-15-writing-strength-v2.2-design.md")
    interface = design.split("## Assertion-site registry", 1)[1].split(
        "## Declaration and lexical enforcement", 1
    )[0]
    lexical = design.split("## Declaration and lexical enforcement", 1)[1].split(
        "## Residual rule", 1
    )[0]
    normalized_interface = " ".join(interface.split())
    normalized_lexical = " ".join(lexical.split())
    assert "`title` is a first-class section role" in normalized_interface
    assert "coverage is a closed manuscript range" in normalized_interface
    for coverage_field in ("path:", "start_anchor:", "end_anchor:"):
        assert coverage_field in interface
    assert (
        "does not automatically cover an abstract, title, or conclusion site"
        in normalized_interface
    )
    assert (
        "Tier, residual, prominence, and scope are computed there and nowhere else"
        in normalized_lexical
    )
    assert "manuscript_sources" in normalized_lexical
    assert "ASSERTION_SITE_UNREGISTERED" in normalized_lexical
    assert "the failure direction is the safe one" in normalized_lexical
    assert "completeness is unknown rather than reporting success" in normalized_lexical
    for semantic_class in (
        "causal",
        "scope-qualifying",
        "evidential-weak",
        "evidential-moderate",
        "evidential-strong",
        "descriptive",
        "concessive",
    ):
        assert semantic_class in normalized_lexical
    assert "Matching is inflection tolerant" in normalized_lexical
    assert "Evidential frames are **graded**" in normalized_lexical
    assert "project-extensible" in normalized_lexical
    assert (
        "does not create a global banned-word list or prescribe sentence form"
        in normalized_lexical
    )

    structural = read("skills/empirical-workflow/stages/stage6b-structural.md")
    structural_actions = " ".join(
        structural.split("## Automatic actions", 1)[1].split("## Required artifacts", 1)[0].split()
    )
    structural_action_bullets = normalized_markdown_bullets(
        structural.split("## Automatic actions", 1)[1].split("## Required artifacts", 1)[0]
    )
    for rule in (
        "Keep `identified` and `calibrated` lexically distinct",
        "State identification as a property delivered by data variation and a "
        "moment/likelihood component",
        "state calibration as an analyst-authored setting with its fixed value and source",
        "identified → simulated",
        "model_internal",
        "`as_modeled: true`",
        "`underlying_precision.has_sampling_distribution: false`",
    ):
        assert rule in structural_actions
    assert (
        "Register every qualifier governing multiple counterfactuals as a "
        "`scope_declaration` with an explicit manuscript coverage range. A body "
        "declaration does not cover a title, abstract, or conclusion site outside "
        "that range."
    ) in structural_action_bullets
    structural_red_lines = " ".join(
        structural.split("## Red lines", 1)[1].split("## Exit condition", 1)[0].split()
    )
    assert (
        "Never present a simulated model-internal quantity as identified empirical "
        "evidence or use `significant` for it without a sampling distribution"
        in structural_red_lines
    )

    assert " ".join(structural.split("## Exit condition", 1)[1].split()) == " ".join(
        """
        The structural Checkpoint C record shows that every parameter is identified or
        labeled calibrated and sourced; multiple starts and uncertainty are reported;
        targeted and untargeted fit, sensitivity, and reduced-form discipline are
        visible; and each counterfactual has a support boundary. Every claim traces to
        its Evidence card and output.

        ## 6b operating sequence

        1. Lock primitives, parameter statuses, identification table, and estimation
           plan before running the solver.
        2. Estimate from multiple starts; record convergence, targeted and untargeted
           fit, and parameter uncertainty.
        3. Run sensitivity and reduced-form companion checks; return to primitives on
           a material fit failure.
        4. Produce bounded counterfactuals, evidence cards, three-line tables, and the
           structural Checkpoint C record.
        """.split()
    )
    assert (
        "Pause before changing approved primitives, moments, sample, equilibrium, "
        "estimator, or counterfactual after results are observed."
        in " ".join(structural.split())
    )

    writing = read("skills/empirical-workflow/stages/stage7-writing.md")
    writing_actions = " ".join(
        writing.split("## Automatic actions", 1)[1].split("## Required artifacts", 1)[0].split()
    )
    writing_action_bullets = normalized_markdown_bullets(
        writing.split("## Automatic actions", 1)[1].split("## Required artifacts", 1)[0]
    )
    for route in (
        "A positive `overclaim_residual` blocks and a negative residual is INFO",
        "Low lexical strength on a discriminating assertion is neutral",
    ):
        assert route in writing_actions
    assert (
        "Enforce narrowing propagation to title, abstract, and conclusion; disclose "
        "identifying-assumption counterevidence in a separate contrastive sentence "
        "in the main text. Treat immediate recovery and a missing abstract/title "
        "`upgrade_justification` trace as WARN, not blockers. A dedicated limitations "
        "section does not replace disclosure beside the affected claim."
    ) in writing_action_bullets
    assert " ".join(writing.split("## Exit condition", 1)[1].split()) == " ".join(
        """
        The manuscript has complete three-line economics tables, verified citations,
        and a claim-to-evidence audit in which each substantive claim traces to a
        recorded result and limitation. Independent-runtime identification review is
        CLEAR or CONDITIONAL with tracked resolution; no unresolved HOLD remains; and
        the publication decision and remaining limitations are documented.

        ## 7 operating sequence

        1. Assemble evidence-backed sections and tables before drafting the
           introduction and conclusion.
        2. Complete the claim-to-evidence and citation-verification audits, including
           every number in the abstract and introduction.
        3. Run review at the required depth; give the independent runtime the
           identification memo, diagnostic evidence, Evidence cards, and relevant
           manuscript section rather than an executor summary.
        4. Resolve findings, verify cross-references and table order, document the
           publication decision, then apply the outlet formatting adapter.
        """.split()
    )
    assert (
        "External circulation or submission requires the protocol-required recorded "
        "decision."
        in " ".join(writing.split())
    )


def test_example_config_values():
    config = yaml.safe_load(read("research.example.yaml"))
    assert config == {
        "project_name": "example_platform_adoption",
        "target_outlets": ["Management Science", "ISR", "MISQ"],
        "reference_pools": ["UTD24", "FT50", "TopEcon", "JAIS", "IJRM"],
        "research_domain": "platform_and_firm_panel_causal",
        "observation_unit": "firm_quarter",
        "analysis_languages": {"etl": "python", "estimation": "r"},
        "allowed_designs": [
            "fixed_effects",
            "selection_on_observables",
            "did",
            "event_study",
            "ddd",
            "iv",
            "rdd",
            "synthetic_control",
            "field_experiment",
            "conjoint",
        ],
        "autonomy_mode": "complete_with_red_lines",
        "current_stage": "stage_1_data_infrastructure",
        "primary_data_format": "parquet",
        "conversation_language": "Chinese",
        "artifact_language": "English",
        "analysis_input_contract": {
            "data_version": "firm_quarter_v2026_08_15",
            "dataset_path": "data/analysis/firm_quarter.parquet",
            "producing_script": "code/py/04_export.py",
            "time_granularity": "quarter",
            "primary_key": ["firm_id", "year_qtr"],
        },
    }


def test_runtime_adapters_and_records():
    required = (
        "CLAUDE.md", "AGENTS.md",
        "skills/empirical-workflow/templates/decision-log-template.md",
        "skills/empirical-workflow/templates/evidence-card-template.md",
        "skills/empirical-workflow/templates/literature-map-template.md",
    )
    for path in required:
        assert (ROOT / path).is_file()
    for path in ("CLAUDE.md", "AGENTS.md"):
        body = read(path)
        assert "Runtime Adapter" in body
        assert "RESEARCH_PROTOCOL.md" in body
        assert len(body.splitlines()) < 140
        handoff = body.split("## Cross-runtime handoff", maxsplit=1)[1].lower()
        continuation_order = (
            "research_protocol.md",
            "research.yaml",
            "_status.md",
            "relevant current evidence card",
            "decision-log.md",
        )
        assert [handoff.index(item) for item in continuation_order] == sorted(
            handoff.index(item) for item in continuation_order
        )


def test_canonical_validator_uses_the_bootstrapped_interpreter(tmp_path):
    command = ROOT / "tools" / "validate_registry"
    completed = subprocess.run(
        [str(command), "--version"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONNOUSERSITE": "1"},
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "empirical-workflow 2.3"

    canonical = "tools/validate_registry"
    for path in ("AGENTS.md", "CLAUDE.md", "RESEARCH_PROTOCOL.md", "README.md"):
        assert canonical in read(path), path


def test_codex_install_uses_discovered_agents_skill_path():
    for path in ("README.md", "docs/v2-migration-guide.md"):
        body = read(path)
        assert ".agents/skills/empirical-workflow" in body
        assert ".codex/skills/empirical-workflow" not in body


def test_stage_contracts():
    stages = sorted((ROOT / "skills/empirical-workflow/stages").glob("stage*.md"))
    assert len(stages) == 8
    headings = (
        "## Inputs",
        "## Automatic actions",
        "## Required artifacts",
        "## Red lines",
        "## Exit condition",
    )
    for stage in stages:
        body = stage.read_text(encoding="utf-8")
        for heading in headings:
            assert heading in body, f"{stage.name} lacks {heading}"


def test_shared_standards_are_routed_to_producer_and_consumers():
    router = read("skills/empirical-workflow/SKILL.md")
    for reference in ("references/data-contract.md", "references/python-standards.md", "references/r-standards.md"):
        assert reference in router

    stage1 = read("skills/empirical-workflow/stages/stage1-data-infra.md")
    assert "references/python-standards.md" in stage1
    assert "references/data-contract.md" in stage1
    for stage in ("stage5-measurement.md", "stage6a-reduced-form.md", "stage6b-structural.md"):
        body = read(f"skills/empirical-workflow/stages/{stage}")
        assert "references/data-contract.md" in body
        assert "references/r-standards.md" in body


def test_decision_log_is_the_only_append_only_history_and_checkpoints_have_no_waivers():
    status = read("skills/empirical-workflow/templates/status-template.md")
    normalized = " ".join(status.split()).lower()
    assert "decision-log.md is the sole append-only history" in normalized
    assert "## 6. Decision log" not in status
    assert "## 7. Abandoned approaches (append only)" not in status

    governed = "\n".join(
        read(path)
        for path in (
            "RESEARCH_PROTOCOL.md",
            "skills/empirical-workflow/SKILL.md",
            "skills/empirical-workflow/stages/stage3-theory-hypotheses.md",
            "skills/empirical-workflow/stages/stage5-measurement.md",
        )
    ).lower()
    assert "waiver" not in governed


def test_causal_platform_risks_and_traceability():
    tree = read("skills/empirical-workflow/references/identification-decision-tree.md").lower()
    for phrase in ("anticipation", "spillover", "treatment exit", "negative weights"):
        assert phrase in tree
    reduced = read("skills/empirical-workflow/stages/stage6a-reduced-form.md")
    assert "Evidence card" in reduced
    writing = read("skills/empirical-workflow/stages/stage7-writing.md").lower()
    assert "three-line" in writing


def test_data_contract_template():
    path = ROOT / "skills/empirical-workflow/templates/data-contract-template.yaml"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    for key in (
        "project_name:",
        "data_version:",
        "producing_script:",
        "observation_unit:",
        "time_granularity:",
        "primary_key:",
        "row_count:",
        "unit_count:",
        "period_count:",
        "missingness:",
        "merge_rates:",
        "merge_audit:",
    ):
        assert key in body
    contract = yaml.safe_load(body)
    project = yaml.safe_load(read("research.example.yaml"))
    expected_identity = project["analysis_input_contract"]
    assert contract["project_name"] == project["project_name"]
    assert contract["observation_unit"] == project["observation_unit"]
    for key in ("data_version", "dataset_path", "producing_script", "time_granularity"):
        assert contract[key] == expected_identity[key]
    assert contract["primary_key"]["columns"] == expected_identity["primary_key"]
    audit_path = ROOT / "skills/empirical-workflow/templates/merge-audit-template.yaml"
    assert audit_path.is_file()
    audit = yaml.safe_load(audit_path.read_text(encoding="utf-8"))
    assert contract["merge_audit"]["data_version"] == audit["data_version"]
    assert audit["output_dataset"]["path"] == contract["dataset_path"]
    assert audit["output_dataset"]["row_count"] == contract["row_count"]
    step = audit["merge_steps"][0]
    assert step["matched_left_row_count"] + step["unmatched_left_row_count"] == step["left_source"]["input_row_count"]
    assert step["left_match_rate"] == step["matched_left_row_count"] / step["left_source"]["input_row_count"]


def test_r_standards_start_after_python_etl():
    body = read("skills/empirical-workflow/references/r-standards.md")
    contract = read("skills/empirical-workflow/references/data-contract.md")
    assert "01_validate_contract.R" in body
    assert "02_construct.R" in body
    assert "01_ingest.R" not in body
    assert "02_clean.R" not in body
    assert "Python owns raw ingestion, cleaning, entity resolution, and merging." in body
    assert "`code/r/01_validate_contract.R` is the prerequisite" in contract
    assert "before `code/r/02_construct.R`" in contract


def test_smoke_covers_expected_identity_handoff_and_failed_identification():
    runner = read("tests/smoke/run_smoke.sh")
    verifier = read("tests/smoke/verify_panel.R")
    recovery = read("tests/smoke/recover_handoff.py")
    for expected in (
        "handoff-fixture/research.yaml",
        "recover_handoff.py",
        "failed-identification.yaml",
        "Failed identifying diagnostic: formal analysis blocked",
    ):
        assert expected in runner
    for identity in (
        "project_name",
        "data_version",
        "dataset_path",
        "producing_script",
        "observation_unit",
        "time_granularity",
        "primary_key",
    ):
        assert identity in verifier
    assert "READ_ORDER" in recovery
    assert "decision-log.md" in recovery


def test_smoke_environment_preflight_isolated_and_actionable():
    runner = read("tests/smoke/run_smoke.sh")
    bootstrap = read("tests/bootstrap_test_environment.sh")
    ignore = read(".gitignore")
    for module in ("import pyarrow", "import yaml"):
        assert module in runner
    assert "find_spec" not in runner
    for package in ("arrow", "yaml", "fixest", "modelsummary"):
        assert package in runner
        assert package in bootstrap
    for body in (runner, bootstrap):
        assert "print_diagnostic_excerpt" in body
        assert "process_status_message" in body
        assert "terminated by signal" in body
        assert "Rscript --vanilla" in body
    assert "local package_status=$?" in runner
    assert "local package_status=$?" in bootstrap
    assert "verify_r_package" in bootstrap
    assert bootstrap.index("verify_r_package") < bootstrap.index("Repository-local smoke-test environment is ready")
    assert 'registry_command="$repo_root/tools/validate_registry"' in runner
    assert "tools/validate_registry --version" in bootstrap
    assert 'pkg-config --modversion arrow' in bootstrap
    assert 'arrow_${arrow_cpp_version}.tar.gz' in bootstrap
    assert 'ARROW_HOME="$arrow_home" R CMD INSTALL' in bootstrap
    assert ".r-lib/" in ignore


def test_readme_cross_runtime_quickstart():
    body = read("README.md")
    for phrase in (
        "Claude Code",
        "Codex",
        "RESEARCH_PROTOCOL.md",
        "research.yaml",
        "tests/smoke/run_smoke.sh",
    ):
        assert phrase in body


def test_absorbed_global_instructions_are_portably_routed():
    required = (
        "skills/empirical-workflow/references/research-writing.md",
        "skills/empirical-workflow/references/execution-discipline.md",
        "skills/empirical-workflow/references/method-governance.md",
        "skills/empirical-workflow/references/code-review.md",
        "skills/empirical-workflow/templates/handoff-template.md",
        "runtime-profile.example.yaml",
        "THIRD_PARTY_NOTICES.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    protocol = read("RESEARCH_PROTOCOL.md")
    router = read("skills/empirical-workflow/SKILL.md")
    for phrase in (
        "Research judgment and verification",
        "Research writing and source use",
        "Publication, confidentiality, and release",
    ):
        assert phrase in protocol
    for path in required[:4]:
        assert path.removeprefix("skills/empirical-workflow/") in router

    profile = yaml.safe_load(read("runtime-profile.example.yaml"))
    assert profile["runtime_profile"]["scholarly_sources"]["cache_dir"]
    assert profile["runtime_profile"]["presentation"]["assets_path"]
    assert profile["runtime_profile"]["browser"]["public_profile"]
    for name in (
        "EWF_CACHE_DIR",
        "EWF_STATE_DIR",
        "EWF_PDF_HELPER",
        "EWF_PRESENTATION_ASSETS",
        "EWF_COURSE_ROOT",
    ):
        assert name in profile["runtime_profile"]["environment_bindings"]

    for adapter in ("CLAUDE.md", "AGENTS.md"):
        body = read(adapter)
        assert len(body.splitlines()) < 140
        assert "runtime-profile" in body


def test_claim_governance_and_preregistration_are_routed():
    required = (
        "skills/empirical-workflow/templates/governance-registry-template.yaml",
        "skills/empirical-workflow/templates/preregistration-template.yaml",
        "skills/empirical-workflow/scripts/validate_governance.py",
        "skills/preregister/SKILL.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    stage3 = read("skills/empirical-workflow/stages/stage3-theory-hypotheses.md")
    stage5 = read("skills/empirical-workflow/stages/stage5-measurement.md")
    prereg = read("skills/preregister/SKILL.md")
    assert "preregistration-template.yaml" in stage3
    assert "acceptance-gate" in stage5.lower()
    for phrase in (
        "focal outcome",
        "focal analysis",
        "refuse",
        "falsification",
        "retrospective",
    ):
        assert phrase in prereg.lower()

    registry = yaml.safe_load(read(required[0]))
    prereg_template = yaml.safe_load(read(required[1]))
    assert registry["registry_version"]
    assert prereg_template["preregistration"]["outcome_seen"] is False
    assert prereg_template["preregistration"]["focal_analysis_run"] is False


def test_research_source_skills_are_routed_and_honest_about_coverage():
    required = (
        "skills/research-sources/SKILL.md",
        "skills/research-sources/REFERENCE.md",
        "skills/research-sources/scripts/paper.py",
        "skills/literature-review/SKILL.md",
        "skills/bibliography-audit/SKILL.md",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    source_skill = read(required[0]).lower()
    literature_skill = read(required[3]).lower()
    bibliography_skill = read(required[4]).lower()
    stage2 = read("skills/empirical-workflow/stages/stage2-lit-map.md")
    stage7 = read("skills/empirical-workflow/stages/stage7-writing.md")

    for phrase in ("version_read", "source_rung", "abstract only", "coverage"):
        assert phrase in source_skill
    assert "source coverage" in literature_skill
    assert "never overwrites" in bibliography_skill
    assert "metadata" in bibliography_skill and "claim support" in bibliography_skill
    assert "literature-review" in stage2 and "bibliography-audit" in stage2
    assert "bibliography-audit" in stage7

    portable_files = required + (
        "skills/empirical-workflow/stages/stage2-lit-map.md",
        "skills/empirical-workflow/stages/stage7-writing.md",
    )
    for path in portable_files:
        assert "~/.claude" not in read(path)


def test_method_specific_causal_packs_are_selectively_routed():
    methods_root = ROOT / "skills/empirical-workflow/methods"
    expected = (
        "causal-design",
        "fixed-effects",
        "selection-on-observables",
        "did",
        "iv",
        "rdd",
        "synthetic-control",
        "field-experiment",
        "conjoint",
    )
    for method in expected:
        pack = methods_root / method
        for name in ("prompt.md", "canon.md", "details.md", "template.R"):
            assert (pack / name).is_file(), f"{method} lacks {name}"
        prompt = (pack / "prompt.md").read_text(encoding="utf-8")
        canon = (pack / "canon.md").read_text(encoding="utf-8")
        assert "8958cc246e65cdf7c36604f397a1c1719b7e2c14" in prompt
        for phrase in (
            "Current as of",
            "Verified through",
            "Role:",
            "Settles:",
            "Binds when:",
            "Implement:",
            "Scope limits:",
            "Named disagreements:",
            "Excluded:",
        ):
            assert phrase in canon, f"{method} canon lacks {phrase}"

    config = yaml.safe_load(read("research.example.yaml"))
    for design in (
        "selection_on_observables",
        "synthetic_control",
        "field_experiment",
        "conjoint",
    ):
        assert design in config["allowed_designs"]

    stage = read("skills/empirical-workflow/stages/stage6a-reduced-form.md")
    tree = read("skills/empirical-workflow/references/identification-decision-tree.md")
    assert "methods/<selected-method>/prompt.md" in stage
    assert "Load only the selected method pack" in stage
    for method in expected:
        assert f"methods/{method}/prompt.md" in tree


def test_review_response_and_replication_release_are_governed():
    skills = (
        "skills/research-council/SKILL.md",
        "skills/manuscript-review/SKILL.md",
        "skills/referee-response/SKILL.md",
        "skills/replication-release/SKILL.md",
    )
    templates = (
        "skills/empirical-workflow/templates/review-finding-template.yaml",
        "skills/empirical-workflow/templates/response-matrix-template.yaml",
        "skills/empirical-workflow/templates/replication-checklist-template.md",
    )
    scanners = tuple(
        f"skills/replication-release/scripts/{name}.py"
        for name in ("scan_headers", "scan_values", "scan_qsf", "sample_open_text")
    )
    for path in skills + templates + scanners:
        assert (ROOT / path).is_file(), path

    council = read(skills[0]).lower()
    response = read(skills[2]).lower()
    release = read(skills[3]).lower()
    stage7 = read("skills/empirical-workflow/stages/stage7-writing.md")
    assert "never by vote count" in council
    assert "verify every pin" in response
    assert "confidential" in release
    assert "policy" in release and "current" in release
    assert "staging" in release and "never" in release and "source" in release
    for name in ("research-council", "manuscript-review", "referee-response", "replication-release"):
        assert name in stage7

    finding = yaml.safe_load(read(templates[0]))
    response_matrix = yaml.safe_load(read(templates[1]))
    assert finding["finding"]["severity"]
    assert response_matrix["comments"][0]["pin_verification"]["verified"] is False


def test_latex_and_presentation_production_are_portable():
    skill_roots = (
        "skills/latex-production",
        "skills/research-talk",
        "skills/teaching-lecture",
        "skills/slide-review",
        "skills/course-site",
    )
    for root in skill_roots:
        body = read(f"{root}/SKILL.md")
        assert "8958cc246e65cdf7c36604f397a1c1719b7e2c14" in body
        assert "runtime-profile.yaml" in body
    required = (
        "agents/tikz-reviewer.md",
        "presentation-tooling/README.md",
        "presentation-tooling/_extensions/starter/_extension.yml",
        "presentation-tooling/_extensions/starter/stage-slide.lua",
        "presentation-tooling/_extensions/starter/starter-theme.scss",
        "presentation-tooling/deck-check.mjs",
        "presentation-tooling/stage-check.mjs",
        "presentation-tooling/check-offline.py",
        "skills/slide-review/scripts/probe.js",
        "skills/slide-review/scripts/figure-ground.js",
    )
    for path in required:
        assert (ROOT / path).is_file(), path

    text_suffixes = {".md", ".py", ".js", ".mjs", ".lua", ".qmd", ".scss", ".yml"}
    roots = [ROOT / path for path in skill_roots] + [ROOT / "presentation-tooling", ROOT / "agents"]
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in text_suffixes:
                body = path.read_text(encoding="utf-8", errors="replace")
                assert "~/.claude" not in body, path
                assert "/Users/" not in body, path


def test_documentation_maps_full_absorbed_workflow():
    bodies = [read("README.md"), read("docs/v2-migration-guide.md")]
    combined = "\n".join(bodies)
    for name in (
        "research-sources",
        "literature-review",
        "bibliography-audit",
        "preregister",
        "research-council",
        "manuscript-review",
        "referee-response",
        "replication-release",
        "latex-production",
        "research-talk",
        "teaching-lecture",
        "slide-review",
        "course-site",
    ):
        assert name in combined
    for phrase in (
        "runtime-profile.yaml",
        "THIRD_PARTY_NOTICES.md",
        "governance registry",
        "method pack",
        "policy verification",
        "confidentiality",
    ):
        assert phrase in combined
    assert "research-sources → literature-review → preregister" in combined
    assert "manuscript-review → referee-response → replication-release" in combined
