#!/usr/bin/env python3
"""Compatibility launcher for multi-seed PPO training.

Allows running from workspace root via:
  python scripts/21_train_ppo_multiseed.py ...

It forwards execution to:
  Mining Env/scripts/21_train_ppo_multiseed.py
"""

from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "Mining Env" / "scripts" / "21_train_ppo_multiseed.py"
    if not target.is_file():
        raise FileNotFoundError(f"Training script not found: {target}")
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
