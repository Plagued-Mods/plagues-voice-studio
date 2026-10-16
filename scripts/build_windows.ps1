<#
.SYNOPSIS
  Build a bundled Windows portable package and Inno Setup installer.
.DESCRIPTION
  Build machine: Windows x64, Python 3.11, Git, internet to download weights,
  and Inno Setup 6 for the optional conventional installer.
  -FullOffline downloads AND validates all four models, then bundles an
  offline-only policy marker so runtime will never silently download weights.
  -SkipModels can be used with -FullOffline ONLY if all weights were previously
  downloaded to models/. The preflight validation will still run.
.EXAMPLE
  .\scripts\build_windows.ps1 -FullOffline
.EXAMPLE
  .\scripts\build_windows.ps1 -FullOffline -SkipModels
.EXAMPLE
  .\scripts\build_windows.ps1 -Models nano
#>
param(
    [ValidateSet('nano','turbo','english','multilingual-v3')]
    [string[]]$Models = @('nano'),
    [switch]$FullOffline,
    [switch]$SkipModels,
    [switch]$SkipInstaller
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root

function Assert-Success([string]$message) {
    if ($LASTEXITCODE -ne 0) { throw $message }
}

if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    throw 'The Windows installer must be built on 64-bit Windows.'
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required on the BUILD machine to install upstream Chatterbox.'
}
if ($FullOffline) {
    $Models = @('nano','turbo','english','multilingual-v3')
    Write-Host 'Building STRICT FULL-OFFLINE edition with ALL FOUR Chatterbox models.'
}

if (-not (Test-Path '.venv-build\Scripts\python.exe')) {
    py -3.11 -m venv .venv-build
    Assert-Success 'Could not create venv. Install 64-bit Python 3.11.'
}
$python = Join-Path $root '.venv-build\Scripts\python.exe'
& $python -m pip install --upgrade pip setuptools wheel
Assert-Success 'pip bootstrap failed'
& $python -m pip install -e '.[build]'
Assert-Success 'Project dependency installation failed'

# Remove stale strict mode marker before preparing a new build.
$marker = Join-Path $root 'models\offline-bundle.json'
if (Test-Path $marker) { Remove-Item $marker -Force }
if (-not $SkipModels) {
    & $python scripts\download_models.py @Models
    Assert-Success 'Model download or validation failed; no installer produced.'
}
if ($FullOffline) {
    & $python scripts\verify_models.py --all --root models --write-marker
    Assert-Success 'Strict offline preflight failed. Cannot release an incomplete bundle.'
}

# Never reuse previous frozen Python modules. Source edits do not change a built EXE.
if (Test-Path 'dist\PlaguesVoiceStudio024') {
    Remove-Item -LiteralPath 'dist\PlaguesVoiceStudio024' -Recurse -Force
}
& $python -m PyInstaller --clean --noconfirm ChatterboxStudio.spec
Assert-Success 'PyInstaller build failed'

# Smoke-test the actual frozen executable, not just the source venv. This
# catches missing importlib.metadata *.dist-info directories, such as the
# Transformers/requests issue, BEFORE compression or installer generation.
$exe = Join-Path $root 'dist\PlaguesVoiceStudio024\PlaguesVoiceStudio024.exe'
$report = Join-Path $root 'build\frozen-smoke-test.json'
if (Test-Path $report) { Remove-Item $report -Force }
Write-Host 'Testing frozen runtime and dependency metadata...'
$smoke = Start-Process -FilePath $exe -ArgumentList @('--self-test', ('"' + $report + '"')) -Wait -PassThru
if (-not (Test-Path $report)) {
    throw "Frozen self-test did not produce a report (exit code $($smoke.ExitCode))."
}
$smokeReport = Get-Content -LiteralPath $report -Raw | ConvertFrom-Json
if ($smoke.ExitCode -ne 0 -or $smokeReport.status -ne 'passed') {
    $details = ($smokeReport.errors | Out-String).Trim()
    throw "Frozen application self-test failed. Fix before packaging. Details:`n$details"
}
Write-Host 'Frozen runtime self-test PASSED (all checked package metadata and model imports).'

# Exercise the ACTUAL packaged Qt main window and its Export Library.
# A basic dependency test does not catch NameError in ExportBrowser._build.
$uiReport = Join-Path $root 'build\frozen-ui-smoke-test.json'
if (Test-Path $uiReport) { Remove-Item -LiteralPath $uiReport -Force }
Write-Host 'Smoke-testing packaged Qt GUI initialization...'
$uiSmoke = Start-Process -FilePath $exe -ArgumentList @('--ui-self-test', ('"' + $uiReport + '"')) -Wait -PassThru
if (-not (Test-Path $uiReport)) {
    throw "Frozen GUI test did not produce a report (exit code $($uiSmoke.ExitCode)). The installer was NOT created."
}
$uiResult = Get-Content -LiteralPath $uiReport -Raw | ConvertFrom-Json
if ($uiSmoke.ExitCode -ne 0 -or $uiResult.status -ne 'passed' -or $uiResult.version -ne '0.2.4') {
    $details = ($uiResult.errors | Out-String).Trim()
    throw "Frozen GUI startup test failed. Installer not created. Details:`n$details"
}
Write-Host 'Frozen Qt main-window test PASSED.'

if ($FullOffline) {
    # PyInstaller onedir locates collected data under dist\App\_internal\.
    & $python scripts\verify_models.py --all --root dist\PlaguesVoiceStudio024\_internal\models --require-marker
    Assert-Success 'Frozen application is missing model data. Packaging aborted.'
}

New-Item -ItemType Directory -Force artifacts | Out-Null
$filename = if ($FullOffline) { 'PlaguesVoiceStudio024-FullOffline-Portable.zip' } else { 'PlaguesVoiceStudio024-Portable.zip' }
$portable = Join-Path $root ('artifacts\' + $filename)
if (Test-Path $portable) { Remove-Item $portable -Force }
Compress-Archive -Path 'dist\PlaguesVoiceStudio024' -DestinationPath $portable -CompressionLevel Optimal
Write-Host "Portable distribution: $portable"

if (-not $SkipInstaller) {
    $iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if (-not $iscc) {
        $candidate = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
        if (Test-Path $candidate) { $iscc = @{ Source=$candidate } }
    }
    if (-not $iscc) {
        Write-Warning 'Inno Setup 6 not found; installer skipped. The portable ZIP was built.'
    } else {
        if (Test-Path 'dist-installer') {
            # Avoid copying stale BIN slices from earlier builds.
            Remove-Item dist-installer -Recurse -Force
        }
        & $iscc.Source installer.iss
        Assert-Success 'Inno Setup compilation failed'
        # With disk spanning, a full-offline setup consists of an EXE and BIN slices.
        $setupFiles = @(Get-ChildItem dist-installer -File | Where-Object { $_.Extension -in '.exe', '.bin' })
        if (-not $setupFiles) { throw 'Inno Setup reported success but generated no installer.' }
        Copy-Item -LiteralPath $setupFiles.FullName -Destination artifacts\ -Force
        Write-Host 'Installer files are in artifacts\. Keep Setup.exe and every Setup-*.bin together.'
    }
}
Write-Host 'Done. Target Windows machines do NOT require Python, pip or network access to synthesize speech in full-offline mode.'
