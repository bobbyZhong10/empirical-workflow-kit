# Evidence card: Management Science template update

- Batch identifier: kit-mnsc-template-2026-10-04
- Producer runtime: Codex
- Created at: 2026-10-04
- Claim supported: The kit contains the supplied June 2024 template, and its Stage 7 installation compiles.
- Source artifact: Supplied June 2024 template distribution; repository copy in `Template_for_Management_Science_Journal/`.
- Output paths: `Template_for_Management_Science_Journal/`, `skills/empirical-workflow/references/latex-manuscript-adapter.md`.
- Method: Compared the names and SHA-256 content of all 12 supplied files with the kit copy. Copied the adapter-listed files into an isolated `paper/` directory, then built `manuscript.tex` with the manifest-named runtime CLI and configured `latexmk`.
- Observation: All 12 files matched byte for byte. `latexmk` exited 0 and generated a six-page PDF. The build log had no fatal errors; it reported font size substitutions and one oversized sample float (27.14 pt).
- Inference: The new template and its listed dependencies are sufficient for a local PDF build in the tested environment.
- Limitations: The supplied `informs4.cls` contains marked `[circulation]` edits. This check does not establish compliance with the target journal's submission requirements. No research project is configured in this kit checkout, so Checkpoint C does not apply to this maintenance task.
- Audit status: Local build and file comparison passed.
- Decision-log reference: 2026-10-04 Management Science template replacement.
