# database.py

import json
from typing import List, Dict, Any
from datetime import datetime

# Define the path to the JSON database files
PHONE_DATABASE_FILE = "phone_inventory.json"
LOG_DATABASE_FILE = "action_log.json"


# --- Phone Database Functions ---
def load_phone_database() -> List[Dict[str, Any]]:
    """Load the phone inventory from the JSON file."""
    try:
        with open(PHONE_DATABASE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        save_phone_database([])
        return []


def save_phone_database(data: List[Dict[str, Any]]):
    """Save the phone inventory to the JSON file."""
    with open(PHONE_DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- Action Log Database Functions ---
def default_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()


def load_log_database() -> List[Dict[str, Any]]:
    """Load the action log from the JSON file."""
    try:
        with open(LOG_DATABASE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        save_log_database([])
        return []


def save_log_database(data: List[Dict[str, Any]]):
    """Save the action log to the JSON file."""
    with open(LOG_DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4, default=default_converter)


# Initialize databases
db: List[Dict[str, Any]] = load_phone_database()
action_log_db: List[Dict[str, Any]] = load_log_database()
