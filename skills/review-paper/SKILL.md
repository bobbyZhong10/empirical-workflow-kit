---
name: review-paper
description: Compatibility entry point for reviewing a full manuscript against a target journal with severity-triaged findings. TRIGGER on "/review-paper", "review my paper", "referee my draft", "is this ready to submit", "desk reject risk", "Reviewer 2", or "write my referee report". Routes to manuscript-review.
---

# review-paper

This is an Empirical Workflow Kit compatibility facade. Runtime views defined
in `workflow.manifest.yaml` link here; edit only the canonical tree.

Read and execute [`../manuscript-review/SKILL.md`](../manuscript-review/SKILL.md) in full.
That skill owns the complete prompt, safeguards, inputs, outputs, and tool rules.
This alias adds no behavior and must never become a second implementation.
