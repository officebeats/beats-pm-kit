---
description: Release a new version of the brain (Tag + GitHub Release)
---

// turbo-all

1. **CRITICAL**: Check existing tags to prevent regression: `git tag --sort=-v:refname | Select-Object -First 5`
2. Identify all strategic updates since the last release tag using `git log $(git describe --tags --abbrev=0)..HEAD`.
3. Generate Release Notes using the **Strategic Extraction Protocol** (Concept / Requirements / User Journey).
4. **Version & SEO Protocol**:
   - **Neutralize** `README.md`: Remove specific version numbers (use "Latest" or generic terms) to maintain SEO longevity.
   - **Optimize** `README.md`: Ensure keywords (FAANG, Product Management, AI) are present.
   - **Bump** `STATUS.md`: Update "System Health" with the new version `vX.Y.Z`.
   - **Bump** `KERNEL.md`: Update the footer signature.
5. Commit changes: `git commit -a -m "chore: Release vX.Y.Z"`
6. Tag the release: `git tag vX.Y.Z`
7. Push to remote: `git push origin main && git push origin vX.Y.Z`
8. Execute headless release: `gh release create vX.Y.Z --title "vX.Y.Z: Title" --notes "Generated Notes"`
9. Verify Go Live (Headless Heartbeat): `curl -s http://localhost:3000/api/status`

_Note: Requires `gh auth login` to be performed once by the user._
