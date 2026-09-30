$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$siteRoot = (Resolve-Path -LiteralPath (Join-Path $projectRoot 'source\site')).Path
$stageRoot = Join-Path $env:LOCALAPPDATA 'Temp\cch-scope-stage'
$plan = Get-Content -LiteralPath (Join-Path $stageRoot 'scope-report.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$deletionRoot = (Resolve-Path -LiteralPath 'C:\Users\yasoj\OneDrive\デスクトップ\削除用').Path
$destinationRoot = [IO.Path]::GetFullPath((Join-Path $deletionRoot 'Crystal Clean Home_除外ページ_2026-10-01'))
if (-not $destinationRoot.StartsWith($deletionRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination outside approved desktop folder' }
if (Test-Path -LiteralPath $destinationRoot) { throw 'Destination already exists; do not overwrite it' }
$moves = foreach ($relative in $plan.move_entries) {
    $sourcePath = [IO.Path]::GetFullPath((Join-Path $siteRoot $relative))
    $destinationPath = [IO.Path]::GetFullPath((Join-Path $destinationRoot $relative))
    if (-not $sourcePath.StartsWith($siteRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Source outside site folder' }
    if (-not $destinationPath.StartsWith($destinationRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Destination outside discard folder' }
    if (-not (Test-Path -LiteralPath $sourcePath)) { throw "Source missing: $relative" }
    [PSCustomObject]@{ Source = $sourcePath; Destination = $destinationPath }
}
New-Item -ItemType Directory -Path $destinationRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $projectRoot 'source\manifest.json') -Destination (Join-Path $destinationRoot '取得一覧.json')
foreach ($move in $moves) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $move.Destination) -Force | Out-Null
    Move-Item -LiteralPath $move.Source -Destination $move.Destination
}
foreach ($relative in $plan.edited_files) {
    $targetPath = [IO.Path]::GetFullPath((Join-Path $siteRoot $relative))
    if (-not $targetPath.StartsWith($siteRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Edit outside site folder' }
    Copy-Item -LiteralPath (Join-Path (Join-Path $stageRoot 'edited') $relative) -Destination $targetPath -Force
}
Copy-Item -LiteralPath (Join-Path $stageRoot 'manifest.json') -Destination (Join-Path $projectRoot 'source\manifest.json') -Force
Copy-Item -LiteralPath (Join-Path $stageRoot 'scope-report.json') -Destination (Join-Path $projectRoot 'source\scope-report.json') -Force
Write-Output "Moved $($plan.removed_files) files to $destinationRoot"
Write-Output "Remaining site bytes: $($plan.remaining_bytes)"
