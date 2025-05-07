from services.abstract.abstract_scraper import AbstractScraper

class AbstractStreamChecker:
    def __init__(self, streamer, channel):
        self.username = streamer["platform_username"]
        self.discord_id = streamer["discord_id"]
        self.scraper = AbstractScraper()
        self.channel = channel
        self.was_live = False

    async def check_and_notify(self):
        is_live = await self.scraper.is_live(self.username)
        has_keyword = await self.scraper.check_stream_title_for_keywords(self.username)

        if is_live and not self.was_live and has_keyword:
            await self._send_notification()
            self.was_live = True
        elif not is_live and self.was_live:
            self.was_live = False

    async def _send_notification(self):
        import discord
        from discord.ui import View, Button

        url = f"https://portal.abs.xyz/stream/{self.username}"
        member = self.channel.guild.get_member(self.discord_id)
        mention = member.mention if member else self.username

        view = View()
        view.add_item(Button(
            label="Watch on Abstract",
            url=url,
            emoji="🎥",
            style=discord.ButtonStyle.link
        ))

        message = (
            f"### {mention} is live on Abstract!\n"
            f"Go check it out! {url}" 
        )

        await self.channel.send(content=message, view=view)