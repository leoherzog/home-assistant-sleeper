"""Sensor entities for the Sleeper integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SleeperCoordinator
from .models import SleeperData

if TYPE_CHECKING:
    from . import SleeperConfigEntry


@dataclass(frozen=True, kw_only=True)
class SleeperSensorEntityDescription(SensorEntityDescription):
    """Describes a Sleeper sensor entity."""

    value_fn: Callable[[SleeperData], Any]
    attr_fn: Callable[[SleeperData], dict[str, Any] | None]


def _make_roster_description(roster_id: int) -> SleeperSensorEntityDescription:
    """Create a sensor description for a specific roster."""
    return SleeperSensorEntityDescription(
        key=f"roster_{roster_id}_record",
        translation_key="roster_record",
        value_fn=lambda data, rid=roster_id: _roster_record(data, rid),
        attr_fn=lambda data, rid=roster_id: _roster_attrs(data, rid),
    )


def _roster_record(data: SleeperData, roster_id: int) -> str | None:
    """Get the W-L-T record for a roster."""
    for roster in data.rosters:
        if roster.roster_id == roster_id:
            return f"{roster.wins}-{roster.losses}-{roster.ties}"
    return None


def _roster_attrs(data: SleeperData, roster_id: int) -> dict[str, Any] | None:
    """Get extra attributes for a roster sensor."""
    for roster in data.rosters:
        if roster.roster_id == roster_id:
            user = data.roster_to_user.get(roster_id)
            standing = (
                data.standings.index(roster_id) + 1
                if roster_id in data.standings
                else 0
            )
            return {
                "wins": roster.wins,
                "losses": roster.losses,
                "ties": roster.ties,
                "fpts": roster.fpts,
                "fpts_against": roster.fpts_against,
                "standing": standing,
                "display_name": user.display_name if user else "Unknown",
                "team_name": user.team_name if user else None,
                "waiver_position": roster.waiver_position,
                "total_moves": roster.total_moves,
            }
    return None


def _my_matchup_state(data: SleeperData) -> str | None:
    """Get the matchup score string for my team."""
    if data.my_roster is None:
        return None

    my_matchup_id: int | None = None
    my_points: float = 0.0
    for m in data.matchups:
        if m.roster_id == data.my_roster.roster_id:
            my_matchup_id = m.matchup_id
            my_points = m.points
            break

    if my_matchup_id is None:
        return "BYE"

    # Find opponent
    for m in data.matchups:
        if m.matchup_id == my_matchup_id and m.roster_id != data.my_roster.roster_id:
            return f"{my_points} - {m.points}"

    return "BYE"


def _my_matchup_attrs(data: SleeperData) -> dict[str, Any] | None:
    """Get extra attributes for my matchup sensor."""
    if data.my_roster is None:
        return {"opponent_name": None, "opponent_points": None, "week": data.nfl_state.week}

    my_matchup_id: int | None = None
    for m in data.matchups:
        if m.roster_id == data.my_roster.roster_id:
            my_matchup_id = m.matchup_id
            break

    if my_matchup_id is None:
        return {"opponent_name": None, "opponent_points": None, "week": data.nfl_state.week}

    for m in data.matchups:
        if m.matchup_id == my_matchup_id and m.roster_id != data.my_roster.roster_id:
            opp_user = data.roster_to_user.get(m.roster_id)
            opp_name = opp_user.display_name if opp_user else "Unknown"
            return {
                "opponent_name": opp_name,
                "opponent_points": m.points,
                "week": data.nfl_state.week,
            }

    return {"opponent_name": None, "opponent_points": None, "week": data.nfl_state.week}


LEAGUE_SENSORS: tuple[SleeperSensorEntityDescription, ...] = (
    SleeperSensorEntityDescription(
        key="league_status",
        translation_key="league_status",
        value_fn=lambda data: data.league.status,
        attr_fn=lambda data: {
            "league_name": data.league.name,
            "season": data.league.season,
            "total_rosters": data.league.total_rosters,
        },
    ),
    SleeperSensorEntityDescription(
        key="nfl_week",
        translation_key="nfl_week",
        value_fn=lambda data: data.nfl_state.week,
        attr_fn=lambda data: {
            "season": data.nfl_state.season,
            "season_type": data.nfl_state.season_type,
        },
    ),
)

MY_TEAM_SENSORS: tuple[SleeperSensorEntityDescription, ...] = (
    SleeperSensorEntityDescription(
        key="my_record",
        translation_key="my_record",
        value_fn=lambda data: (
            f"{data.my_roster.wins}-{data.my_roster.losses}-{data.my_roster.ties}"
            if data.my_roster
            else "0-0-0"
        ),
        attr_fn=lambda data: (
            {
                "wins": data.my_roster.wins,
                "losses": data.my_roster.losses,
                "ties": data.my_roster.ties,
                "fpts": data.my_roster.fpts,
                "fpts_against": data.my_roster.fpts_against,
            }
            if data.my_roster
            else None
        ),
    ),
    SleeperSensorEntityDescription(
        key="my_points",
        translation_key="my_points",
        value_fn=lambda data: data.my_roster.fpts if data.my_roster else 0.0,
        attr_fn=lambda data: (
            {
                "fpts_against": data.my_roster.fpts_against,
                "points_per_game": round(
                    data.my_roster.fpts
                    / max(
                        data.my_roster.wins + data.my_roster.losses + data.my_roster.ties,
                        1,
                    ),
                    2,
                ),
            }
            if data.my_roster
            else None
        ),
    ),
    SleeperSensorEntityDescription(
        key="my_matchup",
        translation_key="my_matchup",
        value_fn=_my_matchup_state,
        attr_fn=_my_matchup_attrs,
    ),
    SleeperSensorEntityDescription(
        key="my_standing",
        translation_key="my_standing",
        value_fn=lambda data: (
            data.standings.index(data.my_roster.roster_id) + 1
            if data.my_roster and data.my_roster.roster_id in data.standings
            else 0
        ),
        attr_fn=lambda data: {"total_teams": len(data.standings)},
    ),
)

DIAGNOSTIC_SENSOR = SleeperSensorEntityDescription(
    key="last_updated",
    translation_key="last_updated",
    entity_category=EntityCategory.DIAGNOSTIC,
    value_fn=lambda data: datetime.now(timezone.utc).isoformat(),
    attr_fn=lambda data: None,  # Populated in entity class with coordinator info
)


class SleeperSensorEntity(CoordinatorEntity[SleeperCoordinator], SensorEntity):
    """Base class for Sleeper sensor entities."""

    entity_description: SleeperSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SleeperCoordinator,
        description: SleeperSensorEntityDescription,
        league_id: str,
        league_name: str,
        roster_id: int | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{league_id}_{description.key}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, league_id)},
            name=league_name,
            manufacturer="Sleeper",
            model="Fantasy League",
        )
        if roster_id is not None:
            user = coordinator.data.roster_to_user.get(roster_id)
            display_name = user.display_name if user else f"Roster {roster_id}"
            self._attr_translation_placeholders = {"display_name": display_name}

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.key == "last_updated":
            return {
                "update_interval": str(self.coordinator.update_interval),
            }
        return self.entity_description.attr_fn(self.coordinator.data)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SleeperConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sleeper sensor entities from a config entry."""
    coordinator: SleeperCoordinator = entry.runtime_data
    league_id = coordinator.league_id
    league_name = coordinator.data.league.name

    entities: list[SleeperSensorEntity] = []

    # League sensors (always created)
    for description in LEAGUE_SENSORS:
        entities.append(
            SleeperSensorEntity(coordinator, description, league_id, league_name)
        )

    # Diagnostic sensor (always created)
    entities.append(
        SleeperSensorEntity(coordinator, DIAGNOSTIC_SENSOR, league_id, league_name)
    )

    # Per-roster sensors
    known_roster_ids: set[int] = set()
    for roster in coordinator.data.rosters:
        known_roster_ids.add(roster.roster_id)
        description = _make_roster_description(roster.roster_id)
        entities.append(
            SleeperSensorEntity(
                coordinator, description, league_id, league_name,
                roster_id=roster.roster_id,
            )
        )

    # My team sensors (only when user is configured and found in league)
    if coordinator.data.my_roster is not None:
        for description in MY_TEAM_SENSORS:
            entities.append(
                SleeperSensorEntity(coordinator, description, league_id, league_name)
            )

    async_add_entities(entities)

    # Register a listener to detect new rosters on each update
    @callback
    def _async_check_new_rosters() -> None:
        """Check for new rosters and add entities for them."""
        nonlocal known_roster_ids
        new_entities: list[SleeperSensorEntity] = []
        current_roster_ids: set[int] = set()

        for roster in coordinator.data.rosters:
            current_roster_ids.add(roster.roster_id)
            if roster.roster_id not in known_roster_ids:
                description = _make_roster_description(roster.roster_id)
                new_entities.append(
                    SleeperSensorEntity(
                        coordinator, description, league_id, league_name,
                        roster_id=roster.roster_id,
                    )
                )

        if new_entities:
            known_roster_ids = known_roster_ids | current_roster_ids
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_check_new_rosters)
