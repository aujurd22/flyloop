import subprocess

out = subprocess.run(
    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
     r"D:\djr82\flyloop\tests\_kill_all.ps1"],
    capture_output=True, text=True)
print(out.stdout)
print("cleared; relaunch next")
