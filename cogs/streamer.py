import discord
from discord import app_commands, Embed, File
from typing import Literal
import utils.file_loader as file_loader

class Streamer(app_commands.Group):

    def __init__(self):
        super().__init__(name="streamer", description="Streamer management")
        self.stream_config = file_loader.load_stream_config()

    async def has_permission(self, interaction: discord.Interaction) -> bool:
        return isinstance(interaction.user, discord.Member) and any(
            role.id == self.stream_config.get("stream_permission_role") for role in interaction.user.roles
        )

    @app_commands.command(description="Add streamer to the list.")
    @app_commands.describe(
        user="Discord member",
        name="Streamer name on the platform",
        platform="Streaming platform"
    )
    async def add(self, interaction: discord.Interaction, user: discord.Member, name: str, platform: Literal["twitch", "abstract"]):
        stream_config = self.stream_config

        if not await self.has_permission(interaction):
            await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        streamers = stream_config.get("streamers", [])

        if any(s["platform_username"].lower() == name.lower() and s["platform"] == platform for s in streamers):
            await interaction.response.send_message(f"⚠️ **{name}** is already in the list for **{platform}**.", ephemeral=True)
            return

        new_streamer = {
            "platform_username": name,
            "platform": platform,
            "discord_id": user.id
        }
        streamers.append(new_streamer)
        stream_config["streamers"] = streamers

        file_loader.save_stream_config(stream_config)
        self.stream_config = file_loader.load_stream_config()

        await interaction.response.send_message(
            f"✅ **{name}** was added to the list for **{platform}** (linked to {user.mention}).",
            ephemeral=True
        )

    @app_commands.command(description="Remove streamer from the list.")
    @app_commands.describe(name="Streamer name on the platform")
    async def remove(self, interaction: discord.Interaction, name: str, platform: Literal["twitch", "abstract"]):
        if not await self.has_permission(interaction):
            await interaction.response.send_message("🚫 You don't have permission to use this command.", ephemeral=True)
            return

        stream_config = self.stream_config
        streamers = stream_config.get("streamers", [])

        index_to_remove = next(
            (i for i, s in enumerate(streamers)
            if s["platform_username"].lower() == name.lower() and s["platform"] == platform),
            None
        )

        if index_to_remove is None:
            await interaction.response.send_message(f"⚠️ **{name}** is not in the list for **{platform}**.", ephemeral=True)
            return

        del streamers[index_to_remove]
        stream_config["streamers"] = streamers
        file_loader.save_stream_config(stream_config)
        self.stream_config = file_loader.load_stream_config()

        await interaction.response.send_message(f"🗑️ **{name}** was removed from the list for **{platform}**.", ephemeral=True)


    @app_commands.command(description="List of all streamers.")
    async def list(self, interaction: discord.Interaction):
        streamers = self.stream_config.get("streamers", [])

        twitch_streamers = [s["platform_username"] for s in streamers if s["platform"] == "twitch"]
        abstract_streamers = [s["platform_username"] for s in streamers if s["platform"] == "abstract"]

        embed = Embed(
            title="List of Streamers",
            description="Here are the currently registered streamers:",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")

        if twitch_streamers:
            twitch_links = "\n".join(f"- [{name}](https://www.twitch.tv/{name})" for name in twitch_streamers)
            embed.add_field(name="**Twitch:**", value=twitch_links, inline=False)

        if abstract_streamers:
            abstract_links = "\n".join(f"- [{name}](https://portal.abs.xyz/stream/{name})" for name in abstract_streamers)
            embed.add_field(name="**Abstract:**", value=abstract_links, inline=False)

        if not twitch_streamers and not abstract_streamers:
            embed.add_field(name="📭 No streamers found.", value="The list is currently empty.", inline=False)

        await interaction.response.send_message(
            embed=embed,
            file=File('./data/thumbnail.png', filename='thumbnail.png')
        )

async def setup(bot):
    bot.tree.add_command(Streamer())