"""DataUpdateCoordinator for the Sleeper integration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SleeperApiClient, SleeperApiConnectionError, SleeperApiNotFoundError
from .const import (
    CONF_LEAGUE_ID,
    CONF_USER_ID,
    DOMAIN,
    UPDATE_INTERVAL_GAME_DAY,
    UPDATE_INTERVAL_GAME_WINDOW,
    UPDATE_INTERVAL_OFFSEASON,
    UPDATE_INTERVAL_REGULAR,
)
from .models import SleeperData

_LOGGER = logging.getLogger(__name__)

EASTERN = ZoneInfo("US/Eastern")


class SleeperCoordinator(DataUpdateCoordinator[SleeperData]):
    """Coordinator that fetches Sleeper data with adaptive polling."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: SleeperApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.league_id: str = config_entry.data[CONF_LEAGUE_ID]
        self.user_id: str | None = config_entry.data.get(CONF_USER_ID) or None

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL_REGULAR,
        )

    async def _async_update_data(self) -> SleeperData:
        """Fetch all data from the Sleeper API."""
        try:
            nfl_state = await self.api.async_get_nfl_state()
            league = await self.api.async_get_league(self.league_id)
            rosters = await self.api.async_get_rosters(self.league_id)
            users = await self.api.async_get_users(self.league_id)

            # Only fetch matchups during regular or post season
            if nfl_state.season_type in ("regular", "post"):
                matchups = await self.api.async_get_matchups(
                    self.league_id, nfl_state.week
                )
            else:
                matchups = []

        except SleeperApiConnectionError as err:
            raise UpdateFailed(f"Error communicating with Sleeper API: {err}") from err
        except SleeperApiNotFoundError as err:
            raise UpdateFailed(f"Resource not found: {err}") from err

        data = SleeperData.build(
            nfl_state=nfl_state,
            league=league,
            rosters=rosters,
            users=users,
            matchups=matchups,
            user_id=self.user_id,
        )

        # Recalculate polling interval based on current state
        self.update_interval = self._calculate_update_interval(nfl_state.season_type, nfl_state.week)
        _LOGGER.debug(
            "Update interval set to %s for league %s",
            self.update_interval,
            self.league_id,
        )

        return data

    def _calculate_update_interval(
        self, season_type: str, week: int
    ) -> timedelta:
        """Calculate the next update interval based on NFL state and time."""
        if season_type == "off":
            return UPDATE_INTERVAL_OFFSEASON

        if season_type not in ("regular", "post"):
            # Pre-season or other non-active states
            return UPDATE_INTERVAL_REGULAR

        now_et = datetime.now(EASTERN)
        day_of_week = now_et.weekday()  # 0=Monday, 6=Sunday
        hour = now_et.hour

        if self._is_in_game_window(day_of_week, hour, week, season_type):
            return UPDATE_INTERVAL_GAME_WINDOW

        if self._is_game_day(day_of_week, week, season_type):
            return UPDATE_INTERVAL_GAME_DAY

        return UPDATE_INTERVAL_REGULAR

    @staticmethod
    def _is_game_day(
        day_of_week: int, week: int, season_type: str
    ) -> bool:
        """Check if today is an NFL game day."""
        # Thursday (3), Sunday (6), Monday (0)
        if day_of_week in (0, 3, 6):
            return True

        # Saturday (5) only during weeks 15+ or postseason
        if day_of_week == 5 and (week >= 15 or season_type == "post"):
            return True

        return False

    @staticmethod
    def _is_in_game_window(
        day_of_week: int, hour: int, week: int, season_type: str
    ) -> bool:
        """Check if we're currently in a game window."""
        # Thursday: 7 PM - 12 AM (19-23)
        if day_of_week == 3 and hour >= 19:
            return True

        # Sunday: 12 PM - 12 AM (12-23)
        if day_of_week == 6 and hour >= 12:
            return True

        # Monday: 7 PM - 12 AM (19-23)
        if day_of_week == 0 and hour >= 19:
            return True

        # Saturday: 12 PM - 12 AM (12-23), only weeks 15+ or postseason
        if (
            day_of_week == 5
            and hour >= 12
            and (week >= 15 or season_type == "post")
        ):
            return True

        return False
