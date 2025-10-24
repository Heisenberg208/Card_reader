"""ThreadZip Constants Configuration

This module contains all the configuration constants for the ThreadZip application,
organized by their purpose and environment (development/production).
"""

from pathlib import Path

from dotenv import load_dotenv

from utils.config_helper import (
    get_asset_path,
    safe_get,
    setup_development_config,
    setup_production_config,
    validate_configuration,
)
from utils.logger import logThis

# === Load Environment Variables ===
load_dotenv()
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GITHUB_TOKEN = safe_get("git.GITHUB_TOKEN", "GITHUB_TOKEN")
CACHE_DIR = Path.home() / ".cache" / "tz_script"
MODELS = {
    "best.pt": {
        "source": "github",
        "api_url": "https://api.github.com/repos/recursivezero/tz-script/releases/tags/v3.5.0",
    },
}

# === Basic Configs ===
ENVIRONMENT = safe_get("env.ENVIRONMENT", "ENVIRONMENT", "development")
logThis.info(f"Environment: {ENVIRONMENT}", extra={"color": "yellow"})
logThis.info(f"Project root: {PROJECT_ROOT}", extra={"color": "yellow"})
gemini_key = safe_get("api.GEMINI_API", "GEMINI_API")
# === AWS Configuration ===
AWS_ACCESS_KEY_ID = safe_get("aws.AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = safe_get("aws.AWS_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY")
AWS_REGION = safe_get("aws.AWS_REGION", "AWS_REGION", "us-east-1")
AWS_BUCKET_NAME = safe_get(
    "aws.AWS_BUCKET_NAME", "AWS_BUCKET_NAME", "fabric-storage-bucket"
)

AWS_CONFIG = {
    "access_key_id": AWS_ACCESS_KEY_ID,
    "secret_access_key": AWS_SECRET_ACCESS_KEY,
    "region": AWS_REGION,
    "bucket_name": AWS_BUCKET_NAME,
}

# === Validate AWS Configuration ===
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION:
    logThis.info("AWS configuration successfully loaded", extra={"color": "yellow"})
else:
    logThis.warning(
        "Incomplete AWS configuration - some services may not work properly"
    )

# === Application Constants ===
API_PREFIX = "/api/v1"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "avif", "bmp"}
GENERATED_IMAGE_EXTENSION = "webp"


DEFAULT_LIMIT = 4
IMAGES_PER_ROW = 4
TABLE_NAME = "fabric_table"

# === File Paths ===
IMAGE_BASE = get_asset_path()
COMPANY_LOGO = IMAGE_BASE.joinpath("company_logo.png")


# === S3 Configuration ===
S3_PATHS = {
    "bucket_name": AWS_CONFIG["bucket_name"],
    "database": f"s3://{AWS_CONFIG['bucket_name']}/table",
    "uploaded": "uploaded",
    "single": "uploaded/single/",
    "group": "uploaded/group/",
    "generated": "generated/",
    "search_uploads": "uploaded/search/",
    "root_folder": f"s3://{AWS_CONFIG['bucket_name']}/sample_table_images/",
    "card_uploads": "uploaded/card/",
}


# === Apply Environment Configuration ===
env_config = (
    setup_production_config(AWS_CONFIG, S3_PATHS)
    if ENVIRONMENT.lower() == "production"
    else setup_development_config(PROJECT_ROOT, IMAGE_BASE)
)

# === Extract Configuration Variables ===
STORAGE_OPTIONS = env_config["STORAGE_OPTIONS"]
# Uncomment for local table storage and comment the S3 path line
DATABASE_PATH = env_config["DATABASE_PATH"]
IMAGE_FOLDER = env_config["IMAGE_FOLDER"]
UPLOAD_FOLDER = env_config["UPLOAD_FOLDER"]
SINGLE_IMAGE_FOLDER = env_config["SINGLE_IMAGE_FOLDER"]
GROUP_IMAGE_FOLDER = env_config["GROUP_IMAGE_FOLDER"]
GENERATED_IMAGE_FOLDER = env_config["GENERATED_IMAGE_FOLDER"]
UPLOAD_FOLDER_FABRIC = env_config["UPLOAD_FOLDER_FABRIC"]
UPLOAD_FOLDER_CARD = env_config["UPLOAD_FOLDER_CARD"]

# Handle relative generated folder path for table update use only

RELATIVE_GENERATED_FOLDER = env_config["RELATIVE_GENERATED_FOLDER"]

SAMPLE_IMAGES_FOLDER = get_asset_path("sample")
CARD_SAMPLES = Path(SAMPLE_IMAGES_FOLDER, "cards")
# JSON file to store all results
RESULTS_FILE = Path(PROJECT_ROOT,"card_reader", "business_cards.json")
DEFAULT_IMAGES = {
    "Sample 1": SAMPLE_IMAGES_FOLDER.joinpath("fabric-1.webp"),
    "Sample 2": SAMPLE_IMAGES_FOLDER.joinpath("fabric-2.webp"),
    "Sample 3": SAMPLE_IMAGES_FOLDER.joinpath("fabric-4.webp"),
    "Sample 4": SAMPLE_IMAGES_FOLDER.joinpath("fabric-5.webp"),
}

# === Final Validation ===
_ = validate_configuration(ENVIRONMENT, DATABASE_PATH, IMAGE_FOLDER, AWS_CONFIG)
