$ports = 49621, 49622, 49623
$conns = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $ports -contains $_.LocalPort }
foreach ($c in $conns) {
    $procId = $c.OwningProcess
    $p = Get-CimInstance Win32_Process -Filter "ProcessId = $procId" -ErrorAction SilentlyContinue
    Write-Output ("port=" + $c.LocalPort + " pid=" + $procId + " cmd=" + $p.CommandLine)
}
