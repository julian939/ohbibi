import aiohttp
import logging
import utils.file_loader as file_loader

logger = logging.getLogger(__name__)

class TwitchAPI:
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    BASE_URL = "https://api.twitch.tv/helix"

    def __init__(self):
        env = file_loader.load_env()
        self.client_id = env["TWITCH_CLIENT_ID"]
        self.client_secret = env["TWITCH_CLIENT_SECRET"]
        self.access_token = None
        self.session = None

    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session

    async def authenticate(self) -> bool:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        session = await self._get_session()
        try:
            async with session.post(self.AUTH_URL, params=params) as resp:
                data = await resp.json()
                self.access_token = data.get("access_token")
                if not self.access_token:
                    logger.error(f"Authentication failed: {data}")
                    return False
                logger.info("Twitch authentication successful.")
                return True
        except Exception:
            logger.exception("Error during Twitch authentication")
            return False

    def _get_headers(self):
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

    async def _ensure_authenticated(self):
        if not self.access_token:
            await self.authenticate()

    async def _get(self, endpoint: str, params: dict = None):
        await self._ensure_authenticated()
        session = await self._get_session()

        try:
            async with session.get(f"{self.BASE_URL}/{endpoint}", headers=self._get_headers(), params=params) as resp:
                if resp.status == 401:
                    logger.warning("Token expired, re-authenticating...")
                    await self.authenticate()
                    return await self._get(endpoint, params)
                return await resp.json()
        except Exception:
            logger.exception(f"Failed GET request to {endpoint}")
            return {}

    async def get_user_info(self, username: str):
        data = await self._get("users", {"login": username})
        users = data.get("data")
        return users[0] if users else None

    async def get_stream_info(self, username: str):
        data = await self._get("streams", {"user_login": username})
        streams = data.get("data")
        return streams[0] if streams else None

    async def check_stream_title_for_keywords(self, username: str):
        config = file_loader.load_stream_config()
        keywords = config.get("stream_categories", [])
        stream_info = await self.get_stream_info(username)
        game = stream_info.get("game_name") if stream_info else None
        return any(k.lower() == game.lower() for k in keywords) if game else False

    async def close(self):
        if self.session:
            await self.session.close()

    async def __aenter__(self):
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
