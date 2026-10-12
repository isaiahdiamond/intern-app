"""Command line entry point.

`config` shows resolved settings, `status` reports what is stored and what has
been spent, `serve` runs the local web app. Later phases add `fetch` and
`extract`.
"""

from __future__ import annotations

import argparse

from intern_app import __version__, db, profile
from intern_app.config import MissingConfigError, settings
from intern_app.sources import adzuna, github_repos, linkedin_mail, muse, quota, usajobs


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
        "YAHOO_EMAIL",
        "YAHOO_APP_PASSWORD",
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


def _cmd_fetch(args: argparse.Namespace) -> int:
    """Pull listings for my profile roles and store them."""
    conn = db.connect()
    try:
        roles = profile.load_role_names(conn)
        if not roles:
            print("No roles yet. Run `intern-app serve` and complete onboarding first.")
            return 1

        print(f"Fetching for {len(roles)} roles: {', '.join(roles)}")

        if args.source in ("all", "muse"):
            try:
                listings = muse.fetch_muse(conn, roles, max_pages=args.max_pages)
                inserted, updated = db.upsert_listings(conn, listings)
                print(f"muse: {len(listings)} matched, {inserted} new, {updated} already seen")
                left = quota.remaining(conn, muse.SOURCE)
                print(
                    f"muse: {db.calls_in_last(conn, muse.SOURCE, days=1)} calls today, {left} left"
                )
                if left == 0:
                    print("muse: budget spent, so this run stopped early. Try again tomorrow.")
            except quota.QuotaExceededError as exc:
                print(f"muse: skipped — {exc}")

        if args.source in ("all", "usajobs"):
            try:
                federal = usajobs.fetch_usajobs(conn, roles)
                inserted, updated = db.upsert_listings(conn, federal)
                print(f"usajobs: {len(federal)} matched, {inserted} new, {updated} already seen")
            except quota.QuotaExceededError as exc:
                print(f"usajobs: skipped — {exc}")
            except MissingConfigError as exc:
                print(f"usajobs: skipped — {exc}")

        if args.source in ("all", "adzuna"):
            try:
                discovered = adzuna.fetch_adzuna(conn, roles)
                inserted, updated = db.upsert_listings(conn, discovered)
                print(f"adzuna: {len(discovered)} matched, {inserted} new, {updated} already seen")
                print(f"adzuna: {quota.remaining(conn, adzuna.SOURCE)} calls left in budget")
            except quota.QuotaExceededError as exc:
                print(f"adzuna: skipped — {exc}")
            except MissingConfigError as exc:
                print(f"adzuna: skipped — {exc}")

        if args.source in ("all", "mail"):
            try:
                alerted = linkedin_mail.fetch_linkedin_mail(conn)
                inserted, updated = db.upsert_listings(conn, alerted)
                print(f"linkedin mail: {len(alerted)} jobs, {inserted} new, {updated} already seen")
            except quota.QuotaExceededError as exc:
                print(f"linkedin mail: skipped — {exc}")
            except MissingConfigError as exc:
                print(f"linkedin mail: skipped — {exc}")
            except OSError as exc:
                print(f"linkedin mail: mailbox unreachable — {type(exc).__name__}")

        if args.source in ("all", "repos"):
            try:
                found = github_repos.fetch_github_repos(conn, roles)
                inserted, updated = db.upsert_listings(conn, found)
                print(f"repos: {len(found)} US/remote, {inserted} new, {updated} already seen")
                boards = conn.execute("SELECT COUNT(*) FROM ats_boards").fetchone()[0]
                print(f"repos: {boards} ATS boards known")
            except quota.QuotaExceededError as exc:
                print(f"repos: skipped — {exc}")
    finally:
        conn.close()
    return 0


