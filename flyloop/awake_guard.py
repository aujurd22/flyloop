"""Standalone sleep guard for the live run: holds ES_SYSTEM_REQUIRED
(0x80000001 = ES_CONTINUOUS | ES_SYSTEM_REQUIRED) for 11h, then exits.
Blocks idle sleep without touching the user's power plan."""
import ctypes
import time

ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
time.sleep(39600)
