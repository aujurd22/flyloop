$targets = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -match 'flyloop\\worker|flyloop\\supervisor|_v7a_launch' }
foreach ($p in $targets) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Output ("killed leftover pid=" + $p.ProcessId)
}
Write-Output "done"
