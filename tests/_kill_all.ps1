# kill all flyloop workers/supervisors/launchers and the 3 sandbox services
$targets = Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -match 'flyloop\\worker|flyloop\\supervisor|_v7a_launch|_v5b_launch|mcp_v3\.py --http --port 8769|mcp_v3\.py --http --port 8770|mcp_v3\.py --http --port 8771' }
foreach ($p in $targets) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Output ("killed pid=" + $p.ProcessId)
}
Write-Output ("remaining flyloop python: " +
    (Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
     Where-Object { $_.CommandLine -match 'flyloop' }).Count)
