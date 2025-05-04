import discord
import asyncio
import requests
from discord.ui import View, Button
from services.stream.twitch_api import TwitchAPI
import utils.file_loader as file_loader

class StreamNotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.config = file_loader.load_config()
        self.stream_config = file_loader.load_stream_config()
        self.interval: int = self.stream_config.get("stream_scraper_interval", 5)
        
        # Instanz der TwitchAPI nur einmal erstellen
        self.twitch_api = TwitchAPI()
        self.channel = self.bot.get_channel(self.config.get("bot_channel_id"))
        
        # Speichern des Live-Status jedes Streamers
        self.live_status = {}

    async def check_streams(self):
        await self.twitch_api.authenticate()
        
        while True:
            streamers = self.stream_config.get("streamers", {})
            for streamer in streamers:
                platform = streamer.get("platform", None)
                platform_username = streamer.get("platform_username", None)
                discord_id = streamer.get("discord_id", None)
                
                if platform == "twitch" and platform_username and discord_id:
                    # Überprüfen, ob der Streamer live ist
                    is_live = await self.is_twitch_live(platform_username)
                    if is_live and self.live_status.get(platform_username) != "live":
                        # Falls der Streamer live ist und noch keine Benachrichtigung gesendet wurde
                        await self.send_twitch_live_message(platform_username, discord_id)
                        self.live_status[platform_username] = "live"  # Setze den Status auf "live"
                    elif not is_live and self.live_status.get(platform_username) == "live":
                        # Falls der Streamer nicht mehr live ist, Status zurücksetzen
                        self.live_status[platform_username] = "offline"
                
                elif platform == "abstract" and platform_username and discord_id:
                    # Überprüfen, ob der Streamer auf Abstract live ist
                    is_live = await self.is_abstract_live(platform_username)
                    if is_live and self.live_status.get(platform_username) != "live":
                        # Falls der Streamer live ist und noch keine Benachrichtigung gesendet wurde
                        await self.send_abstract_live_message(platform_username, discord_id)
                        self.live_status[platform_username] = "live"  # Setze den Status auf "live"
                    elif not is_live and self.live_status.get(platform_username) == "live":
                        # Falls der Streamer nicht mehr live ist, Status zurücksetzen
                        self.live_status[platform_username] = "offline"

            await asyncio.sleep(self.interval * 60)  # Warten für den nächsten Check

    async def is_twitch_live(self, streamer_name) -> bool:
        # Nutzt die gespeicherte TwitchAPI-Instanz, um den Stream-Status abzufragen
        stream_info = await self.twitch_api.get_stream_info(streamer_name)
        return stream_info is not None  # True, wenn der Streamer live ist, andernfalls False

    async def is_abstract_live(self, streamer_name) -> bool:
        # Abfragen, ob der Streamer auf Abstract live ist
        url = f"https://portal.abs.xyz/stream/{streamer_name}"
        r = requests.get(url, timeout=5)
        return "Live" in r.text

    async def send_twitch_live_message(self, streamer_name, discord_id):
        # Streamer-Info abrufen (Profilbild, Streamtitel etc.)
        streamer_info = await self.twitch_api.get_user_info(streamer_name)
        if not streamer_info:
            return
        
        profile_picture_url = streamer_info['profile_image_url']
        stream_info = await self.twitch_api.get_stream_info(streamer_name)
        if not stream_info:
            return

        title = stream_info['title']
        category = stream_info['game_name']
        thumbnail_url = f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{streamer_name}-440x248.jpg"

        # Embed für den Live-Stream
        embed = discord.Embed(
            title=f"🚨 {streamer_name} is live on Twitch! 🚨",
            description=f"\n**Game:** {category}\n**Title:** {title}",
            color=discord.Color.purple()
        )
        
        embed.set_thumbnail(url=profile_picture_url)
        embed.set_image(url=thumbnail_url)

        # View mit Button zum Stream
        view = View()
        view.add_item(Button(
            label="Watch on Twitch",
            url=f"https://twitch.tv/{streamer_name}",
            emoji="<:LogoTwitch:1136815276952915981>",  # Twitch-Emoji (falls du ein benutzerdefiniertes Emoji hast)
            style=discord.ButtonStyle.link
        ))

        try:
            role = self.channel.guild.get_role(1368594398396416010)
            role_mention = f"{role.mention}" if role else "" 

            await self.channel.send(content=f"{role_mention}", embed=embed, view=view)
        except Exception as e:
            await self.channel.send(embed=embed, view=view)


    async def send_abstract_live_message(self, streamer_name, discord_id):
        # Abstract stream logic
        url = f"https://portal.abs.xyz/stream/{streamer_name}"
        r = requests.get(url, timeout=5)
        
        if "Live" not in r.text:
            return  # If the stream isn't live, stop here

        # Abstract stream info
        embed = discord.Embed(
            title=f"🚨 {streamer_name} is live on Abstract! 🚨",
            description=f"**Check out their stream now!**",
            color=discord.Color.blue()
        )

        view = View()
        view.add_item(Button(
            label="Watch on Abstract",
            url=f"https://portal.abs.xyz/stream/{streamer_name}",
            style=discord.ButtonStyle.link
        ))

        try:
            role = self.channel.guild.get_role(1368594398396416010)
            role_mention = f"{role.mention}" if role else "" 

            await self.channel.send(content=f"{role_mention}", embed=embed, view=view)
        except Exception as e:
            await self.channel.send(embed=embed, view=view)

