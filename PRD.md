# Product Requirements Document
## Sleeper Agent — Fantasy Football Draft Automation Suite v2

---

## 1. Overview

A Fantasy Football Draft Automation Suite that:
- Integrates with the Sleeper.app Fantasy Football platform via its public API
- Maintains a live in-memory draft board (pandas DataFrame) that mirrors the Sleeper UI
- Stores player data and draft history in a local SQLite database (swappable with Google Sheets)
- Imports a personal draft cheat sheet (Excel) merged into the board at startup
- Feeds live draft state to a Claude AI agent for pick recommendations and conversational analysis

---

## 2. Goals & Non-Goals

### Goals
- Replace Google Sheets as the hard-coded data store with a swappable local database
- Maintain a live internal draft board as an in-memory pandas DataFrame
- Provide a Claude-powered AI agent that auto-triggers on the user's turn and supports follow-up questions
- Support a personal draft cheat sheet (Excel) merged into the board at startup
- Persist draft history across sessions for future analysis

### Non-Goals (v2)
- Multi-model jury (designed for, not implemented — model is configurable)
- Post-draft analysis UI (draft history DB is stored; analysis interface deferred)
- Cheat sheet editor UI (import from Excel only; web editor deferred)
- Push notifications / mobile interface

---

## 3. Architecture

### 3.1 Directory Structure

```
sleeper_agent/
├── sleeper/                        (unchanged — API & data layer)
│   ├── sleeper_api.py
│   ├── sleeper_user.py
│   ├── sleeper_league.py
│   ├── sleeper_draft.py
│   ├── sleeper_roster.py
│   └── ffcalc_api.py
├── storage/                        (NEW — swappable storage layer)
│   ├── __init__.py
│   ├── base.py                     ABCs: ReferenceStorageBackend, DraftStorageBackend
│   ├── tables.py                   pleasant_database BaseTable subclasses
│   ├── db_backend.py               DatabaseReferenceBackend, DatabaseDraftBackend
│   └── sheets_backend.py           SheetsReferenceBackend, SheetsDraftBackend
├── spreadsheets/                   (unchanged — becomes the GSheets backend implementation)
├── agents/
│   ├── prompts/                    (unchanged — context builder for Claude prompts)
│   │   ├── prompt_builder.py
│   │   └── draft_status_prompt.py
│   ├── draft_agent.py              (NEW — Claude API with tool-calling)
│   └── agent_tools.py              (NEW — tool definitions + implementations)
├── config.py                       (NEW — env var loading with interactive fallback)
├── draft_session.py                (NEW — in-memory state: board, picks, roster)
├── repl.py                         (NEW — terminal REPL: slash commands + free-form chat)
├── run_draft.py                    (NEW — main entry point)
├── .env.example                    (NEW — env var template)
├── data/                           (gitignored — SQLite DB files)
│   ├── players.db
│   └── draft_history.db
└── draft_script.py                 (DEPRECATED — kept for reference)
```

### 3.2 Data Flow

```
Sleeper API + FFCalc API
        ↓
  [startup: refresh players + ADP]
        ↓
  ReferenceStorageBackend ←→ players.db (DB) or PlayersSpreadsheet (GSheets)
        ↓
  DraftSession.initialize_board()     ← cheat sheet merged here
        ↓
  PickPoller (background thread)      ← polls Sleeper API at interval
        ↓ (new picks detected)
  DraftSession.apply_pick()           ← removes from board, saves to picks_df
        ↓
  DraftStorageBackend                 ← persists picks to draft_history.db
        ↓ (if it's user's turn)
  DraftAgent.get_recommendation()     ← calls Claude with tool-calling
        ↓
  Terminal output (ranked list + explanation)
        ↓
  REPL (main thread)                  ← slash commands or free-form → agent.ask()
```

---

## 4. Storage Layer

### 4.1 Abstract Interfaces (`storage/base.py`)

