param(
    [switch]$quiet,
    [switch]$noColor,
    [int]$port = 8000
)

$logDir = "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory $logDir | Out-Null }
$logFile = Join-Path $logDir ("run-" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

function Write-Log {
    param(
        [string]$level,
        [string]$message
    )
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:sszzz"
    $color = $null
    if (-not $noColor) {
        switch ($level) {
            "INFO"  { $color = "Green" }
            "WARN"  { $color = "Yellow" }
            "ERROR" { $color = "Red" }
        }
    }
    $out = "$ts [$level] $message"
    if ($quiet -and $level -eq "INFO") {
        Add-Content -Path $logFile -Value $out
    }
    else {
        if ($color) { Write-Host $out -ForegroundColor $color }
        else { Write-Host $out }
        Add-Content -Path $logFile -Value $out
    }
}

function Run-Cmd {
    param([string]$cmd)
    Write-Log "INFO" $cmd
    & cmd /c $cmd 2>&1 | Tee-Object -FilePath $logFile -Append
    return $LASTEXITCODE
}

trap { Write-Log "ERROR" "Aborted"; exit 2 }

Run-Cmd "git pull --ff-only"
if ($LASTEXITCODE -ne 0) { Write-Log "ERROR" "git pull failed"; exit 1 }

if (Test-Path "requirements.txt") {
    Run-Cmd "python -m pip install -r requirements.txt"
    if ($LASTEXITCODE -ne 0) { Write-Log "ERROR" "deps - pip install failed"; exit 1 }
}
elseif (Test-Path "package.json") {
    Run-Cmd "npm ci --ignore-scripts"
    if ($LASTEXITCODE -ne 0) { Write-Log "ERROR" "deps - npm install failed"; exit 1 }
}

$cmd = $null
if (Test-Path "start.sh") { $cmd = "bash start.sh" }
elseif (Test-Path "package.json") {
    try { if ((Get-Content package.json | ConvertFrom-Json).scripts.start) { $cmd = "npm start" } } catch {}
}
elseif (Test-Path "main.py") { $cmd = "python main.py" }
elseif (Test-Path "index.html") {
    if (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Id -eq (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue).OwningProcess }) {
        $pid = (Get-NetTCPConnection -LocalPort $port).OwningProcess
        Stop-Process -Id $pid -ErrorAction SilentlyContinue
        Write-Log "WARN" "Killed process on port $port"
    }
    $cmd = "python -m http.server $port"
}

if (-not $cmd) { Write-Log "ERROR" "No start command found"; exit 1 }
Run-Cmd $cmd
$status = $LASTEXITCODE
if ($status -eq 0) { Write-Log "INFO" "✓ SUCCESS" } else { Write-Log "ERROR" "✗ FAILED (code $status)" }
exit $status
