# Auto-apply

A browser extension that fills an application form from what it already knows
about me, flags what it does not know, and hands the form back for me to read
and submit.

Nothing here is built yet. This is the plan.

## The shape of it

1. I upload my résumé. An LLM reads it once and proposes a set of **facts** —
   name, email, phone, address, school, degree, graduation date, work
   authorisation, links. I review and correct them. They are stored locally.
2. I open an application in my browser. The extension recognises it as a form
   it can help with and offers to fill it.
3. It fills every field it can map to a fact, highlights each one, leaves the
   rest amber, and tells me how many need me.
4. I fill the gaps. Anything I type can be saved back as a new fact, so the
   next form that asks the same question is already answered.
5. **I read the form and click submit.** The agent never does.
6. On a multi-page application it notices the next page and repeats from 3.

## The boundary

**The agent fills. I submit.** This is the load-bearing decision and everything
else is shaped by it.

Two reasons, and the second matters more than the first. Most ATS terms of
service prohibit automated submission while saying nothing about assisted
filling, so this keeps the feature defensible. And an answer I never read,
submitted under my name, cannot be taken back — a stale graduation date or a
wrong work-authorisation answer is worse than a blank field, because a blank
field gets noticed.

### Never auto-filled, for any reason

| Field | Why |
| --- | --- |
| Race, gender, veteran status, disability | Voluntary self-disclosures under EEO rules. They are mine to give or withhold, and a tool that answers them on my behalf has taken that choice away. Left untouched and unhighlighted. |
| "I certify the above is true" and any signature | A legal attestation. Only a person can make one. |
| Salary expectation | One number, no undo, and it is a negotiation rather than a fact. |
| Free-text essays | It may *draft* one into a side panel for me to edit and paste. It never writes one straight into the form. |
| Any fact the extractor marked low-confidence | An unreviewed guess in a real application is the failure mode this whole design exists to avoid. |

## Architecture

```
  résumé.pdf
      │
      ▼
  ingest ──► LLM extract ──► I review ──► profile_facts  (SQLite, local)
                                               │
  ┌────────────────────────────────────────────┤
  │                                            │
  │  browser                            intern-app (localhost)
  │  ┌──────────────────────┐           ┌──────────────────────┐
  │  │ content script       │  fields   │ POST /api/autofill   │
  │  │  reads the form,     │ ────────► │  match cascade       │
  │  │  writes the values   │ ◄──────── │  returns values      │
  │  │  paints the state        │  values   │                      │
  │  ├──────────────────────┤           │  learned_mappings    │
  │  │ service worker       │           │  profile_facts       │
  │  │  holds the token     │           └──────────────────────┘
  │  └──────────────────────┘
```

### Why a local HTTP bridge, and the hole it opens

The extension talks to the app over `127.0.0.1:8000`. That is simple and needs
no native-messaging host — but **any page in the browser can also reach
localhost**. An API that serves my address and phone number to whoever asks is
a worse privacy failure than anything this feature fixes.

So:

- Every autofill endpoint requires a secret header. The token is generated on
  first run, stored in the app's data directory, and pasted into the extension
  once.
- The token lives in the **service worker**, never in the content script, so a
  hostile page cannot read it out of the page context.
- The endpoints check `Origin` and reject anything that is not the extension.
- `GET` never returns the whole fact set. The extension sends the fields it
  found and gets back only values for those fields.

### The match cascade

Cheapest first. Most ATS forms are conventional and never reach an LLM.

| Pass | How | Cost |
| --- | --- | --- |
| 1 | `autocomplete` attribute → canonical key. The HTML spec already names these: `given-name`, `email`, `postal-code`. | free |
| 2 | `name`/`id` patterns and normalised label text. "First Name", `first_name`, `firstName` all reach the same key. | free |
| 3 | `learned_mappings`, keyed by host and field signature. Anything solved once on a given ATS is solved forever. | free |
| 4 | One LLM call for everything still unmapped on the page, batched. Returns a canonical key per field or `unknown`. Result is written to `learned_mappings`. | ~$0.001, once per new form shape |

A field that reaches pass 4 and still comes back `unknown` is left amber. The
tool says "I do not know what this is" rather than guessing — a wrong value is
worse than an empty one, which is the same rule as the never-fill table above.

## Data

