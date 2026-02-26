"""Constants for the Sleeper integration."""

from datetime import timedelta

DOMAIN = "sleeper"

CONF_LEAGUE_ID = "league_id"
CONF_USERNAME = "username"
CONF_USER_ID = "user_id"
CONF_LEAGUE_NAME = "league_name"

API_BASE_URL = "https://api.sleeper.app/v1"

UPDATE_INTERVAL_GAME_WINDOW = timedelta(minutes=5)
UPDATE_INTERVAL_GAME_DAY = timedelta(minutes=15)
UPDATE_INTERVAL_REGULAR = timedelta(hours=1)
UPDATE_INTERVAL_OFFSEASON = timedelta(hours=24)

