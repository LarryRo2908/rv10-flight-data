import os
from pathlib import Path

# Base directories (BASE_DIR is scripts/ folder)
BASE_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
RAW_CSV_DIR = DATA_DIR / "raw_csvs"
PARQUET_DIR = DATA_DIR / "parquet"
TEMP_DIR = PROJECT_DIR / "temp"

# Output Parquet Files
METADATA_PARQUET = PARQUET_DIR / "flights_metadata.parquet"
FLIGHT_TELEMETRY_PARQUET = PARQUET_DIR / "n205en_engine_telemetry.parquet"
GROUND_TELEMETRY_PARQUET = PARQUET_DIR / "n205en_ground_maintenance.parquet"

# Auth Session Storage
SESSION_FILE = DATA_DIR / "savvy_session.json"

# Create directories if they do not exist
DATA_DIR.mkdir(exist_ok=True)
RAW_CSV_DIR.mkdir(exist_ok=True)
PARQUET_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

SAVVY_BASE_URL = "https://apps.savvyaviation.com"
SAVVY_FLIGHTS_URL = f"{SAVVY_BASE_URL}/flights"

