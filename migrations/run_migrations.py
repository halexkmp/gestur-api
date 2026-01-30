#!/usr/bin/env python3
"""
Run Aerich migrations once during deployment.
This script is intended to be executed by Vercel's installCommand so it runs
exactly once per deployment, before the serverless function is used.
"""
from __future__ import annotations

import subprocess
import sys


def main() -> int:
    print("[migrations] Starting Aerich upgrade...")
    try:
        # Execute `python -m aerich upgrade` using the current interpreter
        proc = subprocess.run(
            [sys.executable, "-m", "aerich", "upgrade"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.returncode != 0:
            # Surface stderr and fail the deployment to avoid schema drift
            err = proc.stderr.strip()
            print(f"[migrations] Aerich upgrade failed (code {proc.returncode}).")
            if err:
                print(err)
            return proc.returncode
        print("[migrations] Aerich migrations applied successfully.")
        return 0
    except Exception as e:
        print(f"[migrations] Unexpected error running migrations: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
