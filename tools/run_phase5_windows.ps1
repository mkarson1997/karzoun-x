$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoUrl = "https://github.com/mkarson1997/karzoun-x.git"
$Model = "qwen3:14b-q4_K_M"
$OllamaBaseUrl = "http://127.0.0.1:11434"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunRoot = Join-Path $env:USERPROFILE "Downloads\karzoun-x-phase5-$Timestamp"

function Write-Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Require-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function Resolve-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            & py -3.11 -c "import sys; assert sys.version_info >= (3, 11)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return @("py", "-3.11")
            }
        } catch {}
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
        if ($LASTEXITCODE -eq 0) {
            return @("python")
        }
    }

    throw "Python 3.11 or newer is required."
}

function Invoke-Python([string[]]$PythonCommand, [string[]]$Arguments) {
    $exe = $PythonCommand[0]
    $prefix = @()
    if ($PythonCommand.Count -gt 1) {
        $prefix = $PythonCommand[1..($PythonCommand.Count - 1)]
    }
    & $exe @prefix @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

Write-Step "Checking required tools"
Require-Command git
Require-Command ollama
$PythonCommand = Resolve-Python

Write-Step "Checking local Ollama service"
$OllamaReady = $false
try {
    $null = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 5
    $OllamaReady = $true
} catch {
    Write-Host "Ollama is installed but the API is not responding. Starting ollama serve..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        try {
            $null = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 3
            $OllamaReady = $true
            break
        } catch {}
    }
}
if (-not $OllamaReady) {
    throw "Ollama API did not become available at $OllamaBaseUrl."
}

Write-Step "Checking required model: $Model"
$Models = (& ollama list) -join "`n"
if ($Models -notmatch [regex]::Escape($Model)) {
    Write-Host "Model is not present locally. Pulling $Model now. This can take a while."
    & ollama pull $Model
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to pull Ollama model $Model."
    }
} else {
    Write-Host "Model found locally."
}

Write-Step "Cloning a clean research workspace"
& git clone --depth 1 $RepoUrl $RunRoot
if ($LASTEXITCODE -ne 0) {
    throw "Git clone failed."
}
Set-Location $RunRoot
$SourceCommit = (& git rev-parse HEAD).Trim()
Write-Host "Source commit: $SourceCommit"

Write-Step "Creating isolated Python environment"
$VenvPath = Join-Path $RunRoot ".venv"
Invoke-Python $PythonCommand @("-m", "venv", $VenvPath)
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    throw "Virtual environment Python was not created."
}

& $PythonExe -m pip install --upgrade "pip==26.2.1"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to set the pinned pip version."
}
& $PythonExe -m pip install --require-hashes --only-binary=:all: --no-deps -r requirements-ci.lock
if ($LASTEXITCODE -ne 0) {
    throw "Hash-verified dependency installation failed."
}

$env:PYTHONPATH = Join-Path $RunRoot "src"

Write-Step "Running repository quality checks"
& $PythonExe -m ruff check .
if ($LASTEXITCODE -ne 0) {
    throw "Ruff failed. Phase 5 will not run on a dirty code state."
}
& $PythonExe -m pytest -q
if ($LASTEXITCODE -ne 0) {
    throw "Tests failed. Phase 5 will not run."
}

Write-Step "Recording local execution environment"
$EnvironmentLines = New-Object System.Collections.Generic.List[string]
$EnvironmentLines.Add("KARZOUN-X Phase 5 local execution environment")
$EnvironmentLines.Add("timestamp_local=$((Get-Date).ToString('o'))")
$EnvironmentLines.Add("source_commit=$SourceCommit")
$EnvironmentLines.Add("python=$(& $PythonExe --version 2>&1)")
$EnvironmentLines.Add("ollama=$(& ollama --version 2>&1)")
$EnvironmentLines.Add("model=$Model")
$EnvironmentLines.Add("ollama_base_url=$OllamaBaseUrl")
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $GpuInfo = & nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1
    foreach ($Line in $GpuInfo) {
        $EnvironmentLines.Add("gpu=$Line")
    }
} else {
    $EnvironmentLines.Add("gpu=nvidia-smi unavailable")
}
New-Item -ItemType Directory -Force -Path "results\phase5" | Out-Null
$EnvironmentLines | Set-Content -Path "results\phase5\environment.txt" -Encoding utf8

Write-Step "Running the frozen Phase 5 local-LLM benchmark"
$RunLog = Join-Path $RunRoot "results-phase5.log"
& $PythonExe scripts/run_phase5_local_llm.py --base-url $OllamaBaseUrl --model $Model 2>&1 |
    Tee-Object -FilePath $RunLog
if ($LASTEXITCODE -ne 0) {
    throw "Phase 5 benchmark failed. Partial files remain in $RunRoot for inspection."
}

Write-Step "Phase 5 completed"
Get-Content "results\phase5\summary.md"

Write-Step "Committing machine-generated Phase 5 results"
& git add results/phase5 results-phase5.log
$HasChanges = (& git status --porcelain) -join "`n"
if ([string]::IsNullOrWhiteSpace($HasChanges)) {
    Write-Host "No result changes were produced."
} else {
    & git config user.name "Mahmoud Karzoun"
    & git config user.email "135722882+mkarson1997@users.noreply.github.com"
    & git commit -m "results: record phase5 local LLM benchmark"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the Phase 5 results commit."
    }

    Write-Step "Pushing results to GitHub"
    & git push origin HEAD:main
    if ($LASTEXITCODE -ne 0) {
        $Branch = "phase5-local-results-$Timestamp"
        Write-Host "Direct push to main was not accepted. Pushing the same commit to $Branch instead."
        & git branch $Branch
        & git push -u origin $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Results are complete locally but GitHub push failed."
            Write-Host "Local workspace: $RunRoot"
            exit 2
        }
        Write-Host "Results branch pushed: $Branch"
    } else {
        Write-Host "Results pushed to main successfully."
    }
}

Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "KARZOUN-X PHASE 5 COMPLETE" -ForegroundColor Green
Write-Host "Workspace: $RunRoot"
Write-Host "Summary:   $RunRoot\results\phase5\summary.md"
Write-Host "Raw data:  $RunRoot\results\phase5\raw_responses.jsonl"
Write-Host "===============================================" -ForegroundColor Green
