# kill all flyloop workers/supervisors/launchers and the 3 sandbox services
$targets = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -match 'flyloop\worker|flyloop\supervisor|_launch|rsi0_g2_20260929_1618|v7c_20260929_1618' }
foreach ($p in $targets) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Output ("killed pid=" + $p.ProcessId)
}
Write-Output "all flyloop pair processes cleared"