Two ABCs, one per domain (minimizes switching interfaces):

#### `ReferenceStorageBackend`
Manages NFL player master list and ADP data.

| Method | Description |
|---|---|
| `save_players(df)` | Persist player master list |
| `get_players() -> df` | Retrieve full player list |
| `players_need_refresh() -> bool` | True if player data needs to be fetched |
| `save_adp(df)` | Persist ADP data |
| `get_adp() -> df` | Retrieve ADP data |

#### `DraftStorageBackend`
Manages draft metadata and pick history (persistent across sessions).

| Method | Description |
|---|---|
| `save_draft(draft_id, league_name, year, draft_type)` | Upsert draft record |
| `save_picks(draft_id, picks_df)` | Upsert all picks for a draft |
| `get_picks(draft_id) -> df` | Retrieve all picks for a draft |
| `close()` | Close DB sessions |

### 4.2 Database Backend (`storage/db_backend.py`)

Uses `pleasant_database` (SQLAlchemy/SQLite). Two separate database files:

**`data/players.db`** — `DatabaseReferenceBackend`
- Wiped and re-seeded from Sleeper API at every startup
- `players_need_refresh()` returns `True` if table is empty
- Write: `clear_table()` + `append_dataframe(df)`
- Read: `to_dataframe()`

**`data/draft_history.db`** — `DatabaseDraftBackend`
- Persistent across all drafts, never wiped
- Uses `upsert()` so re-running on a live draft is safe
- Enables future post-draft analysis

### 4.3 Google Sheets Backend (`storage/sheets_backend.py`)

Thin wrappers delegating to existing spreadsheet classes:
- `SheetsReferenceBackend` → wraps `PlayersSpreadsheet`
- `SheetsDraftBackend` → wraps `DraftSpreadsheet` (also provides live visual board in Sheets)

### 4.4 Database Tables (`storage/tables.py`)

All tables extend `pleasant_database.BaseTable` (SQLAlchemy declarative base).

**`NFLPlayerRow`** — primary key: `player_id` (String, not autoincrement)
```
player_id (String PK), full_name, normalized_name, fantasy_positions,
team, age (Float), last_updated (DateTime), [+ optional stat columns as String/Float]
```
> Note: Uses `clear_table()` + `append_dataframe()` for writes; `to_dataframe()` for reads.
> `fetch_item_by_id()` is not used (it expects an Integer `id` column).

**`DraftRow`** — primary key: `id` (Integer, autoincrement)
```
id (PK), draft_id (String, UniqueConstraint), league_name, year (Integer),
draft_type, created_at (DateTime)
```

**`PickRow`** — primary key: `id` (Integer, autoincrement)
```
id (PK), draft_id (String), pick_no (Integer), round_num (Integer),
player_id (String), username (String)
UniqueConstraint("draft_id", "pick_no")
```

---

## 5. Configuration

### 5.1 Mechanism
Environment variables loaded via `python-dotenv` from a `.env` file. Missing required values fall back to interactive `input()` prompts at startup.

### 5.2 Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SLEEPER_USERNAME` | yes | — | Sleeper account username |
| `SLEEPER_LEAGUE_NAME` | yes | — | League name to search for |
| `ANTHROPIC_API_KEY` | yes | — | Anthropic API key |
| `STORAGE_BACKEND` | no | `db` | `db` or `sheets` |
| `POLL_INTERVAL_SECONDS` | no | `10` | Draft state poll frequency (seconds) |
| `DRAFT_TYPE` | no | `redraft` | `redraft` or `dynasty` |
| `CHEAT_SHEET_PATH` | no | — | Absolute or relative path to Excel cheat sheet |
| `AI_MODEL` | no | `claude-opus-4-6` | Claude model ID |

