import json
import os
from dotenv import load_dotenv

def load_config():
    
    load_dotenv()

    with open("./config.json", encoding="utf-8") as f:
        config = json.load(f)

    config["DISCORD_TOKEN"] = os.getenv("DISCORD_TOKEN")
    config["DISCORD_SERVER_ID"] = os.getenv("DISCORD_SERVER_ID")
    config["prefix"] = config["prefix"]

    return config