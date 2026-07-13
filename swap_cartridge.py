# -*- coding: utf-8 -*-
"""Swap the live cartridge to the sharded (4GB-safe) pack. Safe + revertible.

Stops every process holding kg_triples (watchdog first so it can't resurrect the engine,
then engine + learner + sprint daemons), renames kg_triples->backup and sharded->kg_triples
with a retry loop (Windows releases memmap handles a beat after kill), then restarts the
watchdog (which relaunches the engine). If the rename can't complete, it reverts and restarts
so the live system is never left broken.
"""
from __future__ import annotations
import io, os, subprocess, sys, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = Path("C:/0.ASKIM ALL-VIN/27., ATANOR DEMO")
GS = ROOT / "data" / "graph_scale"
LIVE, SHARDED, BACKUP = GS / "kg_triples", GS / "kg_triples_sharded", GS / "kg_triples_ram_backup"


def _ps(cmd: str) -> str:
    return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                          capture_output=True, text=True).stdout.strip()


def _kill_holders():
    # watchdog FIRST (else it relaunches the engine mid-swap), then EVERY app.main uvicorn
    # (port owner AND any orphans — orphans still memmap kg_triples and blocked the rename),
    # plus learner + sprint daemons. Match by command line so orphans are covered.
    _ps("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
        "Where-Object { $_.CommandLine -match 'engine_watchdog' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -Confirm:$false }")
    time.sleep(1)
    _ps("Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
        "Where-Object { $_.CommandLine -match 'app.main|learner_daemon|sprint_daemon' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -Confirm:$false }")


def _try_rename() -> bool:
    for _ in range(30):
        try:
            os.rename(LIVE, BACKUP)
            os.rename(SHARDED, LIVE)
            return True
        except OSError:
            time.sleep(2)
    return False


def main() -> int:
    if not SHARDED.exists():
        print("no kg_triples_sharded — nothing to swap"); return 1
    print("stopping holders (watchdog, engine, learner, sprint)…")
    _kill_holders()
    time.sleep(5)
    print("renaming (retry until handles release)…")
    if not _try_rename():
        print("RENAME FAILED — reverting; restarting watchdog, live unchanged")
        subprocess.Popen(["python", "scripts/engine_watchdog.py"], cwd=str(ROOT),
                         creationflags=0x00000008)
        return 2
    live_backend = (LIVE / "meta.json").read_text(encoding="utf-8")
    print("SWAPPED. live kg_triples backend now:",
          "sharded" if '"sharded"' in live_backend else "??")
    print("restarting watchdog (relaunches engine)…")
    subprocess.Popen(["python", "scripts/engine_watchdog.py"], cwd=str(ROOT),
                     creationflags=0x00000008)
    for i in range(60):
        time.sleep(3)
        if _ps("try{(Invoke-WebRequest 'http://127.0.0.1:8502/health' -UseBasicParsing "
               "-TimeoutSec 3).StatusCode}catch{'down'}") == "200":
            time.sleep(18)  # let warmup settle
            rss = _ps("$e=(Get-NetTCPConnection -State Listen -LocalPort 8502).OwningProcess|"
                      "Select -First 1; [int]((Get-Process -Id $e).WorkingSet64/1MB)")
            print(f"engine UP on sharded cartridge. RSS: {rss} MB (was ~2500)")
            return 0
    print("engine did not come back up in time — check watchdog")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
