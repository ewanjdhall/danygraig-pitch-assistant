# AI-assisted repository preparation checks

Date: 2 November 2026. Performed by Codex / ChatGPT (OpenAI), not by the student. These checks prepare a separate upload copy; they do not constitute a coursework submission or a participant evaluation.

## Starting point and unchanged application

- Original project snapshot: `1bd8f79945a45521dbb941418b03ad58b0c9fcb6` (28 October).
- Privacy-safe equivalent: `d867594958186334896b1bfe6b5552af7c8a81b3`.
- Original project files and Git history remain untouched. Application code, fictional data, figures and recorded outputs were not changed during preparation.
- README statements and ignore patterns were improved; this record and the history mapping were added.

## Replays and self-tests

All commands were run with `IIS_MODEL=mock`; no API key or live model was used.

| Check | Result |
|---|---|
| `python3 tests/run_tests.py` | Six Lab 3 conversations replayed on both v1 and v2 (12 runs); recorded result files unchanged. |
| `python3 tests/run_lab4.py` | 26 question/tool/image cases reproduced, plus six v3 regression cases matching v2; recorded result files unchanged. This is replay evidence, not comprehensive correctness. |
| `python3 hold_tool.py --selftest` | Valid hold shape accepted; 21-night stay refused. |
| `python3 vlm.py --selftest` | Both supplied mock image cases completed. The sample images themselves explicitly identify the material as drawn for teaching and the name/mark as invented. |
| `git diff --check` | Passed after normalising `.gitignore` line endings. |

## Known failures independently reproduced

These remain unfixed and are documented in Draft 2 and the README.

| Input | Actual v3 behaviour |
|---|---|
| `Hi, 2 adults plus bella, 6m campervan, 14-16 Aug, need electric hook-up` | No clarification; recommends Pitch 7 and assumes no dog. |
| `Hi, 0 adults, 6m campervan, 14-16 Aug, need electric hook-up` | Recommends Pitch 7 for zero adults. The hold tool's later validation is stricter than the recommendation path. |
| `Hi, 2 adults, 6m campervan, 14-16 Aug 2028, need electric hook-up` | Recommends Pitch 7 for 2027, silently discarding the explicit year. |

## Upload checks and history

- Scanned 192 historical file blobs for private-key, GitHub-token and API-token patterns; no pattern hits. A pattern scan is not a guarantee that every possible secret is absent.
- Checked current text files for local home-directory paths, the student number and university email addresses; no matches in tracked file contents.
- Fictional bookings contain pitch numbers and dates, not real guest identities. Real booking/payment/email integrations are not present.
- Replaced university email metadata with the selected account's GitHub no-reply address in this upload copy only. Compared all 24 historical commits: file trees, timestamps and messages match their originals. `HISTORY_MAP.md` maps the changed IDs.
- Only the prepared `main` branch is intended for upload; backup/original refs are not to be pushed.
- Supplied teaching fixtures are distinguished from the actual assignment requirements. No module PDFs, whole course folder, report drafts, credentials or saved guest holds are included.

## What is still required

- Student: run/inspect the prototype and record genuine personal checks in the README. Do not replace this with a claim that these assisted checks were performed personally.
- Student: approve public visibility before a marker can access the repository, or obtain an agreed alternative from the module team.
- Student: review and approve the final report and submission separately. No Canvas upload or submission has been made.
