# AGENTS.md

This file provides guidance to Claude Code, Codex, Gemini, etc when working with code in this repository.

## Project Overview

Home Assistant custom integration for the Sleeper Fantasy Football platform. Provides sensors for league standings, rosters, matchups, and personal team data. Domain: `sleeper`, requires HA 2024.8.0+.

## Development

No build step or external dependencies — this is a pure Python HA custom component with zero `requirements` in manifest.json. All HTTP is done via HA's built-in aiohttp session.

To validate Python syntax: `python3 -m py_compile custom_components/sleeper/<file>.py`

No tests exist yet. If adding tests, follow HA custom component testing conventions with pytest and `pytest-homeassistant-custom-component`.

To install in a Home Assistant instance, symlink or copy `custom_components/sleeper/` into the HA config's `custom_components/` directory.

## Architecture

**Data flow:** ConfigFlow → `__init__.py` creates API client + coordinator → coordinator polls Sleeper API → `SleeperData` model aggregates results → sensor entities read from coordinator.

### Key components

- **`api.py`** — Stateless async HTTP client wrapping `https://api.sleeper.app/v1`. Raises `SleeperApiConnectionError` or `SleeperApiNotFoundError`. No authentication required.
- **`models.py`** — Dataclasses (`NflState`, `LeagueInfo`, `Roster`, `LeagueUser`, `Matchup`, `SleeperData`). `SleeperData` is the aggregated container with computed properties (standings, roster-to-user mapping, "my" roster/user).
- **`coordinator.py`** — Extends `DataUpdateCoordinator[SleeperData]`. Implements adaptive polling: 5 min during game windows, 15 min on game days, 1 hour regular season, 24 hours offseason. Game window detection uses Eastern timezone and knows NFL schedule patterns (Thu/Sun/Mon nights, Sat in weeks 15+).
- **`sensor.py`** — Defines all sensor entities via `SleeperSensorEntityDescription` dataclasses with `value_fn`/`attr_fn` callables. Base class is `SleeperSensorEntity(CoordinatorEntity[SleeperCoordinator])`. Dynamically creates per-roster sensors and listens for new rosters.
- **`config_flow.py`** — Two steps: initial setup (league_id required, username optional) and reconfigure (username update). Validates league/user existence and league membership via API.
- **`__init__.py`** — Defines `SleeperConfigEntry = ConfigEntry[SleeperCoordinator]` type alias. Only platform is `Platform.SENSOR`.

### Sensor categories

- **League sensors** (always): `league_status`, `nfl_week`
- **Personal sensors** (when username configured): `my_record`, `my_points`, `my_matchup`, `my_standing`
- **Per-roster sensors** (dynamic): `roster_X_record` for each roster in the league

## Conventions

- All network calls are async (`aiohttp.ClientSession`)
- Models use `@dataclass` with type hints throughout
- Config keys defined in `const.py` — use these constants, not string literals
- Sensor descriptions use functional `value_fn` and `attr_fn` patterns (lambdas/functions that take `SleeperData` as input)
- Translations live in `strings.json` (canonical) and `translations/en.json` (must stay in sync)
