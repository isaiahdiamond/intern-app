"""Command line entry point.

Phase 0 ships `config` only, so there is something runnable to confirm the layout
and the environment wiring. Later phases add `fetch`, `extract`, `rank`, `serve`.
"""

from __future__ import annotations

import argparse

from intern_app import __version__
from intern_app.config import settings


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intern-app", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    config_cmd = sub.add_parser("config", help="show resolved settings and credential status")
    config_cmd.set_defaults(func=_cmd_config)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
