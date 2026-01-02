#!/bin/bash
# Mac/Linux Hydration Script

echo "🧠 Hydrating Antigravity Brain..."

# Array of Template -> Target
declare -a files=(
    "templates/SETTINGS_TEMPLATE.md:SETTINGS.md"
    "tracking/bugs/bugs-master_TEMPLATE.md:tracking/bugs/bugs-master.md"
    "tracking/critical/boss-requests_TEMPLATE.md:tracking/critical/boss-requests.md"
    "tracking/critical/escalations_TEMPLATE.md:tracking/critical/escalations.md"
    "tracking/projects/projects-master_TEMPLATE.md:tracking/projects/projects-master.md"
    "tracking/people/engineering-items_TEMPLATE.md:tracking/people/engineering-items.md"
    "tracking/people/stakeholders_TEMPLATE.md:tracking/people/stakeholders.md"
    "tracking/people/ux-tasks_TEMPLATE.md:tracking/people/ux-tasks.md"
    "tracking/people/delegated-tasks_TEMPLATE.md:tracking/people/delegated-tasks.md"
    "TEMPLATES/PRD_TEMPLATE.md:vault/products/PRD_TEMPLATE.md"
)

# Loop and copy
for entry in "${files[@]}"; do
    template="${entry%%:*}"
    target="${entry##*:}"

    if [ ! -f "$target" ]; then
        cp "$template" "$target"
        echo "  [+] Created $target"
    else
        echo "  [skip] $target (Exists)"
    fi
done

# Directories
mkdir -p MEETINGS system/inbox/screenshots DATA RESEARCH

echo ""
echo "✅ Brain is ready."
