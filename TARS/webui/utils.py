# Part of TARS integrated web UI – prepared for HTMX + Tailwind

from pathlib import Path
from TARS.config.loader import load_config as _load_config
from TARS.config.schema import Config

def load_tars_config() -> Config:
    """Load TARS configuration from default ~/.TARS/config.json."""
    # The default loader handles the path expansion if needed, 
    # but here we follow the user's explicit path ~/.TARS/config.json
    config_path = Path.home() / ".TARS" / "config.json"
    if not config_path.exists():
        return Config()
    return _load_config(config_path)
