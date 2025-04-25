import discord
from discord import app_commands
from typing import Literal
import utils.file_loader as file_loader
import utils.utils as utils

class Streamer(app_commands.Group):

    def __init__(self):
        super().__init__(name="streamer", description="Streamer management")
        self.config = file_loader.load_config()

    async def has_permission(self, interaction: discord.Interaction) -> bool:
        return isinstance(interaction.user, discord.Member) and any(
            role.id == self.config.get("streamer_permission_role") for role in interaction.user.roles
        )

    @app_commands.command(description="Add streamer to the list.")
    @app_commands.describe(
        name="Streamer name on the platform",
        platform="Streaming platform"
    )
    async def add(self, interaction: discord.Interaction, name: str, platform: Literal["twitch", "abstract"]):
        config = self.config

        if not await self.has_permission(interaction):
            await interaction.response.send_message("🚫 You dont have the permission to use this command.", ephemeral=True)
            return

        streamers = config.get("streamers", {})
        if platform not in streamers:
            streamers[platform] = []

        if name in streamers[platform]:
            await interaction.response.send_message(f"⚠️ **{name}** is already in the list for **{platform}**.", ephemeral=True)
            return
        
        streamers[platform].append(name)
        config["streamers"] = streamers
        file_loader.save_config(config) 
        self.config = file_loader.load_config()

        await interaction.response.send_message(f"✅ **{name}** got added to the list of **{platform}**.", ephemeral=True)

    @app_commands.command(description="Remove streamer from the list.")
    @app_commands.describe(name="Streamer name on the platform")
    async def remove(self, interaction: discord.Interaction, name: str):
        if not await self.has_permission(interaction):
            await interaction.response.send_message("🚫 You dont have the permission to use this command.", ephemeral=True)
            return

        config = self.config
        streamers = config.get("streamers", {})

        removed = False
        for platform in streamers:
            if name in streamers[platform]:
                streamers[platform].remove(name)
                removed = True
                break

        if not removed:
            await interaction.response.send_message(f"⚠️ **{name}** isnt in the list", ephemeral=True)
            return

        config["streamers"] = streamers
        file_loader.save_config(config)
        self.config = file_loader.load_config()

        await interaction.response.send_message(f"🗑️ **{name}** got removed from the list.", ephemeral=True)

    @app_commands.command(description="List of all streamers.")
    async def list(self, interaction: discord.Interaction):
        config = self.config
        streamers = config.get("streamers", {})

        twitch_streamers = streamers.get("twitch", [])
        abstract_streamers = streamers.get("abstract", [])

        fields = []

        if twitch_streamers:
            fields.append(("**Twitch:**", "\n".join(f"- {name}" for name in twitch_streamers)))
        
        if abstract_streamers:
            fields.append(("**Abstract:**", "\n".join(f"- {name}" for name in abstract_streamers)))
        
        if not twitch_streamers and not abstract_streamers:
            fields.append("📭 No streamer in the list.")

        embed = utils.create_embed(
            title="",
            description="📺 Streamer",
            fields=fields
        )

        await interaction.response.send_message(
            embed=embed, 
            #ephemeral=False, 
            file=discord.File('./data/thumbnail.png', filename='thumbnail.png')  
        )



async def setup(bot):
    bot.tree.add_command(Streamer())