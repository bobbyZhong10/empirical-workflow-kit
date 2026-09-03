import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/research-sources/scripts/paper.py"


def load_module():
    spec = importlib.util.spec_from_file_location("research_sources_paper", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_title_normalization_removes_punctuation_and_latex_braces():
    paper = load_module()
    assert paper._norm_title("The {Value} of A.I.: Evidence!") == "the value of a i evidence"


def test_identity_keys_prefer_doi_then_arxiv_then_title():
    paper = load_module()
    record = {
        "doi": "https://doi.org/10.1000/ABC",
        "arxiv_id": "2401.12345v2",
        "title": "A Test Paper",
    }
    assert paper._dedupe_keys(record) == [
        "doi:10.1000/abc",
        "arxiv:2401.12345",
        "title:a test paper",
    ]


def test_absorb_merges_sources_and_citation_counts_without_erasing_values():
    paper = load_module()
    target = {
        "title": "Paper",
        "sources": ["openalex"],
        "citations": {"openalex": 10},
        "doi": "10.1/x",
    }
    source = {
        "title": "Paper",
        "sources": ["semanticscholar"],
        "citations": {"semanticscholar": 12},
        "abstract": "Abstract",
        "doi": None,
    }
    paper._absorb(target, source)
    assert target["sources"] == ["openalex", "semanticscholar"]
    assert target["citations"] == {"openalex": 10, "semanticscholar": 12}
    assert target["doi"] == "10.1/x"
    assert target["abstract"] == "Abstract"


def test_section_selection_preserves_preamble_macros():
    paper = load_module()
    tex = r"""\newcommand{\ATE}{ATE}
\begin{document}
\section{Introduction}
Intro.
\section{Identification}
The \ATE is identified.
\section{Conclusion}
End.
\end{document}
"""
    selected = paper.pick_section(tex, "identification")
    assert r"\newcommand{\ATE}{ATE}" in selected
    assert r"\section{Identification}" in selected
    assert r"\section{Conclusion}" not in selected


def test_abstract_only_page_is_not_classified_as_full_text():
    paper = load_module()
    short_page = "# Abstract\n" + ("brief result " * 80)
    assert paper.classify_page(short_page) == "abstract-only"
