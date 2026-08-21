from pathlib import Path

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
        "allowed_designs": ["fixed_effects", "did", "event_study", "ddd", "iv", "rdd"],
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
