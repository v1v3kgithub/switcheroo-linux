# CLAUDE.md

Switcheroo for Linux: a keyboard-driven window switcher (Python 3, GTK 3, libwnck).
Run the test suite with `python -m unittest discover -s tests -v` (the same command CI runs).

## Git workflow

### Label → type mapping
| GitHub label    | Branch prefix | Commit type |
|-----------------|---------------|-------------|
| bug             | bugfix        | bugfix      |
| enhancement     | feature       | feature     |
| documentation   | docs          | docs        |
| chore           | chore         | chore       |
| refactor        | refactor      | refactor    |

Only apply labels that already exist in the repo; ask before creating a new one.

### Branches
When assigned an issue: `git fetch origin main`, create `<prefix>/<issue>-<slug>` off
`origin/main`, push it with `-u`, and check it out. Slug: lowercase, hyphenated, ≤5 words.
Examples: `bugfix/6-literal-dot-queries`, `feature/12-workspace-indicator`.

Umbrella issues (e.g. #10) are split into their own issues before work starts.

### Chunked issue work
When an issue can be split, state a chunk plan first. Each chunk must pass
the test suite on its own.

- Default: implement one chunk, run the tests, report, and stop. Do not commit.
- "Next Chunk" → start the next chunk.
- "Commit + Push" → commit all finished, uncommitted work as one commit (or one per
  chunk if asked), then push. Never commit or push without this instruction.
- If told at the start to "do all chunks", work through every chunk without stopping;
  still no commit or push until told.

### Commit messages
Format: `<issue>-<type>: <imperative summary>` (no brackets), using the mapping above.
Examples: `6-bugfix: Fall back to plain search when dot query has no matches`,
`1-bugfix: Track window focus history for MRU ordering`.

Commits not tied to an issue use `<type>: <summary>` (e.g. `docs: Add CLAUDE.md`).
Applies to every contributor, human or AI.

### Issues
When asked to turn a discussion into an issue, show the draft (title, body, label)
and create it, via `gh` or the GitHub MCP tools, only after confirmation.

### Pull requests
Title follows the commit format; body includes `Closes #<issue>`. Squash-merge into main.
