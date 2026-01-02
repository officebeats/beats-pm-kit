# Hydration Script (PowerShell)
# Private by Design: This script copies templates to active files ONLY if they don't exist.
# It ensures your local environment is ready for data without overwriting anything.

$templates = @(
    @{ Template = "templates/SETTINGS_TEMPLATE.md"; Target = "SETTINGS.md" },
    @{ Template = "tracking/bugs/bugs-master_TEMPLATE.md"; Target = "tracking/bugs/bugs-master.md" },
    @{ Template = "tracking/critical/boss-requests_TEMPLATE.md"; Target = "tracking/critical/boss-requests.md" },
    @{ Template = "tracking/critical/escalations_TEMPLATE.md"; Target = "tracking/critical/escalations.md" },
    @{ Template = "tracking/projects/projects-master_TEMPLATE.md"; Target = "tracking/projects/projects-master.md" },
    @{ Template = "tracking/people/engineering-items_TEMPLATE.md"; Target = "tracking/people/engineering-items.md" },
    @{ Template = "tracking/people/stakeholders_TEMPLATE.md"; Target = "tracking/people/stakeholders.md" },
    @{ Template = "tracking/people/ux-tasks_TEMPLATE.md"; Target = "tracking/people/ux-tasks.md" }
)

Write-Host "🧠 Hydrating Antigravity Brain..." -ForegroundColor Cyan

foreach ($item in $templates) {
    if (-not (Test-Path $item.Target)) {
        Copy-Item $item.Template $item.Target
        Write-Host "  [+] Created $($item.Target)" -ForegroundColor Green
    } else {
        Write-Host "  [skip] $($item.Target) (Exists)" -ForegroundColor DarkGray
    }
}

# Ensure Directories Exist
$dirs = @("MEETINGS", "system/inbox/screenshots", "DATA", "RESEARCH")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  [+] Created Directory $dir/" -ForegroundColor Green
    }
}

Write-Host "`n✅ Brain is ready. Your privacy is secured." -ForegroundColor Cyan
Write-Host "Active files are ignored by git. You can now add your real data." -ForegroundColor Yellow
Start-Sleep -Seconds 3
