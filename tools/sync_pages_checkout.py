"""Copy the verified public site into the existing GitHub Pages checkout.

Only tracked site content is synchronized. Git metadata and Pages configuration
stay in the destination checkout.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "source/site").resolve()
KEEP = {".gitattributes", ".nojekyll"}


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(cwd), *args], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    dest = args.destination.resolve(strict=True)
    if not (dest / ".git").exists() or "yasojima/yasojima.github.io.git" not in git(dest, "remote", "get-url", "origin"):
        parser.error("Destination must be the existing yasojima.github.io checkout")
    if git(dest, "status", "--porcelain"):
        parser.error("Destination has uncommitted changes")
    source_files = {p.relative_to(SOURCE).as_posix(): p for p in SOURCE.rglob("*") if p.is_file()}
    tracked = set(git(dest, "ls-files").splitlines())
    copied = 0
    removed = 0
    for rel, source in source_files.items():
        target = (dest / rel).resolve()
        if not target.is_relative_to(dest):
            raise ValueError(f"Destination escaped checkout: {rel}")
        if target.exists() and target.read_bytes() == source.read_bytes():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied += 1
    for rel in tracked - source_files.keys() - KEEP:
        if rel.startswith(".github/"):
            continue
        target = (dest / rel).resolve()
        if not target.is_relative_to(dest):
            raise ValueError(f"Deletion escaped checkout: {rel}")
        if target.is_file():
            target.unlink()
            removed += 1
    print(f"copied={copied} removed={removed} source_files={len(source_files)}")


if __name__ == "__main__":
    main()
