# Font Policy

[FRAME] Font choice follows controlling evidence rather than a universal default.

## Selection Order

[FRAME] Use: controlling template/brand → current user choice → accepted user presentation profile → project configuration → fonts verified in build and render environments → ask the user → explicitly approved compatibility fallback.

[FRAME] Microsoft YaHei, Arial, and Calibri are compatibility examples only. They may be used when the controlling template requires them or the user explicitly approves them as fallbacks; they are not unconditional defaults.

## Three Environments

| Environment | Required evidence | Failure behavior |
|---|---|---|
| Build | fonts available to the primary renderer | required unavailable/unknown → `need-user`; do not silently substitute |
| Render | fonts available to the current rendering tool | required unavailable/unknown → `need-user`; visual evidence is not current |
| Target | fonts available on the presentation machine/viewer | unknown may remain named `Unverified`; do not claim cross-viewer fidelity |

[FRAME] `font-contract.json` records intended families, roles, whether each is required, and user-approved fallbacks. `font-audit.json` records observed availability/substitution and binds to the current contract hash.

[FRAME] Run `report_font_audit.py <workspace>` after recording build/render/target evidence. Workspace readiness also embeds the same deterministic audit; required build/render gaps return `need-user`, while an unknown target remains `Unverified`.

[FRAME] An empty required-font set does not prove typography is designed. Add families before build when the design contract depends on them.
