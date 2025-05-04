import discord
import logging
import os
import asyncio
from discord.ext import commands
import utils.file_loader as file_loader
from utils.logger import setup_logger 
from services.stream.twitch_api import TwitchAPI as TwitchAPI
from services.stream.stream_notification_service import StreamNotificationService as StreamNotificationService

config = file_loader.load_config()
env = file_loader.load_env()
setup_logger()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.get("prefix", "!"), intents=intents)


async def _register_cogs():
    try:
        guild = discord.Object(id=env["DISCORD_SERVER_ID"]) 
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        logging.info("Synchronised cogs sucessful.")
    except Exception as e:
        logging.error(f"Error while synchronising: {e}")

async def _load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logging.info(f"Cog {filename} loaded successful.")
            except Exception as e:
                logging.error(f"Error while loading cog {filename}: {e}")

@bot.event
async def on_ready():
    logging.info(f'Bot is online as {bot.user}')

    await bot.change_presence(activity=discord.Streaming(name="Oh Baby! Kart", url="https://www.twitch.tv/directory/category/oh-baby-kart"))

    await _load_cogs()
    await _register_cogs()
    
    asyncio.create_task(StreamNotificationService(bot).check_streams())

    print("Registered Slash-Commands:")
    for command in bot.tree.get_commands(guild=discord.Object(id=env["DISCORD_SERVER_ID"])):
        print(f"- {command.name}")

bot.run(env["DISCORD_TOKEN"])
