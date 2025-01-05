import json

from utils.logger import logger

# The file path to the config file
CONFIG_FILE = 'utils/configs.json'


def load_config() -> dict:
    # Load the configuration file if it exists, otherwise return an empty dictionary
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_config(config) -> None:
    # Save the config dict to the config file
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)


def initiate_channel_config(chat_id: str):
    """
    Initialize the configuration for a channel, if no config exists.

    Args:
        chat_id (str): The ID of the channel.
    """

    config = load_config()

    if chat_id not in config:
        config[chat_id] = {
            "posting_interval": 14400,  # 4 hours by default
            "mode": "simultaneous",
            "pair_list": [],
            "channel_link": None
        }

        save_config(config)
        logger.info(f"Initialized configuration for channel {chat_id}")

    else:
        logger.info(f"Configuration for channel {chat_id} already exists")

    return config
