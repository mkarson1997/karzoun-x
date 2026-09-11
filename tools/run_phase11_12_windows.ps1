$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repo = "https://github.com/mkarson1997/karzoun-x.git"
$BaseUrl = "http://127.0.0.1:11434"
$Models = @("qwen3:4b", "qwen3:8b", "qwen3:14b-q4_K_M")
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$Workspace = Join-Path $Downloads "karzoun-x-phase11-12"

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [Parameter(Mandatory=$true)][string]$FailureMessage
    )
    $process = Start-Process -FilePath $FilePath -ArgumentList $Arguments -Wait -NoNewWindow -PassThru
    if ($process.ExitCode -ne 0) {
        throw "$FailureMessage (exit code $($process.ExitCode))."
    }
}

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

Write-Host "`n=== Checking local Ollama and required models ===" -ForegroundColor Cyan
try {
    $tags = Invoke-RestMethod -Uri "$BaseUrl/api/tags" -Method Get -TimeoutSec 10
} catch {
    throw "Ollama is not reachable at $BaseUrl. Start Ollama and rerun this command."
}

$OllamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $OllamaCommand) {
    throw "ollama executable was not found."
}

$installed = @($tags.models | ForEach-Object { $_.name })
foreach ($Model in $Models) {
    if ($installed -contains $Model) {
        Write-Host "Model already installed: $Model" -ForegroundColor Green
        continue
    }
    Write-Host "Model missing: $Model" -ForegroundColor Yellow
    Write-Host "Pulling $Model. This can take several minutes depending on connection speed." -ForegroundColor Yellow
    Invoke-NativeChecked -FilePath $OllamaCommand.Source -Arguments @("pull", $Model) -FailureMessage "Ollama pull failed for $Model"
}

$tags = Invoke-RestMethod -Uri "$BaseUrl/api/tags" -Method Get -TimeoutSec 10
$installed = @($tags.models | ForEach-Object { $_.name })
$stillMissing = @($Models | Where-Object { $installed -notcontains $_ })
if ($stillMissing.Count -gt 0) {
    throw "Required model(s) still missing: $($stillMissing -join ', ')"
}

Write-Host "`n=== Preparing clean Phase 11/12 workspace ===" -ForegroundColor Cyan
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

Write-Host "`n=== Ensuring pinned resource-sampler dependency ===" -ForegroundColor Cyan
& $Python -m pip install -r requirements-phase8.txt
if ($LASTEXITCODE -ne 0) { throw "Phase 12 resource dependency install failed." }
& $Python -m pip check
if ($LASTEXITCODE -ne 0) { throw "Python environment failed pip check." }

Write-Host "`n=== Running repository quality checks ===" -ForegroundColor Cyan
$env:PYTHONPATH = Join-Path $Workspace "src"
& $Python -m ruff check .
if ($LASTEXITCODE -ne 0) { throw "Ruff failed." }
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
Write-Host "Quality checks passed." -ForegroundColor Green

Write-Host "`n=== Running Phase 11 held-out epistemic-gate study ===" -ForegroundColor Cyan
$Phase11Log = Join-Path $Workspace "results-phase11.log"
& $Python "scripts\run_phase11_epistemic_gate.py" --base-url $BaseUrl --model "qwen3:14b-q4_K_M" 2>&1 |
    Tee-Object -FilePath $Phase11Log
if ($LASTEXITCODE -ne 0) { throw "Phase 11 failed." }

Write-Host "`n=== Recording Phase 11 environment ===" -ForegroundColor Cyan
$PythonVersion = (& $Python --version 2>&1 | Out-String).Trim()
$OllamaVersion = (& ollama --version 2>&1 | Out-String).Trim()
@(
    "KARZOUN-X Phase 11 local environment"
    "timestamp_local=$((Get-Date).ToString('o'))"
    "source_commit=$SourceCommit"
    "python=$PythonVersion"
    "ollama=$OllamaVersion"
    "model=qwen3:14b-q4_K_M"
    "ollama_base_url=$BaseUrl"
) | Set-Content -Path (Join-Path $Workspace "results\phase11\environment.txt") -Encoding UTF8
& $Python -m pip freeze | Set-Content -Path (Join-Path $Workspace "results\phase11\pip-freeze.txt") -Encoding UTF8

Write-Host "`n=== Running Phase 12 three-model resource/quality ablation ===" -ForegroundColor Cyan
$Phase12Log = Join-Path $Workspace "results-phase12.log"
& $Python "scripts\run_phase12_model_resource_ablation.py" --base-url $BaseUrl 2>&1 |
    Tee-Object -FilePath $Phase12Log
if ($LASTEXITCODE -ne 0) { throw "Phase 12 failed." }

Write-Host "`n=== Recording Phase 12 environment ===" -ForegroundColor Cyan
@(
    "KARZOUN-X Phase 12 local environment"
    "timestamp_local=$((Get-Date).ToString('o'))"
    "source_commit=$SourceCommit"
    "python=$PythonVersion"
    "ollama=$OllamaVersion"
    "models=$($Models -join ',')"
    "ollama_base_url=$BaseUrl"
) | Set-Content -Path (Join-Path $Workspace "results\phase12\environment.txt") -Encoding UTF8
& $Python -m pip freeze | Set-Content -Path (Join-Path $Workspace "results\phase12\pip-freeze.txt") -Encoding UTF8

Write-Host "`n=== Committing machine-generated Phase 11 and 12 results ===" -ForegroundColor Cyan
& git config user.name "Mahmoud Karzoun"
& git config user.email "135722882+mkarson1997@users.noreply.github.com"
& git add results/phase11 results/phase12 results-phase11.log results-phase12.log
$changes = (& git status --porcelain) -join "`n"
if (-not [string]::IsNullOrWhiteSpace($changes)) {
    & git commit -m "results: record Phase 11 and Phase 12 follow-up experiments"
    if ($LASTEXITCODE -ne 0) { throw "Git commit failed." }
}

Write-Host "`n=== Synchronizing with main and pushing results ===" -ForegroundColor Cyan
& git pull --rebase origin main
if ($LASTEXITCODE -ne 0) {
    throw "Could not rebase Phase 11/12 results onto current main."
}
& git push origin HEAD:main
if ($LASTEXITCODE -ne 0) {
    $Branch = "phase11-12-results-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Write-Host "Main push blocked. Pushing $Branch instead." -ForegroundColor Yellow
    & git checkout -b $Branch
    & git push -u origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "Git push failed." }
    Write-Host "Results branch pushed: $Branch" -ForegroundColor Yellow
} else {
    Write-Host "Results pushed to main. Phase 13 will run automatically once GitHub sees both result sets." -ForegroundColor Green
}

Write-Host "`n======================================================" -ForegroundColor Green
Write-Host "KARZOUN-X PHASE 11 + PHASE 12 COMPLETE" -ForegroundColor Green
Write-Host "Workspace: $Workspace"
Write-Host "Phase 11:  $Workspace\results\phase11\summary.md"
Write-Host "Phase 12:  $Workspace\results\phase12\summary.md"
Write-Host "======================================================" -ForegroundColor Green
