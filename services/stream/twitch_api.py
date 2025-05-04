import aiohttp
import utils.file_loader as file_loader

class TwitchAPI:
    def __init__(self):
        env = file_loader.load_env()
        self.client_id = env["TWITCH_CLIENT_ID"]
        self.client_secret = env["TWITCH_CLIENT_SECRET"]
        self.access_token = None

    async def authenticate(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, params=params) as resp:
                    if resp.status != 200:
                        print(f"[TwitchAPI] Authentifizierungsfehler: HTTP {resp.status}")
                        return False

                    data = await resp.json()
                    self.access_token = data.get("access_token")

                    if not self.access_token:
                        print(f"[TwitchAPI] Access Token nicht erhalten: {data}")
                        return False

                    return True

            except Exception as e:
                print(f"[TwitchAPI] Ausnahme bei Authentifizierung: {e}")
                return False

    async def get_user_info(self, username):
        url = f"https://api.twitch.tv/helix/users?login={username}"
        headers = self._get_auth_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    print(f"[TwitchAPI] Fehler beim Abrufen von Nutzerinformationen für {username}: HTTP {resp.status}")
                    return None

                data = await resp.json()
                return data["data"][0] if data.get("data") else None

    async def get_stream_info(self, username, retry=True):
        url = f"https://api.twitch.tv/helix/streams?user_login={username}"
        headers = self._get_auth_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 401 and retry:
                    print(f"[TwitchAPI] Access Token abgelaufen. Versuche neue Authentifizierung...")
                    if await self.authenticate():
                        return await self.get_stream_info(username, retry=False)
                    else:
                        return None

                if resp.status != 200:
                    print(f"[TwitchAPI] Fehler beim Abrufen von Stream-Info für {username}: HTTP {resp.status}")
                    return None

                try:
                    data = await resp.json()
                except Exception as e:
                    print(f"[TwitchAPI] Fehler beim JSON-Parsing für {username}: {e}")
                    return None

                if not isinstance(data, dict):
                    print(f"[TwitchAPI] Unerwartete Antwortstruktur für {username}: {data}")
                    return None

                if "data" not in data:
                    print(f"[TwitchAPI] 'data'-Feld fehlt in Twitch-Antwort für {username}: {data}")
                    return None

                return data["data"][0] if data["data"] else None

    def _get_auth_headers(self):
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
