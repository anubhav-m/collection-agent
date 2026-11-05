# Nightly job: extract promises -> load SQLite -> write reports. Stops at the first failed
# step, logs each step with its timing, writes run.json, and exits non-zero on failure.
# Usage (from anywhere):  powershell -File scripts\nightly.ps1 [-Extractor llm|regex] [-AsOf 2026-11-05]
param(
    [ValidateSet("llm", "regex")] [string] $Extractor = "llm",
    [string] $AsOf = (Get-Date -Format "yyyy-MM-dd"),
    [string] $NightlyDir = (Join-Path $PSScriptRoot "..\reports\nightly")
)
$ErrorActionPreference = "Stop"
$Backend = Join-Path $PSScriptRoot "..\backend"
$Python = if ($env:NIGHTLY_PYTHON) { $env:NIGHTLY_PYTHON } else { Join-Path $Backend ".venv\Scripts\python.exe" }
$RunId = "{0}_{1}" -f $AsOf, (Get-Date -Format "HHmmss")
$RunDir = Join-Path $NightlyDir $RunId
New-Item -ItemType Directory -Force $RunDir | Out-Null
$RunDir = (Resolve-Path $RunDir).Path; $NightlyDir = (Resolve-Path $NightlyDir).Path
$Log = Join-Path $RunDir "nightly.log"
$Inv = [Globalization.CultureInfo]::InvariantCulture
$Utf8 = New-Object System.Text.UTF8Encoding $false   # no BOM, so Python can parse the JSON
$env:PYTHONIOENCODING = "utf-8"

function Stamp { (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ") }
function Write-Log([string] $Text) {
    $line = "[{0}] {1}" -f (Stamp), $Text
    Write-Host $line
    [IO.File]::AppendAllText($Log, $line + [Environment]::NewLine, $Utf8)
}
function Invoke-Step([string] $Name, [string[]] $Arguments) {
    Write-Log "START $Name"
    $timer = [Diagnostics.Stopwatch]::StartNew()
    # Native stderr must not become a terminating error in Windows PowerShell 5.1.
    $ErrorActionPreference = "Continue"
    & $Python @Arguments 2>&1 | ForEach-Object { Write-Log "  $Name | $_" }
    $code = $LASTEXITCODE
    $seconds = [math]::Round($timer.Elapsed.TotalSeconds, 2)
    $status = if ($code -eq 0) { "success" } else { "failed" }
    Write-Log ("END {0} status={1} exit={2} seconds={3}" -f $Name, $status, $code, $seconds.ToString($Inv))
    [ordered]@{ name = $Name; status = $status; exit_code = $code; seconds = $seconds }
}

$Steps = @(
    @{ name = "extract"; args = @("-m", "app.extraction.run_stored", "--extractor", $Extractor, "--summary", (Join-Path $RunDir "extraction.json")) },
    @{ name = "load"; args = @("-m", "app.reports.load_cli", "--as-of", $AsOf, "--extractor", $Extractor, "--out", $RunDir) },
    @{ name = "reports"; args = @("-m", "app.reports.report_cli", "--as-of", $AsOf, "--out", $RunDir) }
)
$started = Stamp; $results = @(); $failed = $null; $exitCode = 0
Write-Log "nightly run $RunId (as of $AsOf, extractor $Extractor)"
Push-Location $Backend
try {
    if (-not (Test-Path $Python)) { throw "python not found at $Python" }
    foreach ($step in $Steps) {
        $result = Invoke-Step $step.name $step.args
        $results += $result
        if ($result.exit_code -ne 0) { $failed = $step.name; $exitCode = $result.exit_code; break }
    }
} catch {
    Write-Log "ERROR $($_.Exception.Message)"
    if (-not $failed) { $failed = "setup" }; $exitCode = 1
} finally { Pop-Location }
$status = if ($exitCode -eq 0) { "success" } else { "failed" }
$run = [ordered]@{ run_id = $RunId; as_of = $AsOf; status = $status; started_at = $started;
    finished_at = (Stamp); failed_step = $failed; exit_code = $exitCode; steps = @($results) }
$json = ConvertTo-Json -InputObject $run -Depth 5
[IO.File]::WriteAllText((Join-Path $RunDir "run.json"), $json, $Utf8)
[IO.File]::WriteAllText((Join-Path $NightlyDir "last_run.json"), $json, $Utf8)
Write-Log "FINISHED status=$status exit=$exitCode output=$RunDir"
exit $exitCode
