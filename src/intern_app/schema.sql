-- intern-app schema. Applied by db.connect(); every statement is idempotent.
--
-- Tables:
--   listings    one row per posting, deduped on url
--   api_calls   one row per outbound HTTP call, for quota enforcement
--   llm_calls   one row per Claude call, with tokens and computed cost

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS listings (
    id          INTEGER PRIMARY KEY,
    url         TEXT    NOT NULL UNIQUE,   -- the dedupe key
    title       TEXT    NOT NULL,
    company     TEXT    NOT NULL,
    location    TEXT    NOT NULL DEFAULT '',
    description TEXT    NOT NULL DEFAULT '',
    posted_at   TEXT    NOT NULL DEFAULT '',
    source      TEXT    NOT NULL,
    full_text   INTEGER NOT NULL CHECK (full_text IN (0, 1)),
    first_seen  TEXT    NOT NULL,
    last_seen   TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS listings_source_idx ON listings (source);
CREATE INDEX IF NOT EXISTS listings_full_text_idx ON listings (full_text);
CREATE INDEX IF NOT EXISTS listings_first_seen_idx ON listings (first_seen DESC);

-- One row per outbound API call. `sources.quota` counts rows in a window to
-- decide whether a source may call again, so this must be written for every
-- attempt, including failures: a failed call still consumes quota.
CREATE TABLE IF NOT EXISTS api_calls (
    id          INTEGER PRIMARY KEY,
    source      TEXT    NOT NULL,
    endpoint    TEXT    NOT NULL DEFAULT '',
    called_at   TEXT    NOT NULL,
    status_code INTEGER,
    ok          INTEGER NOT NULL CHECK (ok IN (0, 1)),
    error       TEXT    NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS api_calls_source_time_idx ON api_calls (source, called_at DESC);

-- One row per Claude call. cost_usd is computed at write time from the token
-- counts and the price table in llm.pricing, so a later price change does not
-- silently rewrite history.
CREATE TABLE IF NOT EXISTS llm_calls (
    id                  INTEGER PRIMARY KEY,
    prompt_name         TEXT    NOT NULL,
    model               TEXT    NOT NULL,
    listing_id          INTEGER REFERENCES listings (id) ON DELETE SET NULL,
    called_at           TEXT    NOT NULL,
    input_tokens        INTEGER NOT NULL DEFAULT 0,
    output_tokens       INTEGER NOT NULL DEFAULT 0,
    cache_read_tokens   INTEGER NOT NULL DEFAULT 0,
    cache_write_tokens  INTEGER NOT NULL DEFAULT 0,
    cost_usd            REAL    NOT NULL DEFAULT 0.0,
    request_id          TEXT    NOT NULL DEFAULT '',
    input_text          TEXT    NOT NULL DEFAULT '',
    output_text         TEXT    NOT NULL DEFAULT '',
    ok                  INTEGER NOT NULL CHECK (ok IN (0, 1)),
    error               TEXT    NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS llm_calls_time_idx ON llm_calls (called_at DESC);
CREATE INDEX IF NOT EXISTS llm_calls_listing_idx ON llm_calls (listing_id);

-- Onboarding, added in phase 1. One local user for now, so `profile` holds at
-- most one row and `id` is pinned to 1 by a CHECK.
CREATE TABLE IF NOT EXISTS profile (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    school     TEXT NOT NULL DEFAULT '',
    major      TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profile_roles (
    id     INTEGER PRIMARY KEY,
    role   TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL CHECK (source IN ('chip', 'llm_suggested'))
);

-- `rank` is the whole point: the order the industries were chosen in is the
-- preference signal the dashboard sorts on. 1 is most preferred.
CREATE TABLE IF NOT EXISTS profile_industries (
    id       INTEGER PRIMARY KEY,
    industry TEXT    NOT NULL UNIQUE,
    rank     INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS profile_industries_rank_idx ON profile_industries (rank);

-- Phase 2/3. Industry is a property of the company, not the posting, so it is
-- classified once per company and cached here. The Muse gives no industry at
-- all (its `categories` field is a job function), so this is where it comes
-- from. `industry` is NULL until classified.
CREATE TABLE IF NOT EXISTS companies (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    industry      TEXT,
    classified_at TEXT
);

-- The board. One row per listing I act on; status starts at 'new'.
CREATE TABLE IF NOT EXISTS tracker (
    id         INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL UNIQUE REFERENCES listings (id) ON DELETE CASCADE,
    status     TEXT    NOT NULL DEFAULT 'new',
    notes      TEXT    NOT NULL DEFAULT '',
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS tracker_status_idx ON tracker (status);

-- One row per status change, which is the history.
CREATE TABLE IF NOT EXISTS tracker_history (
    id         INTEGER PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings (id) ON DELETE CASCADE,
    status     TEXT    NOT NULL,
    changed_at TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS tracker_history_listing_idx ON tracker_history (listing_id);

-- ATS boards discovered from apply links, never user-managed. A slug is added
-- whenever a listing's url points at greenhouse.io, lever.co, or ashbyhq.com,
-- which is how the app finds company boards without anyone curating a list.
CREATE TABLE IF NOT EXISTS ats_boards (
    id         INTEGER PRIMARY KEY,
    board      TEXT NOT NULL CHECK (board IN ('greenhouse', 'lever', 'ashby')),
    slug       TEXT NOT NULL,
    company    TEXT NOT NULL DEFAULT '',
    found_at   TEXT NOT NULL,
    last_pulled TEXT NOT NULL DEFAULT '',
    UNIQUE (board, slug)
);

-- What a title means once the noise is stripped. Kept beside `listings` rather
-- than as columns on it, for the same reason `companies` is separate: the raw
-- posting stays exactly as the source gave it, and the cleaned reading can be
-- recomputed or corrected without touching it.
CREATE TABLE IF NOT EXISTS listing_details (
    listing_id  INTEGER PRIMARY KEY REFERENCES listings (id) ON DELETE CASCADE,
    clean_title TEXT NOT NULL DEFAULT '',
    level       TEXT NOT NULL DEFAULT '',
    education   TEXT NOT NULL DEFAULT '',
    term        TEXT NOT NULL DEFAULT '',
    cleaned_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS listing_details_level_idx ON listing_details (level);
CREATE INDEX IF NOT EXISTS listing_details_education_idx ON listing_details (education);

-- A company's website and its favicon, so the board can show a logo.
-- The listing's apply url is usually an ATS (greenhouse, workday, ashby) and
-- not the company at all, so the domain is worked out separately and cached
-- here. The image bytes live in the row because they are a couple of kilobytes
-- each and this keeps the whole cache inside the one database file.
--
-- A row with ok = 0 is a company we looked for and did not find. It is kept so
-- the lookup is not retried on every page load.
CREATE TABLE IF NOT EXISTS company_icons (
    company      TEXT PRIMARY KEY,
    domain       TEXT NOT NULL DEFAULT '',
    domain_from  TEXT NOT NULL DEFAULT '',
    image        BLOB,
    content_type TEXT NOT NULL DEFAULT '',
    fetched_at   TEXT NOT NULL,
    ok           INTEGER NOT NULL DEFAULT 0,
    error        TEXT NOT NULL DEFAULT ''
);
