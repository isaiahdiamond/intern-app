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
