---
description: Publish a new GitHub release with semantic versioning
---

# GitHub Release Workflow

## Pre-Flight Check

// turbo

```bash
git status
```

// turbo

```bash
git tag --sort=-v:refname | head -5
```

## Versioning Rules

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, minor updates

## Release Steps

### 1. Stage All Changes

```bash
git add .
```

### 2. Commit with Conventional Message

```bash
git commit -m "feat: [Brief description of changes]"
```

### 3. Create Annotated Tag

Replace `[VERSION]` with next version (e.g., if latest is v6.3.0, use v6.4.0):

```bash
git tag -a v[VERSION] -m "v[VERSION] - [Release Title]"
```

### 4. Push to GitHub

```bash
git push origin main
git push origin v[VERSION]
```

### 5. Create GitHub Release

```bash
gh release create v[VERSION] \
  --title "v[VERSION] - [Release Title]" \
  --notes "## What's New
- Change 1
- Change 2

**Full Changelog**: https://github.com/officebeats/beats-pm-antigravity-brain/compare/v[PREV_VERSION]...v[VERSION]" \
  --latest
```

## Verification

// turbo

```bash
gh release view v[VERSION] --json tagName,name,url
```
