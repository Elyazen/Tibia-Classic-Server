param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"

if ($Build -or -not (Test-Path "build\game.exe")) {
    Write-Host "Building server..."
    # Placeholder for Windows build command
    # mingw32-make -j4
}

$Global:TEST_DIR = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), [System.IO.Path]::GetRandomFileName())
Write-Host "Setting up test environment in $TEST_DIR"

New-Item -ItemType Directory -Force -Path "$TEST_DIR\bin" | Out-Null
New-Item -ItemType Directory -Force -Path "$TEST_DIR\data" | Out-Null
New-Item -ItemType Directory -Force -Path "$TEST_DIR\logs" | Out-Null

Copy-Item "build\game.exe" -Destination "$TEST_DIR\bin\" -ErrorAction SilentlyContinue

if (Test-Path "tibia.pem") {
    Copy-Item "tibia.pem" -Destination "$TEST_DIR\bin\"
}

$env:TIBIA_TEST_MODE = "1"

@"
binpath = "."
datapath = "../data"
logpath = "../logs"
mappath = "../data"
monsterpath = "../data"
savepath = "../data"
world = "Test"
"@ | Out-File "$TEST_DIR\bin\.tibia" -Encoding ASCII

Set-Location "$TEST_DIR\bin"

Write-Host "Starting server..."
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = ".\game.exe"
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo
$process.Start() | Out-Null

$process.Id | Out-File "..\server.pid" -Encoding ASCII

Write-Host "Server started with PID: $($process.Id)"

$ready = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient("localhost", 7171)
        if ($tcpClient.Connected) {
            $tcpClient.Close()
            $ready = $true
            Write-Host "Server is ready (connected to port)."
            break
        }
    } catch {
        # Ignore
    }

    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Host "ERROR: Server failed to start properly."
    $process.Kill()
}

Write-Host "Server is up and running."
