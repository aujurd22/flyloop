$ports = 8769, 8770, 8771
$conns = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $ports -contains $_.LocalPort }
foreach ($c in $conns) {
    $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
    if ($p -and $p.ProcessName -like "python*") {
        Stop-Process -Id $p.Id -Force
        Write-Output ("killed pid=" + $p.Id + " port=" + $c.LocalPort)
    }
}
Write-Output "ports cleared"