### 5.3 `Config` Dataclass (`config.py`)
```python
@dataclass
class Config:
    username: str
    league_name: str
    anthropic_api_key: str
    storage_backend: str = "db"
    poll_interval: int = 10
    draft_type: str = "redraft"
    cheat_sheet_path: str | None = None
    ai_model: str = "claude-opus-4-6"
```

---

## 6. In-Memory Draft Session (`draft_session.py`)

Single source of truth for all live state during a draft. Never persisted — always rebuildable from the DB.

### 6.1 `DraftSession` State

| Attribute | Type | Description |
|---|---|---|
| `board` | `pd.DataFrame` | Available players (shrinks as picks land) |
| `picks_df` | `pd.DataFrame` | All picks made so far |
| `my_roster` | `Roster \| None` | User's current roster |
| `cheat_sheet` | `pd.DataFrame \| None` | Cheat sheet data merged into board |
| `_my_draft_slots` | `set[int]` | Pre-computed set of pick numbers belonging to user |

### 6.2 Board Initialization

1. Start with `players_df` (from DB/Sheets)
2. Merge ADP from FFCalc on `normalized_name`
3. If cheat sheet provided: merge on `normalized_name` to attach `tier`, `intra_tier_ranking`, `overall_ranking`, projected stats
4. `_compute_my_draft_slots()` — derive pick numbers from `Draft.order` and number of teams

### 6.3 Snake Draft Slot Computation

`Draft.order` is a list of user IDs in draft slot order (1-indexed position in list). For a `T`-team snake draft:
- Odd rounds: user at slot `S` picks at position `S` (1-indexed pick within round)
- Even rounds: user at slot `S` picks at position `T - S + 1`
- Absolute pick number for round `R`, round-position `P`: `(R - 1) * T + P`

### 6.4 Key Methods

| Method | Description |
|---|---|
| `initialize_board()` | Merge ADP + cheat sheet into players_df; set board |
| `load_cheat_sheet(path)` | Import Excel, normalize names, merge into board |
| `apply_pick(pick_dict)` | Remove from board, add to picks_df, update roster if mine |
| `apply_picks_batch(picks)` | Bulk apply on startup to catch up to current draft state |
| `is_my_turn(pick_no)` | Check pick_no against `_my_draft_slots` |
| `rebuild_board()` | Full board rebuild from players_df minus picks_df (recovery) |

### 6.5 Cheat Sheet Format

Expected Excel columns (flexible — extra columns are kept):

| Column | Required | Notes |
|---|---|---|
| `full_name` or `name` | yes | Matched via `normalize_name()` to get `player_id` |
| `tier` | yes | Integer tier number |
| `intra_tier_ranking` | yes | Rank within tier |
| `overall_ranking` | yes | Overall rank across all positions |
| `position` | yes | WR / RB / QB / TE / K / DEF |
| `team` | yes | Team abbreviation |
| projected stats | optional | Any additional columns are preserved |

Merge key: `normalized_name` (via `spreadsheets/spreadsheet_utils.normalize_name()` — removes suffixes, punctuation, lowercases).

---

## 7. Background Pick Poller

### 7.1 `PickPoller(threading.Thread)`

Runs in background while the REPL holds the main thread.

**On each poll cycle:**
1. Call `Draft.update_picks()` to fetch latest picks from Sleeper API
2. Diff against `session.picks_df` by `pick_no` to find new picks
3. For each new pick: call `session.apply_pick()`, print to terminal
4. Save updated picks to `DraftStorageBackend`
5. Determine next open pick slot; if it's the user's turn:
   - Print `[Your turn!]`
   - Call `agent.reset_history()` then `agent.get_recommendation()`
   - Print recommendation to terminal
6. If `draft.status == COMPLETE`: set stop event

**Threading:** `stop_event` (a `threading.Event`) coordinates shutdown between poller and REPL.

---

## 8. AI Draft Agent

### 8.1 Design Decisions

