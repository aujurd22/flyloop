Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -match 'flyloop|v7a|v5b|supervisor' } |
    Select-Object ProcessId, @{N = 'MB'; E = { [math]::Round($_.WorkingSetSize / 1MB) }},
        @{N = 'Cmd'; E = { $_.CommandLine.Substring(0, [Math]::Min(110, $_.CommandLine.Length)) }} |
    Format-Table -AutoSize -Wrap
