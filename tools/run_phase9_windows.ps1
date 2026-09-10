$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo = "https://github.com/mkarson1997/karzoun-x.git"
$Model = "qwen3:14b-q4_K_M"
$BaseUrl = "http://127.0.0.1:11434"
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Workspace = Join-Path $Downloads "karzoun-x-phase9"

Write-Host "`n=== Locating verified KARZOUN-X Python environment ===" -ForegroundColor Cyan
$Python = Get-ChildItem $Downloads -Directory |
    Where-Object { $_.Name -like "karzoun-x-phase5-*" } |
    Sort-Object LastWriteTime -Descending |
    ForEach-Object {
        $candidate = Join-Path $_.FullName ".venv\Scripts\python.exe"
        if (Test-Path $candidate) { $candidate }
    } |
    Select-Object -First 1

if (-not $Python) {
    throw "Verified KARZOUN-X Python environment not found in Downloads."
}

Write-Host "Python environment: $Python" -ForegroundColor Green
& $Python -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "Python environment failed pip check."
}

Write-Host "`n=== Checking local Ollama ===" -ForegroundColor Cyan
try {
    $tags = Invoke-RestMethod -Uri "$BaseUrl/api/tags" -Method Get -TimeoutSec 10
} catch {
    throw "Ollama is not reachable at $BaseUrl."
}
$names = @($tags.models | ForEach-Object { $_.name })
if ($names -notcontains $Model) {
    throw "Required model $Model is not installed in Ollama."
}

Write-Host "`n=== Preparing clean Phase 9 workspace ===" -ForegroundColor Cyan
if (Test-Path $Workspace) {
    Set-Location $Workspace
    & git fetch origin main
    if ($LASTEXITCODE -ne 0) { throw "git fetch failed." }
    & git checkout main
    if ($LASTEXITCODE -ne 0) { throw "git checkout main failed." }
    & git reset --hard origin/main
    if ($LASTEXITCODE -ne 0) { throw "git reset failed." }
} else {
    & git clone $Repo $Workspace
    if ($LASTEXITCODE -ne 0) { throw "git clone failed." }
    Set-Location $Workspace
}

$SourceCommit = (& git rev-parse HEAD).Trim()
Write-Host "Source commit: $SourceCommit" -ForegroundColor Green

Write-Host "`n=== Running repository quality checks ===" -ForegroundColor Cyan
$env:PYTHONPATH = Join-Path $Workspace "src"
& $Python -m ruff check .
if ($LASTEXITCODE -ne 0) { throw "Ruff failed." }
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
Write-Host "Quality checks passed." -ForegroundColor Green

Write-Host "`n=== Recording local execution environment ===" -ForegroundColor Cyan
$Output = Join-Path $Workspace "results\phase9"
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$PythonVersion = (& $Python --version 2>&1 | Out-String).Trim()
$OllamaVersion = (& ollama --version 2>&1 | Out-String).Trim()
@(
    "KARZOUN-X Phase 9 local hard-stress environment"
    "timestamp_local=$((Get-Date).ToString('o'))"
    "source_commit=$SourceCommit"
    "python=$PythonVersion"
    "ollama=$OllamaVersion"
    "model=$Model"
    "ollama_base_url=$BaseUrl"
) | Set-Content -Path (Join-Path $Output "environment.txt") -Encoding UTF8

Write-Host "`n=== Running Phase 9 hard-stress benchmark ===" -ForegroundColor Cyan
$Log = Join-Path $Workspace "results-phase9.log"
& $Python "scripts\run_phase9_hard_stress.py" `
    --base-url $BaseUrl `
    --model $Model 2>&1 | Tee-Object -FilePath $Log
if ($LASTEXITCODE -ne 0) {
    throw "Phase 9 benchmark failed."
}

Write-Host "`n=== Committing machine-generated Phase 9 results ===" -ForegroundColor Cyan
& git config user.name "Mahmoud Karzoun"
& git config user.email "135722882+mkarson1997@users.noreply.github.com"
& git add results/phase9 results-phase9.log
$changes = (& git status --porcelain) -join "`n"
if (-not [string]::IsNullOrWhiteSpace($changes)) {
    & git commit -m "results: record Phase 9 hard-stress local LLM benchmark"
    if ($LASTEXITCODE -ne 0) { throw "Git commit failed." }
}

Write-Host "`n=== Synchronizing with main and pushing results ===" -ForegroundColor Cyan
& git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    throw "Could not rebase Phase 9 results onto current main."
}
& git push origin HEAD:main
if ($LASTEXITCODE -ne 0) {
    $Branch = "phase9-hard-stress-results-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Write-Host "Main push blocked. Pushing $Branch instead." -ForegroundColor Yellow
    & git checkout -b $Branch
    & git push -u origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "Git push failed." }
    Write-Host "Results branch pushed: $Branch" -ForegroundColor Yellow
} else {
    Write-Host "Results pushed to main." -ForegroundColor Green
}

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "KARZOUN-X PHASE 9 COMPLETE" -ForegroundColor Green
Write-Host "Workspace: $Workspace"
Write-Host "Summary:   $Workspace\results\phase9\summary.md"
Write-Host "===============================================" -ForegroundColor Green