- **Model:** Claude (default `claude-opus-4-6`), configurable via `AI_MODEL` env var
- **Trigger:** Auto-fires when it's the user's turn; also available on-demand via REPL
- **Concurrency:** Async background agent with background poller thread + main REPL thread
- **History:** Conversation history is reset at the start of each pick turn; maintained within a turn for follow-ups
- **Output format:** Ranked list of recommendations followed by a narrative explanation

### 8.2 `DraftAgent` (`agents/draft_agent.py`)

```python
class DraftAgent:
    def __init__(self, session: DraftSession, config: Config): ...
    def get_recommendation(self) -> str: ...   # auto-trigger; no history
    def ask(self, question: str) -> str: ...   # conversational; uses + updates history
    def reset_history(self) -> None: ...       # called at start of each turn
    def _build_system_prompt(self) -> str: ... # uses DraftStatusPrompt for context
    def _run_tool_loop(self, messages: list) -> str: ...  # standard Anthropic tool loop
```

### 8.3 Context Prompt

Built via `DraftStatusPrompt` (existing class, unchanged). Includes:
- Current roster and position counts
- Top N available players by tier and ADP
- Recent pick summary (last ~10 picks, position distribution)
- Scarcity analysis (available players per position by tier cutoff)

Full pick history is **not** included by default (token efficiency) — agent can call `get_recent_picks` tool for more.

### 8.4 Tool Definitions (`agents/agent_tools.py`)

| Tool | Description | Key Parameters |
|---|---|---|
| `get_available_players` | Top N available players sorted by ADP or tier | `position`, `sort_by`, `n` |
| `get_my_roster` | Current roster and position counts | — |
| `get_position_scarcity` | Count of available players at position, by tier | `position` |
| `get_recent_picks` | Last N picks with player info | `n` |
| `get_cheat_sheet_top` | Top N from cheat sheet, filtered by position and tier | `position`, `tier_max`, `n` |

All tools receive the live `DraftSession` and return a formatted string.

### 8.5 Multi-Model Jury (Future)

Not implemented in v2. The agent accepts a `model: str` parameter — swapping models or running parallel agents requires no architectural changes.

---

## 9. Terminal REPL (`repl.py`)

### 9.1 Design

- **Main thread** runs the REPL; background thread runs the poller
- Poller prints pick notifications and agent recommendations directly to stdout (interrupts the prompt visually but does not break input)
- REPL reads input line by line

### 9.2 Slash Commands

| Command | Description |
|---|---|
| `/board [position]` | Print current draft board, optionally filtered by position |
| `/roster` | Print user's current roster and position counts |
| `/picks [n]` | Print last N picks (default 10) |
| `/scarcity [position]` | Print count of available players per position by tier |
| `/help` | List available commands |
| `/quit` | Exit gracefully (sets stop event, joins poller) |

Any other input is passed to `agent.ask()` as a free-form question.

### 9.3 Conversation Continuity

The agent's `_history` list persists across REPL inputs within a pick turn, enabling multi-turn conversations like:
```
> Who should I pick at RB?
[agent recommends top RBs]
> What about if I need a WR instead?
[agent adjusts based on context]
```
History is cleared when the poller detects it's the user's turn again.

---

## 10. Entry Point (`run_draft.py`)

### 10.1 Startup Sequence

1. `load_config()` — load env vars, prompt for missing values
2. `create_backends(config)` — instantiate correct backend pair based on `STORAGE_BACKEND`
3. Refresh players: if `ref_backend.players_need_refresh()` → fetch from Sleeper API → `save_players()`
4. Load players: `ref_backend.get_players()` → `players_df`
5. Fetch ADP fresh from FFCalc (always refreshed each session)
6. Save ADP: `ref_backend.save_adp(adp_df)`
7. Init Sleeper: `User(username)` → `user.retrieve_league_info(league_name)` → `League(...)`
8. Build session: `DraftSession(user, league, players_df)` → `session.initialize_board()`
9. Load cheat sheet if `CHEAT_SHEET_PATH` is set: `session.load_cheat_sheet(path)`
10. Catch up: `session.apply_picks_batch(league.draft.picks)` (handles draft already in progress)
11. Persist: `draft_backend.save_draft(...)` + `draft_backend.save_picks(...)`
12. Init agent: `DraftAgent(session, config)`
13. Start poller: `PickPoller(...).start()`
14. Run REPL: `run_repl(session, agent, stop_event)` — blocks main thread
15. Cleanup: set stop event → join poller → `draft_backend.close()`

