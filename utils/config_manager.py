import json

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
