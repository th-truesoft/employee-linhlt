from typing import Dict, List, Optional
import json
import os
from pathlib import Path

# Default organization configurations
DEFAULT_ORGANIZATION_CONFIGS = {
    "default": {
        "columns": ["name", "email", "phone", "status", "department", "position", "location"]
    },
    "org1": {
        "columns": ["name", "email", "department", "position"]
    },
    "org2": {
        "columns": ["name", "status", "department", "location"]
    },
    "org3": {
        "columns": ["name", "phone", "department", "position", "location"]
    }
}

# Path to the organization configurations file
CONFIG_FILE_PATH = Path("organization_configs.json")


def get_organization_columns(organization_id: str) -> List[str]:
    configs = _load_configurations()
    
    # Return the organization's config if it exists, otherwise return default
    return configs.get(organization_id, configs["default"])["columns"]


def _load_configurations() -> Dict:
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If there's an error reading the file, use defaults
            return DEFAULT_ORGANIZATION_CONFIGS
    else:
        # If the file doesn't exist, create it with defaults
        _save_configurations(DEFAULT_ORGANIZATION_CONFIGS)
        return DEFAULT_ORGANIZATION_CONFIGS


def _save_configurations(configs: Dict) -> None:
    try:
        with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(configs, f, indent=2)
    except IOError:
        pass


def update_organization_columns(organization_id: str, columns: List[str]) -> bool:
    configs = _load_configurations()
    
    if organization_id in configs:
        configs[organization_id]["columns"] = columns
    else:
        configs[organization_id] = {"columns": columns}
    
    _save_configurations(configs)
    return True
