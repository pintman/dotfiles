# Issue tracker: Gitea

Issues and PRDs for this repo live as Gitea issues. Use the [`tea`](https://gitea.com/gitea/tea) CLI for all operations — the Gitea counterpart to `gh`.

## Conventions

Pass `--repo <owner>/<repo>` on every call so the target is unambiguous (e.g. `--repo bakera/wahr-falsch`).

- **Create an issue**: `tea issue create --repo <owner>/<repo> --title "..." --labels "..." --description "..."`. For multi-line bodies use `--description-file -` with a heredoc.
- **Read an issue**: `tea issue <number> --repo <owner>/<repo> --comments`. Add `--output json` for machine-readable output.
- **List issues**: `tea issue list --repo <owner>/<repo> --output json` with appropriate `--labels` and `--state` filters.
- **Comment on an issue**: `tea comment <number> "..." --repo <owner>/<repo>`
- **Apply / remove labels**: `tea issue edit <number> --repo <owner>/<repo> --add-labels "..."` / `--remove-labels "..."` (comma-separated).
- **Close**: `tea issue close <number> --repo <owner>/<repo>`. `close` does not accept a comment, so post the explanation first with `tea comment`, then close.
- **Pull requests**: `tea pr create`, `tea pr <number>`, `tea pr list`, etc. — the same shape as `gh pr ...`. Comments on PRs also go through `tea comment <number>`.

Prefer closing via commit messages: keywords like `closes #<number>` (also `close`, `closed`, `fix`/`fixes`/`fixed`, `resolve`/`resolves`/`resolved`) close the referenced issue automatically when pushed to the default branch. This keeps the history traceable.

### Description length limit

Gitea instances may answer `tea issue create --description "..."` with `500 Internal Server Error` once the body exceeds roughly 7–8 KB (observed: 7000 bytes work, 8300 bytes fail). For long content (e.g. detailed specs):

- Split the text at the end of a meaningful section so every part stays below the limit.
- Create the issue with the first part.
- Append the remaining parts as follow-up comments with `tea comment <number> "..." --repo <owner>/<repo>`.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external pull requests as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `tea pr` equivalents:

- **Read a PR**: `tea pr <number> --repo <owner>/<repo> --comments`; check it out with `tea pr checkout <number>` to inspect the diff.
- **List external PRs for triage**: `tea pr list --repo <owner>/<repo> --output json`, then keep only PRs whose author is not a repo collaborator.
- **Comment / label / close**: `tea comment <number>`, `tea pr edit <number> --add-labels`/`--remove-labels`, `tea pr close <number>`.

Like GitHub, Gitea shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `tea pr 42` and fall back to `tea issue 42`.

## When a skill says "publish to the issue tracker"

Create a Gitea issue.

## When a skill says "fetch the relevant ticket"

Run `tea issue <number> --repo <owner>/<repo> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `tea issue create --labels wayfinder:map`.
- **Child ticket**: an issue carrying `Part of #<map>` at the top of its description and labels `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: Gitea's **native issue dependencies** — the canonical, UI-visible representation. Add an edge with `tea api -X POST repos/<owner>/<repo>/issues/<child>/dependencies -f owner=<owner> -f repo=<repo> -F index=<blocker>`. Where dependencies are disabled on the instance, fall back to a `Blocked by: #<n>, #<n>` line at the top of the description. A ticket is unblocked when every blocker is closed.
- **Frontier query**: `tea issue list --repo <owner>/<repo> --output json` scoped to the map's children, drop any with an open blocker — an open issue in `tea api repos/<owner>/<repo>/issues/<n>/dependencies`, or in the `Blocked by` line — or an assignee; first in map order wins.
- **Claim**: `tea issue edit <n> --repo <owner>/<repo> --add-assignees <me>` — the session's first write.
- **Resolve**: `tea comment <n> "<answer>" --repo <owner>/<repo>`, then `tea issue close <n> --repo <owner>/<repo>`, then append a context pointer (gist + link) to the map's Decisions-so-far.
