---
name: atlassian-context-archive
description: Capture Jira and Confluence references found during Slack or Teams intake by using read-only Atlassian connector fetches and saving local markdown context artifacts with full source URLs.
priority: P0
maxTokens: 3000
triggers:
  - "/beats-slack"
  - "/beats-teams"
  - "/beats-comms"
version: 1.0.0
author: Beats PM Brain
---

# Atlassian Context Archive Skill

> **Role**: Enrich communication intake with referenced Jira and Confluence context while keeping Slack, Teams, Jira, and Confluence strictly read-only.

## 1. Archive Contract

Save Atlassian artifacts under:

```text
3. Meetings/context-artifacts/atlassian/jira/{YYYY-MM-DD}_{jira-key}_{RUN_ID}.md
3. Meetings/context-artifacts/atlassian/confluence/{YYYY-MM-DD}_{page-slug}_{RUN_ID}.md
```

Track local dedupe state in:

```text
3. Meetings/context-artifacts/atlassian/_manifest.json
```

Every stored artifact must include the full source URL near the top:

- Frontmatter field: `source_url`
- Body line: `**Source**: [<full Atlassian URL>](<full Atlassian URL>)`

If a full Jira or Confluence URL cannot be resolved, do not write a successful artifact. Report `source_url_missing_or_invalid` or `source_url_unresolved` in the run report.

---

## 2. Safety Boundary

Atlassian capture is referenced-only and read-only.

Allowed Atlassian connector operations:

- Search Jira and Confluence.
- Fetch Jira issue or Confluence page details.
- Read page/issue metadata needed for title, status, owner, updated timestamp, and canonical URL.

Prohibited Atlassian operations:

- Create, edit, comment, transition, assign, delete, update pages, add worklogs, or mutate Jira/Confluence in any way.

Source chat systems remain read-only:

- Do not send, draft, reply, react, edit, delete, upload, or mutate Slack/Teams.
- Do not mark Slack/Teams messages read or unread.

---

## 3. Reference Extraction

After the chat transcript is saved, scan only that transcript:

```bash
python3 system/scripts/atlassian_context_state.py scan --transcript-path "<TRANSCRIPT_PATH>"
```

Capture only references found in the processed transcript window:

- Jira URLs.
- Jira issue keys such as `ABC-123`.
- Confluence page URLs.

Do not broad-search Jira or Confluence. Do not crawl spaces, projects, child pages, comments, or linked issues unless a specific referenced item requires a direct read to identify the source.

Default cap: process up to `10` Atlassian references per run. Report references skipped beyond the cap.

---

## 4. Read-Only Fetch Protocol

For each scan result:

1. If it already has a full `source_url`, use that URL as the required source URL.
2. If it is a Jira key-only reference, resolve it with a read-only Atlassian search/fetch and derive the canonical Jira URL before archiving.
3. If it is a Confluence URL, fetch the page read-only and retain the original or canonical URL.
4. If the connector is unavailable, permissions are missing, or the reference is ambiguous, skip artifact creation and report the issue.
5. If fetched content is unchanged from the manifest hash, skip a new artifact and link the previous artifact path in the run report.

Use the Atlassian connector's read tools only. Prefer direct fetches from exact ARIs/IDs when available; use Rovo search only to resolve exact references such as key-only Jira mentions.

---

## 5. Artifact Writing

After a read-only fetch, write the local artifact with:

```bash
python3 system/scripts/atlassian_context_state.py record \
  --reference-type jira|confluence \
  --reference-id "<JIRA_KEY_OR_PAGE_ID>" \
  --source-url "<FULL_SOURCE_URL>" \
  --run-id "<RUN_ID>" \
  --platform slack|teams|comms \
  --title "<SOURCE_TITLE>" \
  --status "<STATUS_WHEN_AVAILABLE>" \
  --owner "<OWNER_WHEN_AVAILABLE>" \
  --source-updated-at "<SOURCE_UPDATED_AT_WHEN_AVAILABLE>" \
  --summary "<EXTRACTED_CONTEXT_SUMMARY>" \
  --transcript-path "<TRANSCRIPT_PATH>" \
  --message-reference "<CHAT_MESSAGE_REFERENCE>" \
  --fetched-content-file "<LOCAL_FETCHED_CONTENT_SNAPSHOT>"
```

If using a temporary fetched-content file, keep it local and delete it after the artifact is recorded when practical.

Artifacts should include:

- Source URL.
- Fetched timestamp.
- Source title, status, owner, and updated timestamp when available.
- Chat transcript path and message reference.
- Concise extracted context.
- Searchable source content snapshot or bounded relevant excerpt.
- Routing notes for local task/status updates.

---

## 6. Run Report Requirements

Each Slack, Teams, or combined comms run report must include:

- Atlassian references found.
- Artifacts written with paths.
- Existing unchanged artifacts skipped with paths.
- References skipped due to cap, ambiguity, missing URL, permissions, or connector unavailability.
- Task/status routing conflicts that require manual review.

Never present an Atlassian artifact as successfully captured unless the local artifact contains a full `source_url`.
