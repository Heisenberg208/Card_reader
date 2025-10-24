"""

This script provides a secure and flexible way to retrieve configuration values
for Python/Streamlit applications. It supports layered fallbacks in the following order:

    1. Streamlit's secrets.toml (if available)
    2. Environment variables (.env or system)
    3. A default fallback value

Each retrieval logs the source used, making it easy to trace configuration loading.
It is especially useful in environments where secrets may or may not be present.
"""

import os
import streamlit as st

from pathlib import Path
from pprint import pformat
from typing import Any, Dict
from utils.logger import logThis


def safe_get(secret_path: str, env_key: str = "", default: str = "") -> str:
    """
    Safely retrieve a configuration value from:
    1. Streamlit secrets (if secrets.toml exists)
    2. Environment variable
    3. Default fallback

    Logs the source used for each config value.
    """
    value = default
    source = "default"
    secrets_file = Path(".streamlit/secrets.toml")

    # Only try accessing secrets if the file exists

    if secrets_file.exists():
        try:
            secrets_dict: dict[str, Any] = dict(st.secrets)  # Convert to plain dict
            val = secrets_dict

            for key in secret_path.split("."):
                val = (
                    val.get(key, {}) if isinstance(val, dict) else getattr(val, key, {})
                )
            if val and val != {}:
                value = str(val)
                source = "secrets"
        except Exception as e:
            logThis.debug(f"Could not retrieve secret '{secret_path}': {e}")

    # If secrets not used, fallback to env
    if source != "secrets" and env_key:
        env_val = os.getenv(env_key)
        if env_val:
            value = env_val
            source = "env"

    logThis.info(
        f"Loaded config for '{env_key or secret_path}' from [{source}]",
        extra={"color": "yellow"},
    )
    return value


"""ThreadZip Configuration Utilities

This module contains helper functions and utilities used by the main configuration.
"""


def log_config(prefix: str, config_dict: dict) -> None:
    """Log configuration values in a structured and efficient way."""
    logThis.info(
        f"\n{prefix} Configuration:\n" + pformat(config_dict, indent=2),
        extra={"color": "yellow"},
    )


'''
def get_asset_path(project_root: Path, *paths: str) -> Path:
    """Get asset path relative to project root."""
    return project_root.joinpath("assets", *paths)
'''


def get_asset_path(*paths: str) -> Path:
    """
    Get asset path from either installed package (threadzip.assets) or
    fallback to project root (dev mode).

    Example:
        get_asset_path(PROJECT_ROOT, "images", "company_logo.png")
        get_asset_path(PROJECT_ROOT, "block_words")
    """
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    return PROJECT_ROOT.joinpath("assets", "images", *paths)


def setup_production_config(aws_config: Dict, s3_paths: Dict) -> Dict:
    """Setup production environment configuration."""
    config = {
        "STORAGE_OPTIONS": {
            "aws_region": aws_config["region"],
            "aws_access_key_id": aws_config["access_key_id"],
            "aws_secret_access_key": aws_config["secret_access_key"],
        },
        "DATABASE_PATH": s3_paths["database"],
        "IMAGE_FOLDER": aws_config["bucket_name"],
        "UPLOAD_FOLDER": s3_paths["uploaded"],
        "SINGLE_IMAGE_FOLDER": s3_paths["single"],
        "GROUP_IMAGE_FOLDER": s3_paths["group"],
        "GENERATED_IMAGE_FOLDER": s3_paths["generated"],
        "UPLOAD_FOLDER_FABRIC": s3_paths["search_uploads"],
        "RELATIVE_GENERATED_FOLDER": s3_paths["root_folder"],
        "UPLOAD_FOLDER_CARD": s3_paths["card_uploads"],
    }

    log_config(
        "Production",
        {
            "environment": "production",
            "storage_paths": {
                k: v for k, v in config.items() if k != "STORAGE_OPTIONS"
            },
            "s3_config": {
                k: "[HIDDEN]" if "key" in k else v for k, v in aws_config.items()
            },
        },
    )

    return config


def setup_development_config(project_root: Path, image_base: Path) -> Dict:
    """Setup development environment configuration."""
    config = {
        "STORAGE_OPTIONS": {},
        "DATABASE_PATH": str(Path(project_root, "db")),
        "IMAGE_FOLDER": str(image_base),
        "UPLOAD_FOLDER": str(get_asset_path("uploaded")),
        "SINGLE_IMAGE_FOLDER": str(get_asset_path("uploaded", "single")),
        "GROUP_IMAGE_FOLDER": str(get_asset_path("uploaded", "group")),
        "GENERATED_IMAGE_FOLDER": str(get_asset_path("generated")),
        "RELATIVE_GENERATED_FOLDER": str(
            Path("src", "assets", "images", "sample_table_images")
        ),
        "UPLOAD_FOLDER_FABRIC": str(get_asset_path("uploaded", "search")),
        "UPLOAD_FOLDER_CARD": str(get_asset_path("uploaded", "card")),
    }

    # Create directories for development
    for key, path in config.items():
        if ("FOLDER" in key or "DATABASE_PATH" in key) and isinstance(
            path, (str, Path)
        ):
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                logThis.debug(f"Created: {path}")
            except Exception as e:
                logThis.warning(f"Could not create {path}: {e}")

    log_config(
        "Development",
        {
            "environment": "development",
            "project_root": str(project_root),
            "storage_paths": {
                k: v for k, v in config.items() if k != "STORAGE_OPTIONS"
            },
        },
    )
    logThis.info("=" * 78)
    return config


def validate_configuration(
    environment: str,
    database_path: str,
    image_folder: str,
    aws_config: Dict,
) -> bool:
    """Validate the configuration based on environment."""
    issues = []

    if environment.lower() == "development":
        for path in [database_path, image_folder]:
            if not Path(path).exists():
                try:
                    Path(path).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create path {path}: {e}")

    if environment.lower() == "production" and not all(
        [aws_config["access_key_id"], aws_config["secret_access_key"]]
    ):
        issues.append("Missing AWS credentials")

    if issues:
        for issue in issues:
            logThis.error(f"Configuration issue: {issue}", extra={"color": "yellow"})
        return False

    logThis.info("Configuration validation passed", extra={"color": "yellow"})
    return True
