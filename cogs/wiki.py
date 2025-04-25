import discord
from discord import app_commands

class Wiki(app_commands.Group):
    @app_commands.command(description="Answers with Pong!")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong!")

async def setup(bot):
    bot.tree.add_command(Wiki(name="wiki", description="get values from thge wiki"))
