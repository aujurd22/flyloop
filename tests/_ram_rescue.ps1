Get-Process python* -ErrorAction SilentlyContinue |
    Where-Object { $_.WorkingSet64 -gt 50MB } |
    ForEach-Object {
        Write-Output ("killing pid=" + $_.Id + " mb=" + [math]::Round($_.WorkingSet64/1MB))
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
Start-Sleep 5
$free = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
Write-Output ("RAM avail: " + [math]::Round($free, 1) + " GB")
