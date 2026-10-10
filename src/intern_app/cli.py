"""Command line entry point.

`config` shows resolved settings, `status` reports what is stored and what has
been spent. Later phases add `fetch`, `extract`, `rank`, and `serve`.
"""

from __future__ import annotations

import argparse

from intern_app import __version__, db
from intern_app.config import settings
from intern_app.sources import quota


def _cmd_config(_: argparse.Namespace) -> int:
    """Print resolved settings and which credentials are present.

    Prints whether a key is set, never the key.
    """
    cfg = settings()
    print(f"intern-app {__version__}")
    print(f"database     {cfg.db_path}")
    print(f"model        {cfg.model}")
    print(f"prompts      {cfg.prompts_dir}")
    print("credentials:")
    for name in (
        "ANTHROPIC_API_KEY",
        "MUSE_API_KEY",
        "ADZUNA_APP_ID",
        "ADZUNA_APP_KEY",
        "USAJOBS_API_KEY",
        "USAJOBS_EMAIL",
    ):
        print(f"  {'set    ' if cfg.has(name) else 'missing'}  {name}")
    return 0


def _cmd_status(_: argparse.Namespace) -> int:
    """Report stored listings per source, remaining quota, and LLM spend."""
    cfg = settings()
    conn = db.connect()
    try:
        print(f"database {cfg.db_path}")

        rows = db.source_counts(conn)
        if not rows:
            print("\nNo listings stored yet.")
        else:
            print(f"\n{'source':<14}{'listings':>9}{'full text':>11}  last seen")
            for row in rows:
                print(
                    f"{row['source']:<14}{row['listings']:>9}"
                    f"{row['with_full_text'] or 0:>11}  {row['last_seen']}"
                )

        print(f"\n{'source':<14}{'quota left':>11}  last call")
        for source in sorted(quota.LIMITS):
            left = quota.remaining(conn, source)
            print(
                f"{source:<14}{'unlimited' if left is None else left:>11}  "
                f"{db.last_call_at(conn, source) or '-'}"
            )

        spend = db.llm_spend(conn)
        month = db.llm_spend(conn, days=30)
        print(
            f"\nLLM calls {spend['calls']} total, "
            f"{spend['input_tokens']:,} in / {spend['output_tokens']:,} out tokens, "
            f"${spend['cost_usd']:.4f} all time, ${month['cost_usd']:.4f} last 30 days"
        )
    finally:
        conn.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intern-app", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    config_cmd = sub.add_parser("config", help="show resolved settings and credential status")
    config_cmd.set_defaults(func=_cmd_config)

    status_cmd = sub.add_parser("status", help="show stored listings, quota left, and LLM spend")
    status_cmd.set_defaults(func=_cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
