# foreground smoke: N cycles against the running sandbox service
param([int]$Cycles = 60)
$Python = "C:\Users\djr82\AppData\Local\Programs\Python\Python313\python.exe"
$Root   = "D:\djr82\flyloop"
Set-Location $Root
& $Python -m flyloop.worker --run-dir "runs\smoke_$([DateTime]::Now.ToString('HHmmss'))" `
  --max-cycles $Cycles --duration-h 1
