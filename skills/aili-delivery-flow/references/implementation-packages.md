# Implementation Packages

An implementation package is the unit that BUILD may execute.

## Required Fields

- goal and acceptance criteria;
- allowed files or smallest likely edit surface;
- forbidden scope;
- source artifacts and evidence;
- implementation owner or delegation plan;
- verification command(s);
- BUILD local review lanes: code review, test verification, and security review trigger or skip condition;
- repair or retry limit;
- rollback or pause condition;
- whether commits are allowed.

## Rules

- Keep packages independently reviewable where practical.
- Do not combine unrelated feature, harness, install, and documentation work unless explicitly approved.
- BUILD is not complete after writing files; it must finish or explicitly block on the local code-review, test, and security-review gates.
- Security review may be skipped only when no security-sensitive surface is present; record the skip reason.
- If an in-scope repair changes code or behavior, rerun the affected verification and review lane before returning BUILD evidence.
- Pause if the package requires new dependencies, schema changes, public API changes, forbidden files, or broader scope than approved.
