import discord
from discord.ext import commands
import os
from utils.config_loader import load_config
from utils.logger import setup_logger 
import logging

config = load_config()
setup_logger()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

async def register_cogs():
    try:
        guild = discord.Object(id=config["DISCORD_SERVER_ID"]) 
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        logging.info("Synchronised cogs sucessful.")
    except Exception as e:
        logging.error(f"Error while synchronising: {e}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logging.info(f"Cog {filename} loaded successful.")
            except Exception as e:
                logging.error(f"Error while loading cog {filename}: {e}")

@bot.event
async def on_ready():
    logging.info(f'Bot ist online als {bot.user}')

    await load_cogs()
    await register_cogs()

    print("Registered Slash-Commands:")
    for command in bot.tree.get_commands(guild=discord.Object(id=config["DISCORD_SERVER_ID"])):
        print(f"- {command.name}")

bot.run(config["DISCORD_TOKEN"])
