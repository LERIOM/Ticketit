"""Run from executor/: python -m scripts.seed_lab --database lab.sqlite3."""

import argparse
from pathlib import Path

from app.lab.seed import export_logs, seed


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset the simulated lab tables only.")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--logs", type=Path, help="Optional JSONL export destination.")
    args = parser.parse_args()
    if args.logs and args.logs.resolve() == args.database.resolve():
        parser.error("--logs must differ from --database")
    seed(args.database)
    if args.logs:
        args.logs.write_text(export_logs(args.database), encoding="utf-8")
    print("Laboratory initialized; audit and idempotency were not reset.")


if __name__ == "__main__":
    main()