### 10.2 Backend Factory

```python
def create_backends(config: Config) -> tuple[ReferenceStorageBackend, DraftStorageBackend]:
    if config.storage_backend == "db":
        return DatabaseReferenceBackend(), DatabaseDraftBackend()
    return SheetsReferenceBackend(), SheetsDraftBackend(...)
```

---

## 11. Files Unchanged

The following files require no modification:

- `sleeper/sleeper_api.py`, `sleeper_user.py`, `sleeper_league.py`, `sleeper_draft.py`, `sleeper_roster.py`, `ffcalc_api.py`
- `spreadsheets/worksheet_wrapper.py`, `sheet_manager.py`, `spreadsheet_utils.py`, `gspread_client.py`, `spreadsheet_names.py`
- `spreadsheets/draft_spreadsheet/` (all worksheet classes)
- `spreadsheets/players_spreadsheet/` (all worksheet classes)
- `agents/prompts/prompt_builder.py`, `draft_status_prompt.py`

`draft_script.py` — deprecated but kept for reference; add a comment at the top.

---

## 12. Dependencies

New packages to install:

```bash
pip install pleasant_database python-dotenv anthropic openpyxl
```

Full install command:

```bash
pip install pandas requests gspread oauth2client gspread_dataframe \
    google-auth-httplib2 google-auth-oauthlib \
    pleasant_database python-dotenv anthropic openpyxl
```

---

## 13. Gitignore Additions

```
data/
.env
```

(`data/` holds SQLite files; `.env` holds secrets — both already covered by standard patterns but should be explicitly confirmed.)

---

## 14. Implementation Order

| Step | File | Dependencies |
|---|---|---|
| 1 | `storage/tables.py` | none |
| 2 | `storage/base.py` | none |
| 3 | `storage/db_backend.py` | tables, base |
| 4 | `storage/sheets_backend.py` | existing spreadsheets/, base |
| 5 | `config.py` | none |
| 6 | `draft_session.py` | sleeper/, ffcalc_api, spreadsheet_utils |
| 7 | `agents/agent_tools.py` | draft_session |
| 8 | `agents/draft_agent.py` | agent_tools, draft_status_prompt, anthropic |
| 9 | `repl.py` | draft_session, draft_agent |
| 10 | `run_draft.py` + `PickPoller` | everything |
| 11 | `.env.example` | — |
| 12 | `CLAUDE.md` update | — |

---

## 15. Verification

### End-to-End Test
1. Copy `.env.example` → `.env`, fill in `SLEEPER_USERNAME`, `SLEEPER_LEAGUE_NAME`, `ANTHROPIC_API_KEY`
2. `python run_draft.py` — DB initialized, players loaded, REPL opens
3. `/board QB` — prints top QBs available with ADP/tier
4. `/roster` — prints current roster and position counts
5. `"Who are the best value picks right now?"` — Claude responds with ranked list + explanation
6. Change `STORAGE_BACKEND=sheets` in `.env`, rerun — same flow via Google Sheets
7. After draft completes, inspect `data/draft_history.db` to confirm picks saved

### Per-Module Testing (`__main__` pattern)
```bash
python storage/db_backend.py       # CRUD test against local DB
python draft_session.py            # board init, apply_pick, is_my_turn
python agents/draft_agent.py       # tool loop with mock session
```
