import aiohttp
import logging
from utils.file_loader import load_env

logger = logging.getLogger(__name__)

class TwitchAPI:
    def __init__(self):
        env = load_env()
        self.client_id = env["TWITCH_CLIENT_ID"]
        self.client_secret = env["TWITCH_CLIENT_SECRET"]
        self.access_token = None

    async def authenticate(self) -> bool:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, params=params) as resp:
                    data = await resp.json()
                    self.access_token = data.get("access_token")
                    if not self.access_token:
                        logger.error(f"Authentication failed: {data}")
                        return False
                    logger.info("Twitch authentication successful.")
                    return True
            except Exception as e:
                logger.exception("Error during Twitch authentication")
                return False

    async def get_user_info(self, username):
        if not self.access_token:
            await self.authenticate()

        url = f"https://api.twitch.tv/helix/users?login={username}"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()

                    if "data" in data and data["data"]:
                        return data["data"][0] 
                    else:
                        logger.warning(f"No user data found for {username}.")
                        return None
            except Exception as e:
                logger.exception(f"Failed to fetch user info for {username}")
                return None

    async def get_stream_info(self, username):
        if not self.access_token:
            await self.authenticate()

        url = f"https://api.twitch.tv/helix/streams?user_login={username}"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()

                    if "data" in data and data["data"]:
                        return data["data"][0] 
                    else:
                        logger.info(f"Streamer {username} is not currently live.")
                        return None
            except Exception as e:
                logger.exception(f"Failed to fetch stream info for {username}")
                return None
