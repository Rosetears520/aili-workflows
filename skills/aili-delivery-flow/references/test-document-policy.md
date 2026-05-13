# Test Document Policy

The test document turns requirements into verification evidence before implementation starts.

## Required Content

- requirement or scenario identifier;
- test case or manual check;
- expected result;
- command or evidence source;
- status: planned, passed, failed, skipped, or unverified.

## Gate

- DEFINE should create or update the acceptance test document for non-trivial work.
- BUILD may start only when test expectations are accepted or explicitly waived.
- SHIP must use fresh evidence and identify any `Unverified` items.
