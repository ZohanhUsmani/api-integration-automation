"""CLI entry point."""
import argparse
import json
from pathlib import Path

from .client import APIClient


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--output", default="out/items.json")
    ap.add_argument("--token", default=None)
    ap.add_argument("--strategy", default="page", choices=["page", "offset", "cursor"])
    args = ap.parse_args()

    auth = {"type": "bearer", "token": args.token} if args.token else {"type": "none"}
    client = APIClient(args.base, auth=auth)
    items = client.paginate(args.endpoint, strategy=args.strategy)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f"Fetched {len(items)} items -> {out}")


if __name__ == "__main__":
    main()
