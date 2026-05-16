# Praxis Playbook Library

_Generated: 2026-05-15 by `praxis-v0.1`_

## What this is

Each `.md` file in this tree is a playbook derived from a cluster of semantically-similar support tickets. The frontmatter is YAML and is agent-consumable (Brainbox skill, Claude Skill, CrewAI, RAG indexer). The body is human-readable for support team review and refinement.

## Folder structure

Folders are routed by **ticket_class** (not project). A `b2b_operator`
playbook may have evidence from BS or RAOS tickets — what matters is the
customer type the pattern describes.

```
playbooks/
├── end_user/              # B2C consumer-facing patterns
├── b2b_operator/          # Business / operator-facing patterns
├── internal_partner/      # Internal staff support patterns
└── unknown/               # Patterns whose customer-class couldn't be determined
```

Within each class, playbooks are grouped by `issue_category` (bugs / billing / configuration / knowledge_gaps / integrations / vendor_issues / user_issues / feature_requests).

## Playbook count

- **BS:** 95 playbooks
- **RAOS:** 27 playbooks

## Frontmatter fields

Every playbook starts with a YAML block (`---` fenced) containing:

- `id`, `name`, `title`, `description` — identification + summary
- `cluster_id` — back-reference to the source cluster in Postgres/LanceDB
- `ticket_class`, `issue_category`, `resolution_pattern` — taxonomy
- `cluster_size`, `frequency_per_month`, `median_resolution_minutes` — measured stats
- `evidence_tickets` — sample ticket keys for provenance
- `agent_compatibility` — flags for Brainbox / Claude / agent-assist / autonomous
- `status` — `active` (high confidence) / `draft` / `needs_review`
- `annual_hours_saved` — will be populated by ROI analysis (Sloj 7 pipeline step)

## Status meaning

- `active` — extraction confidence ≥ 0.7. Safe to register as agent skill.
- `draft` — confidence 0.5-0.7. Human review recommended before production use.
- `needs_review` — confidence < 0.5. Treat as a starting point only.

## ROI numbers

Hours-per-year figures (when present) are derived from observed frequency × median active resolution time. Multiply by your internal cost-per-hour for currency conversion. Deflection rates, time reductions, and engineering effort estimates (when present, from Sloj 7 pipeline) are LLM-derived hypotheses — they're starting points, not commitments. Validate with pilots.
