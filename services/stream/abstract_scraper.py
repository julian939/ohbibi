import logging
import requests

import utils.file_loader as file_loader

class AbstractScraper():

    def __init__(self, bot):
        self.config = file_loader.load_stream_config()

    async def check_abstract(self):
        streamers = self.config.get("streamers", [])
        for streamer in streamers["abstract"]:
            await self._check_streamer("abstract", streamer, self.is_abstract_live)

    def is_abstract_live(self, username):
        url = f"https://portal.abs.xyz/stream/{username}"
        r = requests.get(url, timeout=5)
        return "Live" in r.text

