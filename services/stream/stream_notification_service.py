import discord
import asyncio
import requests
import utils.file_loader as file_loader
import utils.utils as utils
from discord.ui import View, Button
from services.stream.twitch_api import TwitchAPI as TwitchAPI

class StreamNotificationService():
    def __init__(self, bot):
        self.bot = bot
        self.config = file_loader.load_config()
        self.stream_config = file_loader.load_stream_config()
        if self.config.get("bot_channel_id"):
            self.channel = self.bot.get_channel(self.config.get("bot_channel_id"))
        self.interval: int = self.stream_config.get("stream_scraper_interval", 5)
        self.live_status = {} 

    async def check_streams(self):
        await TwitchAPI().authenticate()
        while True:
            streamers = self.stream_config.get("streamers", [])
            for streamer in streamers:
                platform = streamer.get("platform")
                username = streamer.get("platform_username")
                discord_id = streamer.get("discord_id")
                if not (platform and username and discord_id):
                    continue

                is_live = False
                if platform == "twitch":
                    is_live = await self.is_twitch_live(username)
                elif platform == "abstract":
                    is_live = await self.is_abstract_live(username)

                # Vergleich mit bisherigem Live-Status
                previously_live = self.live_status.get(username, False)

                if is_live and not previously_live:
                    self.live_status[username] = True
                    print(f"{username} is live on {platform}")
                    # await self.send_twitch_live_message(username, discord_id)  # entkommentieren zum Testen
                elif not is_live and previously_live:
                    self.live_status[username] = False 

            await asyncio.sleep(self.interval * 60)

    async def is_twitch_live(self, streamer_name) -> bool:
        stream_info = await TwitchAPI().get_stream_info(streamer_name)
        return bool(stream_info)

    async def is_abstract_live(self, streamer_name) -> bool:
        try:
            url = f"https://portal.abs.xyz/stream/{streamer_name}"
            r = requests.get(url, timeout=5)
            return "Live" in r.text
        except requests.RequestException:
            return False


    async def send_twitch_live_message(self, streamer_name, discord_id):
        if self.channel:
            embed = utils.create_embed(description=f"# <:LogoTwitch:1136815276952915981> {streamer_name} is live on Twitch!", color=discord.Color.purple())

            thumbnail_url = f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{streamer_name}-440x248.jpg"
            embed.set_image(url=thumbnail_url)

            view = View()
            view.add_item(Button(
                label="Twitch",
                url=f"https://twitch.tv/{streamer_name}",
                emoji="<:LogoTwitch:1136815276952915981>",
                style=discord.ButtonStyle.link
            ))

            await self.channel.send(embed=embed, view=view)

    async def send_abstract_live_message(self, streamer_name, discord_id):
        if self.channel:
            ...