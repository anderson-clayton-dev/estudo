---
name: tutor-estudos
description: Teach or continue card-based study courses in this directory. Use when the user wants to learn, continue a course, or navigate study cards; do not use for ordinary file maintenance.
---

# Tutor de Estudos

Use this skill only for teaching and course navigation in `Documentos/ESTUDO`.

## Load the relevant guidance

- At the start of a new course, read the visual overview in `Documentos/ESTUDO/modelo.md` and [card-protocol.md](references/card-protocol.md).
- For other teaching responses, read [card-protocol.md](references/card-protocol.md).
- Before creating a card, navigating, or editing a course history, read [flow-format.md](references/flow-format.md).
- For every numeric menu choice, run `scripts/resolve_option.py` against that course's `fluxo.md`. Treat its result as authoritative; never map a number from memory or from another card.

## Start or resume a course

- For a new course, first identify the subject. If the user has not given a course folder name, ask for it before creating any folder or presenting CARD 1. If the user already gave both, do not ask again.
- Treat a request to start from scratch or a newly proposed subject as a new course, even if another course has a saved `fluxo.md`.
- Resume only a course the user names as a continuation or one that is clearly active in the current conversation. If the intended course is unclear, ask which one; do not silently select the only folder that happens to contain an active-card marker.
- Create the new course folder only after its name is known, then create its initial `fluxo.md` and CARD 1.

Run the resolver from any working directory:

```bash
python3 /absolute/path/to/tutor-estudos/scripts/resolve_option.py /path/to/course/fluxo.md --choice 5
```

For a direct destination request, validate the target with `--goto "CARD 5"`. The script is read-only and prints one JSON result. If it returns `ok: false`, do not guess; resolve the missing or inconsistent state before acting.

## Preserve the course history

Use the active course's own `fluxo.md`; never choose a course or active card by guessing. Update the flow before presenting a newly created card. After `VOLTAR` or `IR PARA`, update its recorded active card before presenting the destination. Keep existing branches and IDs intact.

For card format, onboarding, tone, and the exact semantics of `MAIS`, `VOLTAR`, and `IR PARA`, follow [card-protocol.md](references/card-protocol.md). For the flow schema and update rules, follow [flow-format.md](references/flow-format.md).
