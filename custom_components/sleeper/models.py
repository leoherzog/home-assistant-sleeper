"""Data models for the Sleeper integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NflState:
    """Represents the current NFL state."""

    week: int
    season: str
    season_type: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> NflState:
        """Create from API response."""
        return cls(
            week=data.get("week", 1),
            season=data.get("season", ""),
            season_type=data.get("season_type", "off"),
        )


@dataclass
class LeagueInfo:
    """Represents league information."""

    league_id: str
    name: str
    status: str
    season: str
    total_rosters: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LeagueInfo:
        """Create from API response."""
        return cls(
            league_id=data.get("league_id", ""),
            name=data.get("name", ""),
            status=data.get("status", ""),
            season=data.get("season", ""),
            total_rosters=data.get("total_rosters", 0),
        )


@dataclass
class Roster:
    """Represents a roster in the league."""

    roster_id: int
    owner_id: str | None
    wins: int
    losses: int
    ties: int
    fpts: float
    fpts_against: float
    waiver_position: int
    total_moves: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Roster:
        """Create from API response."""
        settings = data.get("settings") or {}
        fpts_int = settings.get("fpts") or 0
        fpts_dec = settings.get("fpts_decimal") or 0
        fpts_against_int = settings.get("fpts_against") or 0
        fpts_against_dec = settings.get("fpts_against_decimal") or 0

        return cls(
            roster_id=data.get("roster_id", 0),
            owner_id=data.get("owner_id"),
            wins=settings.get("wins") or 0,
            losses=settings.get("losses") or 0,
            ties=settings.get("ties") or 0,
            fpts=fpts_int + fpts_dec / 100,
            fpts_against=fpts_against_int + fpts_against_dec / 100,
            waiver_position=settings.get("waiver_position") or 0,
            total_moves=settings.get("total_moves") or 0,
        )


@dataclass
class LeagueUser:
    """Represents a user in the league."""

    user_id: str
    display_name: str
    team_name: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> LeagueUser:
        """Create from API response."""
        metadata = data.get("metadata") or {}
        return cls(
            user_id=data.get("user_id", ""),
            display_name=data.get("display_name", ""),
            team_name=metadata.get("team_name"),
        )


@dataclass
class Matchup:
    """Represents a matchup entry."""

    roster_id: int
    matchup_id: int | None
    points: float

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Matchup:
        """Create from API response."""
        return cls(
            roster_id=data.get("roster_id", 0),
            matchup_id=data.get("matchup_id"),
            points=data.get("points") or 0.0,
        )


@dataclass
class SleeperData:
    """Aggregated data from all Sleeper API endpoints."""

    nfl_state: NflState
    league: LeagueInfo
    rosters: list[Roster]
    users: list[LeagueUser]
    matchups: list[Matchup]
    roster_to_user: dict[int, LeagueUser] = field(default_factory=dict)
    standings: list[int] = field(default_factory=list)
    my_roster: Roster | None = None
    my_user: LeagueUser | None = None

    @staticmethod
    def build(
        nfl_state: NflState,
        league: LeagueInfo,
        rosters: list[Roster],
        users: list[LeagueUser],
        matchups: list[Matchup],
        user_id: str | None,
    ) -> SleeperData:
        """Build aggregated data with computed fields."""
        # Map owner_id -> LeagueUser
        user_by_id: dict[str, LeagueUser] = {u.user_id: u for u in users}
        placeholder = LeagueUser(user_id="", display_name="Unknown", team_name=None)

        roster_to_user: dict[int, LeagueUser] = {}
        for roster in rosters:
            if roster.owner_id and roster.owner_id in user_by_id:
                roster_to_user[roster.roster_id] = user_by_id[roster.owner_id]
            else:
                roster_to_user[roster.roster_id] = placeholder

        # Standings: sort by wins desc, then fpts desc
        sorted_rosters = sorted(
            rosters, key=lambda r: (r.wins, r.fpts), reverse=True
        )
        standings = [r.roster_id for r in sorted_rosters]

        # My roster/user lookup
        my_roster: Roster | None = None
        my_user: LeagueUser | None = None
        if user_id:
            my_user = user_by_id.get(user_id)
            for roster in rosters:
                if roster.owner_id == user_id:
                    my_roster = roster
                    break

        return SleeperData(
            nfl_state=nfl_state,
            league=league,
            rosters=rosters,
            users=users,
            matchups=matchups,
            roster_to_user=roster_to_user,
            standings=standings,
            my_roster=my_roster,
            my_user=my_user,
        )
