import json
import os
from dotenv import load_dotenv

def load_config():
    if not os.path.exists("./config.json"):
        return {}
    with open("./config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open("./config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def load_env():
    load_dotenv()
    config = {}

    config["DISCORD_TOKEN"] = os.getenv("DISCORD_TOKEN")
    config["DISCORD_SERVER_ID"] = os.getenv("DISCORD_SERVER_ID")

    return config