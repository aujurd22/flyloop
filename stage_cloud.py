"""Stage a Linux-ready flyloop copy for the AutoDL node.

Copies flyloop package + sandbox_mem/flymemory + flypoet/train_v2.py into
stage_cloud/, patches out the Windows-only bits (ctypes windll RAM checks,
subprocess creationflags), verifies zero Windows-isms remain, tars it.
"""
import os, re, shutil, tarfile

SRC = r"D:\djr82\flyloop"
STG = r"D:\djr82\flyloop\stage_cloud"

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def wr(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

# --- fresh staging dir
if os.path.exists(STG):
    shutil.rmtree(STG)
os.makedirs(os.path.join(STG, "flyloop"))
os.makedirs(os.path.join(STG, "sandbox_mem", "flymemory"))
os.makedirs(os.path.join(STG, "flypoet"))

# --- copy package py files
for name in os.listdir(os.path.join(SRC, "flyloop")):
    if name.endswith(".py"):
        shutil.copy2(os.path.join(SRC, "flyloop", name),
                     os.path.join(STG, "flyloop", name))
# --- copy sandbox_mem (skip pycache + big seed pkl keeps db fresh-create)
for name in os.listdir(os.path.join(SRC, "sandbox_mem", "flymemory")):
    if name.endswith(".py"):
        shutil.copy2(os.path.join(SRC, "sandbox_mem", "flymemory", name),
                     os.path.join(STG, "sandbox_mem", "flymemory", name))
# --- flypoet GPT module
shutil.copy2(r"D:\djr82\flypoet\train_v2.py",
             os.path.join(STG, "flypoet", "train_v2.py"))

POSIX_RAM = ('def ram_avail_gb():\n'
             '    import os\n'
             "    return round(os.sysconf('SC_AVPHYS_PAGES') * "
             "os.sysconf('SC_PAGE_SIZE') / 2**30, 1)\n")

def patch(fname, subs):
    p = os.path.join(STG, "flyloop", fname)
    s = rd(p)
    for sub in subs:
        pat, rep = sub[0], sub[1]
        cnt = sub[2] if len(sub) > 2 else 1
        s2, n = re.subn(pat, rep, s, count=cnt, flags=re.S)
        assert n >= 1, f"{fname}: pattern not found: {pat[:60]}"
        s = s2
    wr(p, s)

ram_pat = (r"def ram_avail_gb\(\):.*?return (?:round\()?m\.ullAvailPhys / "
           r"2\*\*30(?:, 1\))?\n")
patch("worker.py", [(ram_pat, POSIX_RAM)])
patch("supervisor.py", [
    (ram_pat, POSIX_RAM),
    (r"creationflags=DETACHED \| CREATE_NO_WINDOW,\s*", ""),
    (r"ctypes\.windll\.kernel32\.SetThreadExecutionState\([^)]*\)",
     "pass  # POSIX node: no sleep to hold"),
    (r"creationflags=CREATE_NO_WINDOW,?\s*", " ", 0),
])
patch("resume.py", [(r"creationflags=0x08000000 \| 0x00000008,\s*"
                     r"# NO_WINDOW \| DETACHED", "")])

# --- verify no Windows-isms remain in staged package
awake = os.path.join(STG, "flyloop", "awake_guard.py")
if os.path.exists(awake):
    os.remove(awake)  # Windows sleep-guard, not referenced by the package
bad = []
for name in os.listdir(os.path.join(STG, "flyloop")):
    s = rd(os.path.join(STG, "flyloop", name))
    for tok in ("windll", "wintypes", "creationflags"):
        if tok in s:
            bad.append((name, tok))
print("windows-isms left:", bad if bad else "NONE")

with tarfile.open(os.path.join(STG, "flycloud.tar"), "w") as tf:
    for sub in ("flyloop", "sandbox_mem", "flypoet"):
        tf.add(os.path.join(STG, sub), arcname=sub)
print("staged:", STG, " tar bytes:", 
      os.path.getsize(os.path.join(STG, "flycloud.tar")))
