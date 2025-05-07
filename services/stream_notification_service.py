import asyncio
import utils.file_loader as file_loader
from services.twitch.twitch_checker import TwitchStreamChecker
from services.abstract.abstract_checker import AbstractStreamChecker

class StreamNotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.config = file_loader.load_config()
        self.stream_config = file_loader.load_stream_config()
        self.interval: int = self.stream_config.get("stream_scraper_interval", 5)
        self.channel = self.bot.get_channel(self.config.get("bot_channel_id"))

        self.checkers = self._init_checkers()

    def _init_checkers(self):
        checkers = []
        for streamer in self.stream_config.get("streamers", []):
            platform = streamer.get("platform")
            if platform == "twitch":
                checkers.append(TwitchStreamChecker(streamer, self.channel))
            elif platform == "abstract":
                checkers.append(AbstractStreamChecker(streamer, self.channel))
        return checkers

    async def check_streams(self):
        while True:
            tasks = [checker.check_and_notify() for checker in self.checkers]
            await asyncio.gather(*tasks)
            await asyncio.sleep(self.interval * 60)
