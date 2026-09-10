$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoUrl = "https://github.com/mkarson1997/karzoun-x.git"
$Model = "qwen3:14b-q4_K_M"
$OllamaBaseUrl = "http://127.0.0.1:11434"
$Downloads = Join-Path $env:USERPROFILE "Downloads"
$RunRoot = Join-Path $Downloads "karzoun-x-phase8"

function Write-Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function Resolve-NvidiaSmi {
    $Command = Get-Command "nvidia-smi" -ErrorAction SilentlyContinue
    if ($null -ne $Command -and -not [string]::IsNullOrWhiteSpace($Command.Source)) {
        return $Command.Source
    }

    $Candidates = @(
        (Join-Path $env:WINDIR "System32\nvidia-smi.exe"),
        (Join-Path $env:ProgramFiles "NVIDIA Corporation\NVSMI\nvidia-smi.exe")
    )

    if (${env:ProgramW6432}) {
        $Candidates += (Join-Path ${env:ProgramW6432} "NVIDIA Corporation\NVSMI\nvidia-smi.exe")
    }

    foreach ($Candidate in ($Candidates | Select-Object -Unique)) {
        if (Test-Path -LiteralPath $Candidate) {
            return $Candidate
        }
    }

    return $null
}

function Request-ModelUnload {
    Write-Host "Requesting Ollama model unload through the local HTTP API..." -ForegroundColor DarkGray
    $Body = @{
        model = $Model
        keep_alive = 0
    } | ConvertTo-Json -Compress

    try {
        $null = Invoke-RestMethod `
            -Uri "$OllamaBaseUrl/api/generate" `
            -Method Post `
            -ContentType "application/json" `
            -Body $Body `
            -TimeoutSec 60
    } catch {
        throw "Ollama model-unload API request failed: $($_.Exception.Message)"
    }

    $Verified = $false
    for ($Attempt = 0; $Attempt -lt 10; $Attempt++) {
        Start-Sleep -Seconds 1
        try {
            $Running = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/ps" -Method Get -TimeoutSec 10
            $Names = @($Running.models | ForEach-Object { $_.name })
            if ($Names -notcontains $Model) {
                $Verified = $true
                break
            }
        } catch {
            # The unload request itself succeeded. Older Ollama builds may not expose /api/ps.
            Write-Host "Could not query /api/ps; continuing after successful unload request." -ForegroundColor Yellow
            $Verified = $true
            break
        }
    }

    if (-not $Verified) {
        throw "Ollama still reports '$Model' as loaded after the unload request. Cold-start benchmark aborted."
    }
}

Write-Step "Locating the verified KARZOUN-X Python environment"
$OldWorkspace = Get-ChildItem -Path $Downloads -Directory |
    Where-Object { $_.Name -like "karzoun-x-phase5-*" } |
    Sort-Object LastWriteTime -Descending |
    Where-Object { Test-Path (Join-Path $_.FullName ".venv\Scripts\python.exe") } |
    Select-Object -First 1

if ($null -eq $OldWorkspace) {
    throw "No verified KARZOUN-X Python environment was found in Downloads."
}

$PythonExe = Join-Path $OldWorkspace.FullName ".venv\Scripts\python.exe"
Write-Host "Python environment: $PythonExe" -ForegroundColor Green
& $PythonExe -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "The existing Python environment is inconsistent."
}

Write-Step "Checking local Ollama and NVIDIA telemetry"
Require-Command git
Require-Command ollama
try {
    $Tags = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 5
} catch {
    throw "Ollama is not responding at $OllamaBaseUrl. Start Ollama and retry."
}
$AvailableModels = @($Tags.models | ForEach-Object { $_.name })
if ($AvailableModels -notcontains $Model) {
    throw "Required model '$Model' is not installed locally."
}

$NvidiaSmi = Resolve-NvidiaSmi
if ($null -ne $NvidiaSmi) {
    $NvidiaDir = Split-Path -Parent $NvidiaSmi
    if (($env:PATH -split ";") -notcontains $NvidiaDir) {
        $env:PATH = "$NvidiaDir;$env:PATH"
    }
    Write-Host "NVIDIA telemetry available: $NvidiaSmi" -ForegroundColor Green
} else {
    Write-Host "nvidia-smi was not found; GPU metrics will be recorded as unavailable." -ForegroundColor Yellow
}

Write-Step "Preparing a clean current-main workspace"
if (Test-Path $RunRoot) {
    Set-Location $RunRoot
    & git fetch origin main
    if ($LASTEXITCODE -ne 0) { throw "git fetch failed." }
    & git reset --hard origin/main
    if ($LASTEXITCODE -ne 0) { throw "git reset failed." }
    & git clean -fd
    if ($LASTEXITCODE -ne 0) { throw "git clean failed." }
} else {
    & git clone --depth 1 --branch main $RepoUrl $RunRoot
    if ($LASTEXITCODE -ne 0) { throw "git clone failed." }
    Set-Location $RunRoot
}

$SourceCommit = (& git rev-parse HEAD).Trim()
Write-Host "Source commit: $SourceCommit" -ForegroundColor Green
$env:PYTHONPATH = Join-Path $RunRoot "src"

Write-Step "Installing the pinned Phase 8 resource sampler"
& $PythonExe -m pip install --disable-pip-version-check -r requirements-phase8.txt
if ($LASTEXITCODE -ne 0) { throw "Phase 8 resource dependency installation failed." }
& $PythonExe -m pip check
if ($LASTEXITCODE -ne 0) { throw "Python environment became inconsistent after installation." }

Write-Step "Running repository quality checks"
& $PythonExe -m ruff check .
if ($LASTEXITCODE -ne 0) { throw "Ruff failed." }
& $PythonExe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
Write-Host "Quality checks passed." -ForegroundColor Green

Write-Step "Preparing cold-start measurement"
Request-ModelUnload
Start-Sleep -Seconds 2
Write-Host "Model unload verified. First measured call is the cold-start case." -ForegroundColor Green

Write-Step "Recording local execution environment"
$ResultDir = Join-Path $RunRoot "results\phase8"
New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null
$EnvironmentLines = @(
    "KARZOUN-X Phase 8 local resource benchmark environment",
    "timestamp_local=$((Get-Date).ToString('o'))",
    "source_commit=$SourceCommit",
    "python=$(& $PythonExe --version 2>&1)",
    "ollama=$(& ollama --version 2>&1)",
    "model=$Model",
    "ollama_base_url=$OllamaBaseUrl",
    "psutil=$(& $PythonExe -c 'import psutil; print(psutil.__version__)' 2>&1)",
    "nvidia_smi=$($NvidiaSmi ?? 'unavailable')"
)
$EnvironmentLines | Set-Content -Path (Join-Path $ResultDir "environment.txt") -Encoding utf8
& $PythonExe -m pip freeze | Set-Content -Path (Join-Path $ResultDir "pip-freeze.txt") -Encoding utf8
Get-FileHash requirements-phase8.txt -Algorithm SHA256 |
    ForEach-Object { "requirements_phase8_sha256=$($_.Hash.ToLower())" } |
    Add-Content -Path (Join-Path $ResultDir "environment.txt") -Encoding utf8

Write-Step "Running Phase 8 with live progress and resource sampling"
$RunLog = Join-Path $RunRoot "results-phase8.log"
& $PythonExe scripts/run_phase8_resource_benchmark.py --base-url $OllamaBaseUrl --model $Model 2>&1 |
    Tee-Object -FilePath $RunLog
if ($LASTEXITCODE -ne 0) {
    throw "Phase 8 failed. The log is at $RunLog"
}

Write-Step "Committing machine-generated Phase 8 results"
& git config user.name "Mahmoud Karzoun"
& git config user.email "135722882+mkarson1997@users.noreply.github.com"
& git add results/phase8 results-phase8.log
$Changes = (& git status --porcelain) -join "`n"
if ([string]::IsNullOrWhiteSpace($Changes)) {
    throw "Phase 8 produced no result changes."
}
& git commit -m "results: record Phase 8 local resource benchmark"
if ($LASTEXITCODE -ne 0) { throw "git commit failed." }

Write-Step "Synchronizing with main and pushing results"
& git fetch origin main
if ($LASTEXITCODE -ne 0) { throw "git fetch failed before push." }
& git rebase origin/main
if ($LASTEXITCODE -ne 0) {
    & git rebase --abort
    throw "Results rebase conflicted. Results remain committed locally for inspection."
}
& git push origin HEAD:main
if ($LASTEXITCODE -ne 0) {
    $Branch = "phase8-results-" + (Get-Date -Format "yyyyMMdd-HHmmss")
    Write-Host "Direct main push was not accepted. Publishing $Branch instead." -ForegroundColor Yellow
    & git checkout -b $Branch
    if ($LASTEXITCODE -ne 0) { throw "Could not create results branch." }
    & git push -u origin $Branch
    if ($LASTEXITCODE -ne 0) { throw "Could not push results branch." }
    Write-Host "RESULT_BRANCH=$Branch" -ForegroundColor Yellow
} else {
    Write-Host "Results pushed to main." -ForegroundColor Green
}

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "KARZOUN-X PHASE 8 COMPLETE" -ForegroundColor Green
Write-Host "Workspace: $RunRoot"
Write-Host "Summary:   $RunRoot\results\phase8\summary.md"
Write-Host "===============================================" -ForegroundColor Green