```sql
-- One row per thing known about me. `source` is how it got here, because a
-- fact an LLM read off a résumé deserves less trust than one I typed.
profile_facts(
    key         TEXT PRIMARY KEY,   -- canonical: given_name, postal_code, …
    value       TEXT NOT NULL,
    source      TEXT NOT NULL,      -- resume | user | onboarding
    confidence  REAL NOT NULL,      -- extractor's own, 1.0 when I typed it
    reviewed    INTEGER NOT NULL,   -- nothing unreviewed is ever auto-filled
    updated_at  TEXT NOT NULL
)

-- What a given field on a given site means. This is what makes the second
-- application to the same ATS free and instant.
learned_mappings(
    host        TEXT NOT NULL,
    signature   TEXT NOT NULL,      -- hash of name/id/label/type
    key         TEXT NOT NULL,      -- the canonical fact it maps to
    hits        INTEGER NOT NULL,
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (host, signature)
)

-- Every fill, so I can see what it did and undo a bad run.
fill_log(
    id, listing_id, host, url, filled, skipped, unknown, filled_at
)
```

`resumes` from PLAN.md phase 6 stays as it is and becomes the input to ingest.

## Build order

Each phase is useful alone, which matters because the extension is the riskiest
part and should not be the first thing built.

### A1 — Résumé ingest and the fact store
Upload a PDF, extract text, one LLM call to propose facts, a review screen that
makes me confirm or correct each one before it is usable.
**done means:** I upload my real résumé, every proposed fact is shown with its
confidence, and nothing is marked `reviewed` until I say so.

### A2 — The match cascade, with no browser involved
Passes 1–4 as a library plus `POST /api/autofill/match`, driven by fixtures:
real saved form HTML from Greenhouse, Lever, Ashby and Workday in
`tests/fixtures/forms/`.
**done means:** against four saved forms it maps the standard fields with no
LLM call at all, and a deliberately odd field reaches pass 4 and then stays
cached.

### A3 — The extension, read-only
MV3 extension that finds the form, shows what it *would* fill, and writes
nothing.
**done means:** on a real application I see a correct list of matches and gaps
and the form is untouched.

### A4 — Filling
Write the values, paint filled/amber/skipped, respect the never-fill list, log
the run, support undo.
**done means:** a real Greenhouse application is filled correctly, EEO
questions are untouched, and one click puts the form back as it was.

### A5 — Gaps and learning
Amber fields prompt me; answering one offers to save it as a fact.
**done means:** a field I filled by hand on one application is filled for me on
the next.

### A6 — Multi-page
Detect navigation within an application and re-run, with a hard stop before any
submit control.
**done means:** a three-page Workday application is filled across all three
pages and stops at the review step every time.

## The agents to build it with

| Agent | Owns | Why it is its own agent |
| --- | --- | --- |
| **résumé-extraction** | A1: the prompt, the fact schema, the eval set | Prompt design with a measurable accuracy target is its own discipline. It needs a labelled set and a score, not an opinion. |
| **extension** | A3, A4, A6 | MV3, content scripts, service workers and message passing share nothing with the React app. Different idioms, different build, different failure modes. |
| **matcher** | A2, A5 | Pure logic over fixtures, no browser, no UI. The one part that can be driven entirely by tests. |
| **security review** | The bridge, before A3 ships | A localhost endpoint serving my address to the browser is the sharpest edge here, and it should be reviewed by something that was not the thing that built it. |
| **ui** (existing) | The in-app surfaces: upload, fact review, fill history | Already knows DESIGN.md and the house style. |
| **reviewer** (existing) | Every diff before commit | Per CLAUDE.md. |

The matcher and the extension can run in parallel once A2's interface is fixed;
everything else is sequential.

## Cost

| | |
| --- | --- |
| Résumé extraction | one call per upload, ~$0.02 |
| A new form shape | one batched call, ~$0.001, then free forever |
| A form shape already seen | **$0.00** |

The cascade exists so that the hundredth Greenhouse application costs nothing.

## Risks worth naming now

**LinkedIn.** CLAUDE.md currently says "No LinkedIn, ever — this clause
survives any future rewrite." That rule was written about *acquiring listings*,
and filling a form I have already opened in my own browser is a different
activity. The decision has been taken to allow the extension there, so the rule
has to be rewritten to say what it now means rather than left contradicting the
code — the listing-acquisition ban stays, the form-fill carve-out is explicit.
Worth being clear-eyed: LinkedIn's user agreement prohibits automated
interaction, they do detect it, and the penalty lands on the account my job
search runs through.

**A new dependency.** Reading a PDF needs one — probably `pypdf`. CLAUDE.md
says ask first, so that is a question before A1, not during it.

**The extension is unsigned.** Loaded unpacked in developer mode. Fine for one
person; it is not a thing to hand to anyone else.

**Stale facts.** A graduation date that was right in March is wrong in June.
Facts carry `updated_at`, and anything older than a threshold should be
re-confirmed rather than silently filled.
