---
name: sre-compliance-evidence
description: Maps SRE and operational artifacts to compliance controls and prepares audit evidence. Use whenever a user mentions an audit, ATO, FedRAMP, NIST 800-53, SOC 2, PCI DSS, HIPAA, ISO 27001, control evidence, POA&M, or asks which controls incident records, DR tests, change records, monitoring or backups satisfy.
---

# Compliance Evidence Mapper

Run bundled scripts with paths rooted at this skill's folder, written here as `${SKILL_PATH}` (the directory containing this SKILL.md). The terminal starts at the workspace root, so never use a bare `scripts/...` path.

Public-sector and regulated clients spend heavily on audit preparation, and SRE teams already produce much of
the evidence. This skill connects the two and finds gaps before auditors do.

## Workflow

1. Identify frameworks in scope from the client overlay or the user.
2. Inventory the artifacts provided (incident records, postmortems, DR test reports, change tickets,
   monitoring configs, access reviews, backup logs).
3. Look up control mappings with `${SKILL_PATH}/scripts/control_lookup.py --framework <name> --topic <topic>`.
   Control text and IDs come from `references/`; never recall them from memory, because wording and
   revisions matter to auditors.
4. For each relevant control: state which artifacts provide evidence, how well (Full / Partial / None),
   and what is missing (e.g., test result not recorded, approval not captured, retention too short).
5. Draft evidence narratives in auditor-friendly language for controls with Full or Partial coverage.
6. Produce remediation items for gaps.

## Deterministic checks

Use the scripts for anything exact; do not recompute their results by hand.

- `python ${SKILL_PATH}/scripts/control_lookup.py controls --framework <id> [--artifact <type>]` lists mapped controls.
- `python ${SKILL_PATH}/scripts/control_lookup.py coverage inventory.yaml --framework <id>` reports Full, Partial or None per control with gaps. Framework ids: nist-800-53-r5, soc2, iso27001-2022, pci-dss-4, hipaa.

## Output format

Coverage table (control ID, control title, evidence artifacts, coverage, gap); evidence narratives;
remediation list.

## Guardrails

- Do not assert a control is satisfied; state evidence coverage for the assessor to judge.
- Cite the framework revision used (e.g., NIST SP 800-53 Rev. 5).
- Never include the evidence content itself if it exceeds the overlay's classification ceiling.

## Resources

- [scripts/control_lookup.py](./scripts/control_lookup.py) — control lookup and evidence coverage (built)
- [references/artifact-to-control-map.yaml](./references/artifact-to-control-map.yaml) — artifact-to-control mapping; compliance lead verifies IDs (built)
- [references/azure-devops.md](./references/azure-devops.md) — ADO tenant adaptations; read when the client overlay declares an ADO tenant (built)
- Planned (not yet built): `references/nist-800-53-r5-ops-controls.md`, `references/soc2-tsc.md`, `references/pci-dss.md`,
  `references/hipaa-security.md`, `references/iso27001-annex-a.md` — curated, licensed control extracts
