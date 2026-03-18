---
description: Publish a new GitHub release with semantic versioning. Runs full regression tests before publishing.
---

# /release — Publish a GitHub Release

## Pre-Flight Checks (MANDATORY — DO NOT SKIP)

// turbo-all

1. Run the release readiness test suite:
```bash
python -m pytest system/tests/test_release_readiness.py -v --tb=short 2>&1
```

2. If ANY test fails, STOP. Fix the issue before proceeding. Do NOT publish a release with test failures.

3. Check git status for uncommitted changes:
```bash
git status --short
```

4. If there are uncommitted changes, stage and commit them first.

## Determine Version

5. Check the latest tag:
```bash
git tag --sort=-v:refname | head -5
```

6. Determine the new version number:
   - **Patch** (x.y.Z): Bug fixes, typo corrections, trivial updates
   - **Minor** (x.Y.0): New skills, agents, workflows, features
   - **Major** (X.0.0): Breaking architecture changes, major restructuring

## Publish

7. Stage, commit, and push:
```bash
git add -A
git commit -m "<version> - <title>"
git push origin main
```

8. Tag and push tag:
```bash
git tag <version> HEAD
git push origin <version>
```

9. Create the release via gh API:
```bash
gh api repos/officebeats/beats-pm-kit/releases --input - <<EOF
{
  "tag_name": "<version>",
  "name": "<version> - <title>",
  "body": "<release notes>",
  "draft": false,
  "make_latest": "true"
}
EOF
```

10. Verify the release is live:
```bash
gh release list --limit 3
```

## Post-Release

11. Clean up any temp files or directories used during the release process.
