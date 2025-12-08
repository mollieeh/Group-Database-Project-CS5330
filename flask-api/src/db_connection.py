import configparser
from pathlib import Path
from typing import Dict, Union

import mysql.connector


# Default location for the configuration file
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "../config.ini"


def load_db_config(config_path: Union[str, Path] = DEFAULT_CONFIG_PATH) -> Dict[str, Union[str, int]]:
    """Load MySQL connection settings from a config.ini file."""
    config = configparser.ConfigParser()
    if not config.read(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    if "mysql" not in config:
        raise KeyError("Missing [mysql] section in config file")

    mysql_section = config["mysql"]
    required_keys = ["host", "port", "user", "password", "database"]
    missing = [key for key in required_keys if key not in mysql_section]
    if missing:
        raise KeyError(f"Missing required config keys: {', '.join(missing)}")

    return {
        "host": mysql_section["host"],
        "port": mysql_section.getint("port"),
        "user": mysql_section["user"],
        "password": mysql_section["password"],
        "database": mysql_section["database"],
    }


def create_mysql_connection(config_path: Union[str, Path] = DEFAULT_CONFIG_PATH) -> mysql.connector.MySQLConnection:
    """Create and return a MySQL connection using settings from config.ini."""
    db_config = load_db_config(config_path)
    return mysql.connector.connect(**db_config)
