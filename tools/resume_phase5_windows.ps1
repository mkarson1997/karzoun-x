$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Model = "qwen3:14b-q4_K_M"
$OllamaBaseUrl = "http://127.0.0.1:11434"

function Write-Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Get-Sha256([string]$Path) {
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try {
            $bytes = $sha.ComputeHash($stream)
            return ([System.BitConverter]::ToString($bytes)).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $sha.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}

Write-Step "Finding the latest failed Phase 5 workspace"
$Workspace = Get-ChildItem -Path (Join-Path $env:USERPROFILE "Downloads") -Directory |
    Where-Object { $_.Name -like "karzoun-x-phase5-*" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $Workspace) {
    throw "No karzoun-x-phase5-* workspace was found in Downloads."
}

$RunRoot = $Workspace.FullName
Set-Location $RunRoot
Write-Host "Resuming workspace: $RunRoot"

$PythonExe = Join-Path $RunRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    throw "The latest workspace does not contain the expected virtual environment."
}

$SourceCommit = (& git rev-parse HEAD).Trim()
Write-Host "Source commit: $SourceCommit"

Write-Step "Installing the missing Windows-only pytest dependency"
$Wheelhouse = Join-Path $RunRoot "wheelhouse-windows"
$WheelManifest = Join-Path $RunRoot "dependency-wheel-manifest.sha256"
New-Item -ItemType Directory -Force -Path $Wheelhouse | Out-Null

& $PythonExe -m pip download --only-binary=:all: --no-deps "colorama==0.4.6" -d $Wheelhouse
if ($LASTEXITCODE -ne 0) {
    throw "Failed to download colorama==0.4.6."
}

$ManifestLines = New-Object System.Collections.Generic.List[string]
Get-ChildItem -Path $Wheelhouse -File | Sort-Object Name | ForEach-Object {
    $Hash = Get-Sha256 $_.FullName
    $ManifestLines.Add("$Hash  $($_.Name)")
}
$ManifestLines | Set-Content -Path $WheelManifest -Encoding ascii
Write-Host "Updated wheel SHA-256 manifest: $WheelManifest"

& $PythonExe -m pip install --no-index --find-links $Wheelhouse --no-deps "colorama==0.4.6"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install colorama==0.4.6 from the local wheelhouse."
}

& $PythonExe -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "The Python dependency set is still inconsistent."
}

$env:PYTHONPATH = Join-Path $RunRoot "src"

Write-Step "Running repository quality checks"
& $PythonExe -m ruff check .
if ($LASTEXITCODE -ne 0) {
    throw "Ruff failed. Phase 5 will not run."
}
& $PythonExe -m pytest -q
if ($LASTEXITCODE -ne 0) {
    throw "Tests failed. Phase 5 will not run."
}

Write-Step "Recording local execution environment"
New-Item -ItemType Directory -Force -Path "results\phase5" | Out-Null
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
$EnvironmentLines | Set-Content -Path "results\phase5\environment.txt" -Encoding utf8
Copy-Item $WheelManifest "results\phase5\dependency-wheel-manifest.sha256" -Force
& $PythonExe -m pip freeze | Set-Content -Path "results\phase5\pip-freeze.txt" -Encoding ascii

Write-Step "Running the frozen Phase 5 local-LLM benchmark"
$RunLog = Join-Path $RunRoot "results-phase5.log"
& $PythonExe scripts/run_phase5_local_llm.py --base-url $OllamaBaseUrl --model $Model 2>&1 |
    Tee-Object -FilePath $RunLog
if ($LASTEXITCODE -ne 0) {
    throw "Phase 5 benchmark failed. Files remain in $RunRoot for inspection."
}

Write-Step "Phase 5 completed"
Get-Content "results\phase5\summary.md"

Write-Step "Committing machine-generated Phase 5 results"
& git config user.name "Mahmoud Karzoun"
& git config user.email "135722882+mkarson1997@users.noreply.github.com"
& git add results/phase5 results-phase5.log
$HasChanges = (& git status --porcelain) -join "`n"
if (-not [string]::IsNullOrWhiteSpace($HasChanges)) {
    & git commit -m "results: record phase5 local LLM benchmark"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create the Phase 5 results commit."
    }

    Write-Step "Pushing Phase 5 results"
    & git push origin HEAD:main
    if ($LASTEXITCODE -ne 0) {
        $Branch = "phase5-local-results-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Host "Main advanced while the experiment was running. Pushing results to $Branch instead."
        & git branch $Branch
        & git push -u origin $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Results are complete locally but the GitHub push failed."
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
