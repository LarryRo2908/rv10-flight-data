import os
from pathlib import Path

# Base directories (BASE_DIR is scripts/ folder)
BASE_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
RAW_CSV_DIR = DATA_DIR / "raw_csvs"
PARQUET_DIR = DATA_DIR / "parquet"
TEMP_DIR = PROJECT_DIR / "temp"
NEW_FLIGHT_LOG_DIR = PROJECT_DIR / "New_Flight_Log"

PARQUET_BACKUP_DIR = PARQUET_DIR / "backups"

# Output Parquet Files
METADATA_PARQUET = PARQUET_DIR / "flights_metadata.parquet"
FLIGHT_TELEMETRY_PARQUET = PARQUET_DIR / "n205en_engine_telemetry.parquet"
GROUND_TELEMETRY_PARQUET = PARQUET_DIR / "n205en_ground_maintenance.parquet"

# Auth Session Storage
SESSION_FILE = DATA_DIR / "savvy_session.json"

# Create directories if they do not exist
for d in [DATA_DIR, RAW_CSV_DIR, PARQUET_DIR, TEMP_DIR, NEW_FLIGHT_LOG_DIR, PARQUET_BACKUP_DIR]:
    try:
        d.mkdir(exist_ok=True)
    except Exception:
        pass

SAVVY_BASE_URL = "https://apps.savvyaviation.com"
SAVVY_FLIGHTS_URL = f"{SAVVY_BASE_URL}/flights"

