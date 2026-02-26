"""The Sleeper integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SleeperApiClient
from .coordinator import SleeperCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type SleeperConfigEntry = ConfigEntry[SleeperCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: SleeperConfigEntry) -> bool:
    """Set up Sleeper from a config entry."""
    session = async_get_clientsession(hass)
    api = SleeperApiClient(session)

    coordinator = SleeperCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SleeperConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
