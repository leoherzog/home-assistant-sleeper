"""Async API client for Sleeper."""

from __future__ import annotations

from typing import Any

import aiohttp

from .const import API_BASE_URL
from .models import LeagueInfo, LeagueUser, Matchup, NflState, Roster


class SleeperApiConnectionError(Exception):
    """Exception for connection errors."""


class SleeperApiNotFoundError(Exception):
    """Exception when a resource is not found (API returns null)."""


class SleeperApiClient:
    """Stateless client for the Sleeper API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session

    async def _get(self, path: str) -> Any:
        """Make a GET request and return the parsed JSON."""
        url = f"{API_BASE_URL}{path}"
        try:
            async with self._session.get(url) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise SleeperApiConnectionError(
                f"Error connecting to Sleeper API: {err}"
            ) from err

        if data is None:
            raise SleeperApiNotFoundError(f"Resource not found: {path}")

        return data

    async def async_get_user(self, username: str) -> dict[str, Any]:
        """Get a user by username. Returns raw dict with user_id etc."""
        return await self._get(f"/user/{username}")

    async def async_get_league(self, league_id: str) -> LeagueInfo:
        """Get league info."""
        data = await self._get(f"/league/{league_id}")
        return LeagueInfo.from_api(data)

    async def async_get_rosters(self, league_id: str) -> list[Roster]:
        """Get all rosters for a league."""
        data = await self._get(f"/league/{league_id}/rosters")
        return [Roster.from_api(r) for r in data]

    async def async_get_users(self, league_id: str) -> list[LeagueUser]:
        """Get all users in a league."""
        data = await self._get(f"/league/{league_id}/users")
        return [LeagueUser.from_api(u) for u in data]

    async def async_get_matchups(
        self, league_id: str, week: int
    ) -> list[Matchup]:
        """Get matchups for a specific week."""
        data = await self._get(f"/league/{league_id}/matchups/{week}")
        return [Matchup.from_api(m) for m in data]

    async def async_get_nfl_state(self) -> NflState:
        """Get the current NFL state."""
        data = await self._get("/state/nfl")
        return NflState.from_api(data)
