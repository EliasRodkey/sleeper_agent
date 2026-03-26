# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Fantasy Football Draft Automation Suite that:
- Integrates with the Sleeper.app Fantasy Football platform via its public API
- Enriches draft data with ADP rankings from Fantasy Football Calculator
- Streams live draft state to Google Sheets for real-time visualization
- Feeds structured data to LLM agents for draft decision support

## Setup

No formal package manager is configured. Install dependencies manually:

```bash
python -m venv venv
source venv/bin/activate
pip install pandas requests gspread oauth2client gspread_dataframe google-auth-httplib2 google-auth-oauthlib
```

**Required credential:** Place a Google service account JSON file at `spreadsheets/spreadsheet_credentials.json` (git-ignored).

## Running the Project

```bash
# Main entry point
python draft_script.py

# Individual modules have __main__ blocks for manual testing
python sleeper/sleeper_draft.py
python agents/prompts/prompt_builder.py
```

No formal test suite or linting configuration exists.

## Architecture

The codebase has three layers with a clear data flow:

```
Sleeper.app API + FFCalc API → sleeper/ → draft_script.py → agents/prompts/
                                               ↕
                                         spreadsheets/ (Google Sheets)
```

### `sleeper/` — API & Data Layer

- **`sleeper_api.py`** — Raw HTTP calls to `https://api.sleeper.app/v1`. The `get_players()` endpoint is rate-limited (max once/day).
- **`sleeper_user.py`** — User singleton pattern; caches User instances by username.
- **`sleeper_league.py`** — Initializes with league data; creates user↔ID mappings and instantiates `Draft`.
- **`sleeper_draft.py`** — Core draft state machine. Tracks `PRE_DRAFT`/`DRAFTING`/`PAUSED`/`COMPLETE` status, diffs new picks against `last_picks`, converts picks JSON to pandas DataFrames, merges with player/ADP data, and provides `get_remaining_players()`.
- **`sleeper_roster.py`** — Converts roster JSON to a DataFrame sorted by `POSITION_ORDER = ['QB', 'WR', 'RB', 'TE', 'K', 'DEF']`.
- **`ffcalc_api.py`** — ADP data from Fantasy Football Calculator. `get_half_ppr_adp_df()` computes a 60/40 weighted average of PPR and standard scoring.

### `spreadsheets/` — Google Sheets Integration

Base classes:
- **`WorksheetWrapper`** — Low-level gspread abstraction for read/write of DataFrames and cell ranges.
- **`SheetManager`** — Lifecycle management (create/delete/rename sheets, caching worksheet objects).

Spreadsheet managers (both extend `SheetManager`):
- **`DraftSpreadsheet`** — Manages four live-draft worksheets: `LeagueSettingsWorksheet`, `DraftboardWorksheet`, `PicksWorksheet`, `MemberRosterWorksheet`. Auto-clears and reinitializes on load.
- **`PlayersSpreadsheet`** — Manages NFL player reference data with 24-hour update throttling.

Key utility:
- **`spreadsheet_utils.py`** — `normalize_name()` standardizes player names (removes suffixes, punctuation) for cross-source matching. Used when merging tier rankings with player IDs.

Spreadsheets are identified by the `EFantasySpreadsheets` enum in `spreadsheet_names.py` (e.g., `DYNASTY2025`, `REDRAFT2025`, `PLAYERS`, `TIERS_2025`).

### `agents/prompts/` — LLM Prompt Layer

- **`PromptBuilder`** — Chainable base class that accumulates text, sections, DataFrames, and dicts into a formatted markdown prompt.
- **`DraftStatusPrompt(PromptBuilder)`** — Wraps draft state (current roster, position counts, picks, remaining players as DataFrames) and provides analysis methods: `get_top_available_by_adp()`, `get_top_available_by_tier()`, `detect_scarcity()`, `summarize_recent_picks()`.

### `draft_script.py` — Orchestration

The main script wires everything together:
1. Load/refresh player data via `PlayersSpreadsheet`
2. Merge tier rankings onto player data (joined on `player_id`)
3. Authenticate and load league via `User` → `League`
4. Retrieve live draft state via `Draft.retrieve_draft_state()`
5. Build user roster via `User.set_roster()`
6. Construct `DraftStatusPrompt` for LLM consumption

## Key Cross-Module Dependencies

- `League.__init__` instantiates `Draft` internally — they hold circular references via `draft.league`.
- `Draft` depends on `ffcalc_api` for ADP merging.
- `DraftSpreadsheet` holds references to `User`, `League`, and `Draft` objects.
- Player name normalization (`normalize_name`) is the critical link between tier rankings and Sleeper player IDs.
