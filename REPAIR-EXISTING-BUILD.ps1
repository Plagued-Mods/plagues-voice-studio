<#
Temporarily repair an already-created PyInstaller one-folder distribution.
Copies Python distribution metadata from the build virtual environment into
`dist\PlaguesVoiceStudio024\_internal`. It does NOT update an existing installer or
portable ZIP. Rebuild with v0.1.2 for release-quality artifacts.
#>
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path $PSScriptRoot).Path
$source = Join-Path $root '.venv-build\Lib\site-packages'
$target = Join-Path $root 'dist\PlaguesVoiceStudio024\_internal'
if (-not (Test-Path $source)) {
    throw "Build environment not found: $source"
}
if (-not (Test-Path $target)) {
    throw "Frozen application not found: $target"
}
$folders = @(Get-ChildItem -LiteralPath $source -Directory -Filter '*.dist-info')
if (-not $folders) { throw 'No package metadata was found in the build environment.' }
foreach ($folder in $folders) {
    Copy-Item -LiteralPath $folder.FullName -Destination $target -Recurse -Force
}
$requestsMeta = @(Get-ChildItem -LiteralPath $target -Directory -Filter 'requests-*.dist-info')
if (-not $requestsMeta) { throw 'Still missing requests distribution metadata.' }
Write-Host "Copied $($folders.Count) metadata directories into the existing frozen application."
Write-Host 'Now test dist\PlaguesVoiceStudio024\PlaguesVoiceStudio024.exe again.'
Write-Host 'IMPORTANT: Existing installer and portable ZIP files are NOT repaired by this command.'
