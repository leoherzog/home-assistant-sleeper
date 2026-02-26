"""Diagnostics support for the Sleeper integration."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from . import SleeperConfigEntry

REDACT_FIELDS = {"user_id", "owner_id"}


def _redact(data: Any) -> Any:
    """Recursively redact sensitive fields from a data structure."""
    if isinstance(data, dict):
        return {
            key: "**REDACTED**" if key in REDACT_FIELDS else _redact(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [_redact(item) for item in data]
    return data


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: SleeperConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    if coordinator.data is None:
        return {"error": "No data available yet"}
    data = asdict(coordinator.data)
    return _redact(data)
