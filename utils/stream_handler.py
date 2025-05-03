import logging
import asyncio

import utils.file_loader as file_loader
import services.stream.twitch_api as twitch
import services.stream.abstract_scraper as abstract

class StreamHandler():

    def __init__(self, bot):
        self.config = file_loader.load_stream_config()
        self.bot = bot
        self.live_status = {}
        self.interval = self.config.get("stream_scraper_interval", 5)

    #start checking for stream informations
    async def start_checking(self):
        while True:
            #check twitch
            #check abstract
            await asyncio.sleep(self.interval)

    #checks if streamers are online
    async def _check_streamer(self, platform, streamer_name, check_func):
        try:
            currently_live = check_func(streamer_name)
        except Exception:
            currently_live = False

        was_live = self.live_status.get((platform, streamer_name), False)

        if currently_live and not was_live:
            logging.info(f"{streamer_name} is live on {platform}!")
        
        self.live_status[(platform, streamer_name)] = currently_live

    

    