def _cmd_classify(args: argparse.Namespace) -> int:
    """Give every company we hold listings for an industry."""
    from intern_app.llm import classify, client

    if not client.have_api_key():
        print("ANTHROPIC_API_KEY is not set. Add it to .env to classify industries.")
        return 1

    conn = db.connect()
    try:
        pending = db.companies_needing_industry(conn)
        if not pending:
            print("Every company already has an industry.")
            return 0

        # $0.0163 per batch of 25 on the default model, measured over 49 real
        # calls that classified 1,219 companies for $0.7986. An earlier figure
        # of $0.011 came from a 6-company batch and under-quoted a full run by a
        # third, so this is taken from batches of the size actually sent.
        # Printed up front because a repo fetch can bring in a thousand new
        # companies at once.
        batches = -(-len(pending) // classify.BATCH_SIZE)
        estimate = batches * 0.0165
        print(f"{len(pending)} companies to classify: {batches} calls, about ${estimate:.2f}")
        if not args.yes and estimate > 0.10:
            answer = input("Continue? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("Nothing classified.")
                return 0

        print(f"Classifying {len(pending)} companies...")
        assigned = classify.classify_companies(conn, pending)
        for name, industry in sorted(assigned.items())[:15]:
            print(f"  {industry:<28} {name}")
        if len(assigned) > 15:
            print(f"  ... and {len(assigned) - 15} more")

        spend = db.llm_spend(conn, days=1)
        print(f"\ncost today: ${spend['cost_usd']:.4f} over {spend['calls']} calls")
    finally:
        conn.close()
    return 0


def _cmd_describe(args: argparse.Namespace) -> int:
    """Collect the full text of every listing on a board that publishes one."""
    from intern_app.sources import ats_detail

    conn = db.connect()
    try:
        pending = ats_detail.listings_needing_description(conn, limit=args.limit)
        if not pending:
            print("Every reachable posting already has its full text.")
            return 0

        print(f"{len(pending)} postings to fetch from greenhouse, lever and ashby")
        found = ats_detail.collect_descriptions(conn, limit=args.limit)
        print(
            f"{found['tried']} tried: {found['stored']} stored, "
            f"{found['empty']} empty, {found['failed']} failed"
        )
        return 0
    finally:
        conn.close()


def _cmd_pages(args: argparse.Namespace) -> int:
    """Read posting pages on hosts that publish no board API."""
    from intern_app.sources import posting_page

    conn = db.connect()
    try:
        pending = posting_page.listings_needing_page(conn, limit=args.limit)
        if not pending:
            print("Every reachable posting page has been tried.")
            return 0

        print(f"{len(pending)} posting pages to try, {posting_page.HOST_DELAY}s between hosts")
        found = posting_page.collect_pages(conn, limit=args.limit)
        print(
            f"{found['tried']} tried: {found['stored']} stored, {found['empty']} with no "
            f"description, {found['refused']} refused, {found['blocked']} blocked by "
            f"robots.txt, {found['failed']} failed"
        )
        for row in conn.execute(
            "SELECT host, reason, COUNT(*) n FROM page_misses GROUP BY host, reason"
            " ORDER BY n DESC LIMIT 8"
        ):
            print(f"  {row['n']:>5}  {row['reason']:<26} {row['host']}")
        return 0
    finally:
        conn.close()


def _cmd_read(args: argparse.Namespace) -> int:
    """Read each collected posting for its level, degree, term and experience."""
    from intern_app.llm import client, postings

    if not client.have_api_key():
        print("ANTHROPIC_API_KEY is not set. Add it to .env to read postings.")
        return 1

    conn = db.connect()
    try:
        pending = postings.listings_with_unread_descriptions(conn, limit=args.limit)
        if not pending:
            print("Every collected posting has been read already.")
            return 0

        # About $0.0015 each on Haiku, measured over real postings.
        estimate = len(pending) * 0.0015
        print(f"{len(pending)} postings to read on {postings.MODEL}, about ${estimate:.2f}")
        needs_confirming = not args.yes and estimate > 0.10
        if needs_confirming and input("Continue? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Nothing read.")
            return 0

        read = failed = 0
        for row in pending:
            try:
                postings.read_posting(conn, row)
                read += 1
            # One bad posting must not end a run of nine hundred.
            except Exception as exc:
                failed += 1
                print(f"  listing {row['id']}: {type(exc).__name__}")
        print(f"read {read} postings, {failed} failed")
        return 0
    finally:
        conn.close()


def _cmd_icons(args: argparse.Namespace) -> int:
    """Find each company's website and cache its favicon.

    Two passes. The apply url answers for the companies that post on their own
    site; the rest need Claude, because a company name is not a domain and the
    obvious guess is often a different company's site.
    """
    from intern_app import icons
    from intern_app.llm import client, domains

    conn = db.connect()
    try:
        pending = icons.companies_needing_icon(conn, limit=args.limit)
        if not pending:
            print("Every company has been looked up already.")
            return 0

        unresolved = [
            row["company"]
            for row in pending
            if not icons.domain_from_urls((row["urls"] or "").split("\n"))
        ]
        resolved: dict[str, str] = {}

        if unresolved and not args.no_llm:
            if not client.have_api_key():
                print("ANTHROPIC_API_KEY is not set, so only apply-url domains can be used.")
            else:
                calls = -(-len(unresolved) // domains.BATCH_SIZE)
                estimate = calls * 0.02
                print(
                    f"{len(pending)} companies, {len(unresolved)} needing Claude: "
                    f"{calls} calls, about ${estimate:.2f}"
                )
                needs_confirming = not args.yes and estimate > 0.10
                answer = input("Continue? [y/N] ").strip().lower() if needs_confirming else "y"
                if answer not in ("y", "yes"):
                    print("Nothing fetched.")
                    return 0
                resolved = domains.resolve_domains(conn, unresolved)
                print(f"Claude placed {len(resolved)} of {len(unresolved)} companies")

        found = icons.collect_icons(conn, limit=args.limit, domains=resolved)
        print(
            f"{found['companies']} companies: {found['icons']} icons, "
            f"{found['no_icon']} with no icon, {found['no_domain']} with no domain"
        )
        return 0
    finally:
        conn.close()


def _cmd_clean(args: argparse.Namespace) -> int:
    """Read every unread title into a role, a level, a degree and a term."""
    from intern_app.llm import client, titles

    if not client.have_api_key():
        print("ANTHROPIC_API_KEY is not set. Add it to .env to clean titles.")
        return 1

    conn = db.connect()
    try:
        pending = db.listings_needing_clean_title(conn, limit=args.limit)
        if not pending:
            print("Every title has been read already.")
            return 0

        # $0.0425 per batch of 40, measured over real batches. Titles are the
        # most expensive LLM step in the app because every listing needs one.
        batches = -(-len(pending) // titles.BATCH_SIZE)
        estimate = batches * 0.0425
        print(f"{len(pending)} titles to read: {batches} calls, about ${estimate:.2f}")
        needs_confirming = not args.yes and estimate > 0.10
        if needs_confirming and input("Continue? [y/N] ").strip().lower() not in ("y", "yes"):
            print("Nothing read.")
            return 0

        stored = titles.clean_titles(conn, pending)
        print(f"read {stored} titles")

        for row in conn.execute(
            "SELECT level, COUNT(*) n FROM listing_details GROUP BY level ORDER BY n DESC"
        ):
            print(f"  {row['n']:>5}  {row['level']}")

        spend = db.llm_spend(conn, days=1)
        print(f"\ncost today: ${spend['cost_usd']:.4f} over {spend['calls']} calls")
    finally:
        conn.close()
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    """Run the local web app, which is where onboarding and the dashboard live."""
    import uvicorn

    print(f"intern-app running at http://{args.host}:{args.port}")
    uvicorn.run("intern_app.server.app:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intern-app", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    config_cmd = sub.add_parser("config", help="show resolved settings and credential status")
    config_cmd.set_defaults(func=_cmd_config)

    status_cmd = sub.add_parser("status", help="show stored listings, quota left, and LLM spend")
    status_cmd.set_defaults(func=_cmd_status)

    fetch_cmd = sub.add_parser("fetch", help="pull listings for my profile roles")
    fetch_cmd.add_argument(
        "--source",
        choices=("all", "muse", "repos", "usajobs", "mail", "adzuna"),
        default="all",
        help="which sources to pull from (default all)",
    )
    fetch_cmd.add_argument(
        "--max-pages",
        type=int,
        default=8,
        help="pages to read per category and level, 20 listings each (default 8)",
    )
    fetch_cmd.set_defaults(func=_cmd_fetch)

    classify_cmd = sub.add_parser("classify", help="assign an industry to each company")
    classify_cmd.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    classify_cmd.set_defaults(func=_cmd_classify)

    clean_cmd = sub.add_parser("clean", help="read titles into role, level, degree and term")
    clean_cmd.add_argument("--limit", type=int, default=0, help="only read this many (0 means all)")
    clean_cmd.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    clean_cmd.set_defaults(func=_cmd_clean)

    icons_cmd = sub.add_parser("icons", help="cache a favicon for each company")
    icons_cmd.add_argument("--limit", type=int, default=0, help="only do this many (0 means all)")
    icons_cmd.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    icons_cmd.add_argument(
        "--no-llm", action="store_true", help="only use domains found in apply urls"
    )
    icons_cmd.set_defaults(func=_cmd_icons)

    describe_cmd = sub.add_parser("describe", help="collect full postings from ATS APIs")
    describe_cmd.add_argument("--limit", type=int, default=0, help="only do this many")
    describe_cmd.set_defaults(func=_cmd_describe)

    pages_cmd = sub.add_parser("pages", help="read posting pages where no board API exists")
    pages_cmd.add_argument("--limit", type=int, default=0, help="only try this many")
    pages_cmd.set_defaults(func=_cmd_pages)

    read_cmd = sub.add_parser("read", help="read collected postings for level and degree")
    read_cmd.add_argument("--limit", type=int, default=0, help="only read this many")
    read_cmd.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    read_cmd.set_defaults(func=_cmd_read)

    serve_cmd = sub.add_parser("serve", help="run the local web app")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8000)
    serve_cmd.add_argument("--reload", action="store_true", help="restart on code changes")
    serve_cmd.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
