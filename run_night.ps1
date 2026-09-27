# flyloop overnight launcher: sandbox service (idempotent) + supervisor detached.
# monitor:  Get-Content <rundir>\STATUS.md -Wait
# stop:     New-Item <rundir>\STOP -ItemType File
$ErrorActionPreference = "Stop"
$Python  = "C:\Users\djr82\AppData\Local\Programs\Python\Python313\python.exe"
$Pythonw = "C:\Users\djr82\AppData\Local\Programs\Python\Python313\pythonw.exe"
$Root    = "D:\djr82\flyloop"

$RunId  = Get-Date -Format "yyyyMMdd_HHmm"
$RunDir = Join-Path $Root "runs\night_$RunId"
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

function Test-Port($p) {
  $c = New-Object Net.Sockets.TcpClient
  try { $c.Connect("127.0.0.1", $p); $c.Connected } catch { $false } finally { $c.Close() }
}

if (-not (Test-Port 8767)) {
  Start-Process -FilePath $Pythonw `
    -ArgumentList "mcp_v3.py","--http","--port","8767" `
    -WorkingDirectory "$Root\sandbox_mem\flymemory" -WindowStyle Hidden
}
$up = $false
foreach ($i in 1..40) { if (Test-Port 8767) { $up = $true; break }; Start-Sleep -Seconds 3 }
if (-not $up) { Write-Host "WARN: sandbox service not up; worker will degrade to local mirror" }

Start-Process -FilePath $Python `
  -ArgumentList "-m","flyloop.supervisor","--run-dir",$RunDir,"--duration-h","5" `
  -WorkingDirectory $Root -WindowStyle Hidden `
  -RedirectStandardOutput "$RunDir\supervisor.out.log" `
  -RedirectStandardError  "$RunDir\supervisor.err.log"

Write-Host "RUN DIR: $RunDir"
Write-Host "monitor: Get-Content '$RunDir\STATUS.md' -Wait"
Write-Host "stop:    New-Item '$RunDir\STOP' -ItemType File"
