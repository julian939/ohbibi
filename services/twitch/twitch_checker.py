from services.twitch.twitch_api import TwitchAPI

class TwitchStreamChecker:
    def __init__(self, streamer, channel):
        self.username = streamer["platform_username"]
        self.discord_id = streamer["discord_id"]
        self.api = TwitchAPI()
        self.channel = channel
        self.was_live = False

    async def check_and_notify(self):
        async with self.api as api:
            is_live = await api.get_stream_info(self.username) is not None
            has_keyword = await api.check_stream_title_for_keywords(self.username)

            if is_live and not self.was_live and has_keyword:
                await self._send_notification()
                self.was_live = True
            elif not is_live and self.was_live:
                self.was_live = False

    async def _send_notification(self):
        import discord
        from discord.ui import View, Button

        async with self.api as api:
            streamer_info = await api.get_user_info(self.username)
            stream_info = await api.get_stream_info(self.username)
            if not streamer_info or not stream_info:
                return

            title = stream_info['title']
            category = stream_info['game_name']
            profile_url = streamer_info['profile_image_url']
            thumbnail_url = f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{self.username}-440x248.jpg"

            embed = discord.Embed(
                title=f"{self.username} is live on Twitch!",
                description=f"\n**Game:** {category}\n**Title:** {title}",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=profile_url)
            embed.set_image(url=thumbnail_url)

            view = View()
            view.add_item(Button(
                label="Watch on Twitch",
                url=f"https://twitch.tv/{self.username}",
                emoji="<:LogoTwitch:1136815276952915981>",
                style=discord.ButtonStyle.link
            ))

            await self.channel.send(embed=embed, view=view)
