import aiohttp
import utils.file_loader as file_loader

class TwitchAPI:
    def __init__(self):
        self.client_id = file_loader.load_env()["TWITCH_CLIENT_ID"]
        self.client_secret = file_loader.load_env()["TWITCH_CLIENT_SECRET"]
        self.access_token = None

    async def authenticate(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                data = await resp.json()
                self.access_token = data["access_token"]

    async def get_user_info(self, username):
        url = f"https://api.twitch.tv/helix/users?login={username}"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data["data"]:
                    return data["data"][0]
                else:
                    return None

    async def get_stream_info(self, username):
        url = f"https://api.twitch.tv/helix/streams?user_login={username}"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if data["data"]:
                    return data["data"][0] 
                else:
                    return None
