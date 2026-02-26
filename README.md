# Sleeper Fantasy Football

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?logo=HomeAssistantCommunityStore&logoColor=white)](https://github.com/hacs/integration)

A Home Assistant integration for [Sleeper](https://sleeper.com/) fantasy football. Track league standings, rosters, matchups, and your personal team performance through sensors with smart polling that adapts to the NFL schedule.

## Features

- **League overview** - league status and current NFL week
- **Personal team sensors** - your record, points, current matchup score, and league standing
- **Per-roster sensors** - W-L-T record and stats for every team in your league
- **Adaptive polling** - updates every 5 minutes during games, every 15 minutes on game days, hourly during the season, and daily in the offseason
- **Dynamic roster detection** - automatically adds sensors when new rosters appear

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Install "Sleeper Fantasy Football"
3. Restart Home Assistant

### Manual

1. Copy `custom_components/sleeper` to your HA `custom_components` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Sleeper Fantasy Football"
3. Enter your **League ID** (required) and optionally your **Sleeper username**

Your League ID can be found in the URL when viewing your league on Sleeper (e.g. `https://sleeper.com/leagues/123456789` → `123456789`).

Adding your username enables personal team sensors. The username must belong to a member of the configured league.

To change your username later, use the **Reconfigure** option on the integration.

## Entities

### League Sensors (always created)

| Entity | State | Attributes |
|--------|-------|------------|
| League Status | League status (e.g. `in_season`) | League name, season, total rosters |
| NFL Week | Current NFL week number | Season year, season type |

### Personal Sensors (when username is configured)

| Entity | State | Attributes |
|--------|-------|------------|
| My Record | W-L-T (e.g. `8-3-0`) | Wins, losses, ties, fantasy points, points against |
| My Points | Total fantasy points | Points against, points per game |
| My Matchup | Score vs opponent (e.g. `105.5 - 98.2`) or `BYE` | Opponent name, opponent points, week |
| My Standing | League rank (e.g. `3`) | Total teams |

### Roster Sensors (one per team in the league)

| Entity | State | Attributes |
|--------|-------|------------|
| {Display Name} Record | W-L-T record | Wins, losses, ties, fantasy points, points against, standing, display name, team name, waiver position, total moves |

### Diagnostic

| Entity | State | Attributes |
|--------|-------|------------|
| Last Updated | ISO 8601 timestamp | Current update interval |

## Requirements

- Home Assistant 2024.8.0+
- A Sleeper fantasy football league

## Support

- [GitHub Issues](https://github.com/leoherzog/home-assistant-sleeper/issues)

## License

This project is licensed under the MIT License.

## About Me

<a href="https://herzog.tech/" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/link-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/link.svg.png">
    <img src="https://herzog.tech/signature/link.svg.png" width="32px">
  </picture>
</a>
<a href="https://mastodon.social/@herzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/mastodon-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/mastodon.svg.png">
    <img src="https://herzog.tech/signature/mastodon.svg.png" width="32px">
  </picture>
</a>
<a href="https://github.com/leoherzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/github-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/github.svg.png">
    <img src="https://herzog.tech/signature/github.svg.png" width="32px">
  </picture>
</a>
<a href="https://keybase.io/leoherzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/keybase-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/keybase.svg.png">
    <img src="https://herzog.tech/signature/keybase.svg.png" width="32px">
  </picture>
</a>
<a href="https://www.linkedin.com/in/leoherzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/linkedin-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/linkedin.svg.png">
    <img src="https://herzog.tech/signature/linkedin.svg.png" width="32px">
  </picture>
</a>
<a href="https://hope.edu/directory/people/herzog-leo/" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/anchor-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/anchor.svg.png">
    <img src="https://herzog.tech/signature/anchor.svg.png" width="32px">
  </picture>
</a>
<br />
<a href="https://herzog.tech/$" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/mug-tea-saucer-solid-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/mug-tea-saucer-solid.svg.png">
    <img src="https://herzog.tech/signature/mug-tea-saucer-solid.svg.png" alt="Buy Me A Tea" width="32px">
  </picture>
  Found this helpful? Buy me a tea!
</a>
