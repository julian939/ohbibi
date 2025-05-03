import discord
import utils.file_loader as file_loader
import utils.utils as utils
from discord.ui import View, Button

class StreamNotificationService():
    def __init__(self, bot):
        self.bot = bot
        self.config = file_loader.load_config()

    async def send_stream_live_message(self, streamer_name: str):
        stream_link = f"https://www.twitch.tv/{streamer_name}"

        channel_id = self.config.get("bot_channel_id")
        channel = self.bot.get_channel(channel_id)

        if channel:
            embed = utils.create_embed(description=f"# <:LogoTwitch:1136815276952915981> {streamer_name} is live on Twitch!", color=discord.Color.purple())

            thumbnail_url = f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{streamer_name}-440x248.jpg"
            embed.set_image(url=thumbnail_url)
            #embed.set_thumbnail(url="https://play-lh.googleusercontent.com/Y6epalNGUKPgWyQpDCgVL621EgmOmXBWfQoJdaM8v0irKWEII5bEDvpaWp7Mey2MVg=w240-h480-rw")
            #embed.set_author(name=streamer_name, url=stream_link)

            view = View()
            view.add_item(Button(
                label="Twitch",
                url=stream_link,
                emoji="<:LogoTwitch:1136815276952915981>",
                style=discord.ButtonStyle.link
            ))

            await channel.send(embed=embed, view=view)