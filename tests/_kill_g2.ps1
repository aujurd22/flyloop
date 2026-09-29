# kill G2 supervisors/workers/services (keep V7C running)
$targets = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -match '_g2_launch|rsi0_g2_20260929_1555' }
foreach ($p in $targets) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Output ("killed pid=" + $p.ProcessId)
}
Write-Output "G2 cleared; V7C untouched"
