$stagingDir = "00-DROP-FILES-HERE-00"
if (!(Test-Path $stagingDir)) { New-Item -ItemType Directory -Path $stagingDir }

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$captured = @()

# Load assemblies for image handling
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 1. Check for Files (FileDropList)
$files = Get-Clipboard -Format FileDropList
if ($files) {
    foreach ($file in $files) {
        $fileName = Split-Path $file -Leaf
        $dest = Join-Path $stagingDir $fileName
        Copy-Item -Path $file -Destination $dest -Force
        $captured += "File: $fileName"
    }
}

# 2. Check for Image
if ([System.Windows.Forms.Clipboard]::ContainsImage()) {
    $img = [System.Windows.Forms.Clipboard]::GetImage()
    $filename = "screenshot_$($timestamp).png"
    $path = Join-Path $stagingDir $filename
    try {
        $img.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        $captured += "Image: $filename"
    } finally {
        $img.Dispose()
    }
}

# 3. Check for Text (only if no files and no image, to avoid redundant paths)
if ($captured.Count -eq 0) {
    $text = Get-Clipboard -Format Text
    if ($text) {
        $filename = "clip_note_$($timestamp).txt"
        $path = Join-Path $stagingDir $filename
        $text | Out-File -FilePath $path
        $captured += "Text: $filename"
    }
}

if ($captured.Count -eq 0) {
    Write-Host "No content found in clipboard."
} else {
    Write-Host "Captured items into staging:"
    foreach ($item in $captured) {
        Write-Host " - $item"
    }
}
