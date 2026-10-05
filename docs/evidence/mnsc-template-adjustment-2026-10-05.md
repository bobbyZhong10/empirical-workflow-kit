# Evidence card: Management Science template adjustment

- Batch identifier: kit-mnsc-template-2026-10-05
- Producer runtime: Codex
- Created at: 2026-10-05
- Claim supported: The kit reflects the supplied template source and still compiles.
- Source artifact: Supplied June 2024 template distribution; repository copy in `Template_for_Management_Science_Journal/`. The external delivery location is omitted from the public record.
- Output path: `Template_for_Management_Science_Journal/INFORMS-MNSC-Template.tex`.
- Method: Compared the source and kit template files, copied the sole changed file, checked all supplied file hashes, and compiled the kit source through `scripts/ewf.py run latexmk` after `doctor` passed for `latexmk`.
- Observation: The adjustment adds four bibliography comments and changes no LaTeX commands. The build exited 0 and produced a six-page PDF. It retained the prior font substitutions and 27.14 pt oversized sample float warning.
- Inference: The adjusted source is installed and builds locally with the existing kit dependencies.
- Limitations: Compilation does not assess submission compliance or the substance of the sample manuscript.
- Audit status: File comparison and local build passed.
- Decision-log reference: 2026-10-05 Management Science template comment adjustment.
