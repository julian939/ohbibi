import logging
import requests
import asyncio

import utils.file_loader as file_loader

class StreamScraper:

    def __init__(self):
        self.config = file_loader.load_config()
        self.live_status = {}
        self.interval = self.config.get("stream_scraper_interval", 5) * 60

    async def start_checking(self):
        while True:
            logging.info("Checking livestreams")

            self.check_twitch()
            self.check_abstract()
            
            await asyncio.sleep(self.interval)

    def check_twitch(self):
        streamers = self.config.get("streamers", [])
        for streamer in streamers["twitch"]:
            self._check_streamer("twitch", streamer, self.is_twitch_live)

    def check_abstract(self):
        streamers = self.config.get("streamers", [])
        for streamer in streamers["abstract"]:
            self._check_streamer("abstract", streamer, self.is_abstract_live)

    def _check_streamer(self, platform, streamer_name, check_func):
        try:
            currently_live = check_func(streamer_name)
        except Exception:
            currently_live = False

        was_live = self.live_status.get((platform, streamer_name), False)

        if currently_live and not was_live:
            #To-Do: trigger embed message
            logging.info(f"{streamer_name} is live on {platform}!")
        
        self.live_status[(platform, streamer_name)] = currently_live

    def is_twitch_live(self, username):
        url = f"https://www.twitch.tv/{username}"
        r = requests.get(url, timeout=5)
        return "isLiveBroadcast" in r.text

    def is_abstract_live(self, username):
        url = f"https://portal.abs.xyz/stream/{username}"
        r = requests.get(url, timeout=5)
        return "Live" in r.text

