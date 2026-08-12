"""
===============================================================================
SAVVY AVIATION AUTOMATED DATA EXTRACTION & PARQUET CONVERSION PIPELINE
===============================================================================
This script automates:
1. Playwright session authentication to Savvy Aviation.
2. Scraping all flight records & metadata (dates, airports, flight bounds)
   1:1 from Savvy Aviation's MUI DataGrid.
3. Bulk downloading and deduplicating raw Dynon engine CSV logs.
4. Harmonizing telemetry column schemas across both Dynon screens.
5. Exporting 3 clean Parquet datasets:
   - data/flights_metadata.parquet (Savvy Flight Catalog)
   - data/n205en_engine_telemetry.parquet (Savvy-aligned Active Flights)
   - data/n205en_ground_maintenance.parquet (100% Preserved Ground/Maintenance)
===============================================================================
"""

import sys
import os
import time
import re
import json
import shutil
import importlib.util
from pathlib import Path

# Load config module directly relative to script location
config_path = Path(__file__).parent.resolve() / "config.py"
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

PROJECT_DIR = config.PROJECT_DIR
DATA_DIR = config.DATA_DIR
RAW_CSV_DIR = config.RAW_CSV_DIR
NEW_FLIGHT_LOG_DIR = config.NEW_FLIGHT_LOG_DIR
PARQUET_BACKUP_DIR = config.PARQUET_BACKUP_DIR
METADATA_PARQUET = config.METADATA_PARQUET
FLIGHT_TELEMETRY_PARQUET = config.FLIGHT_TELEMETRY_PARQUET
GROUND_TELEMETRY_PARQUET = config.GROUND_TELEMETRY_PARQUET
SESSION_FILE = config.SESSION_FILE
SAVVY_BASE_URL = config.SAVVY_BASE_URL

def safe_write_parquet(df, target_path, label, max_backups=5):
    ts = time.strftime("%Y%m%d_%H%M%S")
    PARQUET_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = PARQUET_BACKUP_DIR / f"{target_path.stem}_{ts}.parquet"
    
    print(f"\nWriting {label}: {len(df):,} total rows...")
    
    # 1. Create a timestamped archive copy of existing file before updating
    if target_path.exists():
        try:
            shutil.copy2(str(target_path), str(archive_path))
            print(f"Created rolling backup: {archive_path.name}")
        except Exception as err:
            print(f"Warning: Failed to create archive backup: {err}")
        
    # 2. Write directly to target parquet file
    df.to_parquet(target_path, engine="pyarrow", compression="zstd")
    print(f"Successfully saved {label} ({target_path.stat().st_size / (1024*1024):.2f} MB).")

    # 3. Maintain rolling retention window (keep up to max_backups, prune oldest)
    try:
        existing_archives = sorted(
            list(PARQUET_BACKUP_DIR.glob(f"{target_path.stem}_*.parquet")),
            key=lambda p: p.stat().st_mtime
        )
        if len(existing_archives) > max_backups:
            for old_p in existing_archives[:-max_backups]:
                old_p.unlink()
                print(f"Pruned oldest rolling backup: {old_p.name}")
    except Exception as err:
        print(f"Warning: Backup pruning notice: {err}")

def run_pipeline():
    print("=" * 80)
    print("SAVVY AVIATION TELEMETRY PARQUET PIPELINE")
    print("=" * 80)
    print(f"Data Directory: {DATA_DIR}")
    print(f"Raw CSV Directory: {RAW_CSV_DIR}")
    print("=" * 80)

    import pandas as pd
    try:
        from tqdm import tqdm
    except ImportError:
        def tqdm(iterable, **kwargs):
            return iterable

    has_playwright = False
    try:
        from playwright.sync_api import sync_playwright
        has_playwright = True
    except ImportError:
        print("Note: playwright is not installed. Automated browser scraper will be skipped.")

    if has_playwright:
        print("\nPhase 1: Authenticating & Launching Scraper...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                
                context_kwargs = {}
                if SESSION_FILE.exists():
                    print(f"Loading session from {SESSION_FILE.name}...")
                    context_kwargs["storage_state"] = str(SESSION_FILE)
                    
                context = browser.new_context(**context_kwargs)
                page = context.new_page()

                print(f"Navigating to {AIRCRAFT_FLIGHTS_URL}...")
                page.goto(AIRCRAFT_FLIGHTS_URL)
                page.wait_for_timeout(3000)

                # Check if redirected to login page
                if "login" in page.url:
                    print("\n" + "!" * 80)
                    print("Action Required: Session expired or missing. Please log into Savvy Aviation.")
                    print("!" * 80 + "\n")
                    browser.close()
                    browser = p.chromium.launch(headless=False)
                    context = browser.new_context()
                    page = context.new_page()
                    page.goto(f"{SAVVY_BASE_URL}/login")
                    page.wait_for_url("**/flights**", timeout=300000)
                    print("Login detected! Saving session state...")
                    context.storage_state(path=str(SESSION_FILE))
                    page.goto(AIRCRAFT_FLIGHTS_URL)
                    page.wait_for_timeout(3000)

                print("\nPhase 2: Scraping Flight Catalog & Extracting Metadata...")
                page.wait_for_selector(".MuiDataGrid-row", timeout=15000)

                flights_catalog = []
                page_num = 1

                while True:
                    pag_label = page.query_selector(".MuiTablePagination-displayedRows")
                    label_text = pag_label.inner_text() if pag_label else ""

                    rows = page.query_selector_all(".MuiDataGrid-row")
                    for r in rows:
                        cells = r.query_selector_all(".MuiDataGrid-cell")
                        if len(cells) < 7:
                            continue
                        
                        f_date = cells[1].inner_text().strip()
                        f_time = cells[2].inner_text().strip()
                        dep_apt = cells[3].inner_text().strip()
                        arr_apt = cells[4].inner_text().strip()
                        csv_filename = cells[5].inner_text().strip()
                        duration_str = cells[6].inner_text().strip()
                        r_id = r.get_attribute("data-id")

                        flights_catalog.append({
                            "savvy_flight_id": r_id,
                            "flight_date": f_date,
                            "utc_time": f_time,
                            "departure_airport": dep_apt,
                            "destination_airport": arr_apt,
                            "source_csv_filename": csv_filename,
                            "duration_str": duration_str
                        })

                    next_btn = page.query_selector('button[title="Go to next page"], button[aria-label="Go to next page"]')
                    if next_btn and next_btn.is_enabled() and next_btn.is_visible():
                        next_btn.click()
                        page.wait_for_timeout(1200)
                        page.wait_for_selector(".MuiDataGrid-row", timeout=10000)
                        page_num += 1
                    else:
                        break

                print(f"Total flight records extracted from Savvy catalog: {len(flights_catalog)}")

                # Save metadata catalog
                catalog_df = pd.DataFrame(flights_catalog)
                catalog_df.to_parquet(METADATA_PARQUET, engine="pyarrow")
                print(f"Saved {METADATA_PARQUET.name} ({len(catalog_df)} flight catalog entries)")

                print("\nPhase 3: Checking Unique Raw CSV Downloads...")
                downloaded_files = set(f.name for f in RAW_CSV_DIR.glob("*.csv"))
                print(f"Already downloaded CSV files: {len(downloaded_files)}")

                unique_csvs_to_fetch = set(f["source_csv_filename"] for f in flights_catalog if f["source_csv_filename"])
                print(f"Total unique CSV files referenced across catalog: {len(unique_csvs_to_fetch)}")

                csv_to_flight_id = {}
                for f in flights_catalog:
                    fname = f["source_csv_filename"]
                    fid = f["savvy_flight_id"]
                    if fname and fid and fname not in csv_to_flight_id:
                        csv_to_flight_id[fname] = fid

                needed_csvs = [fn for fn in unique_csvs_to_fetch if fn not in downloaded_files]
                if needed_csvs:
                    print(f"Downloading {len(needed_csvs)} remaining CSV files...")
                    for fname in tqdm(needed_csvs, desc="Downloading CSVs"):
                        fid = csv_to_flight_id.get(fname)
                        if not fid:
                            continue

                        flight_detail_url = f"{SAVVY_BASE_URL}/flights/{fid}"
                        page.goto(flight_detail_url)
                        page.wait_for_timeout(1500)

                        csv_link = page.query_selector('a:has-text(".csv")')
                        if csv_link:
                            try:
                                with page.expect_download(timeout=30000) as download_info:
                                    csv_link.click()
                                download = download_info.value
                                save_path = RAW_CSV_DIR / download.suggested_filename
                                download.save_as(str(save_path))
                                downloaded_files.add(fname)
                                time.sleep(0.3)
                            except Exception as err:
                                print(f"Warning: Failed downloading {fname}: {err}")
                else:
                    print("All raw CSV log files are present locally!")

                context.storage_state(path=str(SESSION_FILE))
                browser.close()
        except Exception as scraper_err:
            print(f"Scraper encountered error or required user browser: {scraper_err}")
            print("Proceeding to process local CSV telemetry files...")
    else:
        print("Skipping Playwright scraping. Proceeding to process local CSV telemetry files...")

    print("\nPhase 4: Incremental Telemetry Ingestion & Parquet Generation...")
    
    # 1. Scan drop directory and raw CSV directory
    drop_csv_files = list(NEW_FLIGHT_LOG_DIR.glob("*.csv"))
    raw_csv_files = list(RAW_CSV_DIR.glob("*.csv"))
    
    if drop_csv_files:
        print(f"Found {len(drop_csv_files)} new flight log CSV file(s) in {NEW_FLIGHT_LOG_DIR.name}/ drop directory:")
        for f in drop_csv_files:
            print(f" - {f.name}")
            
    # Check existing ingested source files from Parquet databases (only if BOTH exist)
    existing_ingested_sources = set()
    if FLIGHT_TELEMETRY_PARQUET.exists() and GROUND_TELEMETRY_PARQUET.exists():
        try:
            flight_sources = set(pd.read_parquet(FLIGHT_TELEMETRY_PARQUET, columns=["source_file"])["source_file"].unique())
            ground_sources = set(pd.read_parquet(GROUND_TELEMETRY_PARQUET, columns=["source_file"])["source_file"].unique())
            existing_ingested_sources = flight_sources.intersection(ground_sources)
        except Exception:
            existing_ingested_sources = set()

    print(f"Already ingested CSV source files in database: {len(existing_ingested_sources)}")

    # Determine candidate files to parse
    all_available_csvs = drop_csv_files + [f for f in raw_csv_files if f.name not in set(c.name for c in drop_csv_files)]
    csv_files_to_parse = [f for f in all_available_csvs if f.name not in existing_ingested_sources]

    if not csv_files_to_parse:
        print("No new raw CSV log files to process. Database is up to date!")
        # Relocate any drop files that were already in database
        for f in drop_csv_files:
            target_p = RAW_CSV_DIR / f.name
            if f.resolve() != target_p.resolve():
                shutil.move(str(f), str(target_p))
                print(f"Moved {f.name} -> {RAW_CSV_DIR.relative_to(PROJECT_DIR)}/")
    else:
        print(f"Parsing {len(csv_files_to_parse)} new raw CSV file(s) into database...")
        new_dfs = []
        for csv_p in tqdm(csv_files_to_parse, desc="Parsing new CSVs"):
            try:
                pdf = pd.read_csv(csv_p, low_memory=False, on_bad_lines="skip")
                pdf.columns = [col.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for col in pdf.columns]
                pdf = pdf.loc[:, ~pdf.columns.duplicated()]
                pdf["source_file"] = csv_p.name
                new_dfs.append(pdf)
            except Exception as err:
                print(f"Warning: Failed to parse {csv_p.name}: {err}")

        if new_dfs:
            new_full_df = pd.concat(new_dfs, ignore_index=True)
            new_full_df = new_full_df.loc[:, ~new_full_df.columns.duplicated()]

            # Harmonize column dtypes
            str_cols = ["source_file", "gps_date_&_time", "system_time", "destination_waypoint_id", "cdi_source_type", "cdi_source_port", "ap_roll_mode", "transponder_status", "egt_leaning_state"]
            for col in tqdm(new_full_df.columns, desc="Coercing dtypes"):
                if col not in str_cols:
                    new_full_df[col] = pd.to_numeric(new_full_df[col], errors="coerce")
                else:
                    new_full_df[col] = new_full_df[col].astype(str)

            # Determine flight vs ground split
            ias_col = "indicated_airspeed_knots" if "indicated_airspeed_knots" in new_full_df.columns else None
            rpm_col = "rpm_l" if "rpm_l" in new_full_df.columns else ("rpm" if "rpm" in new_full_df.columns else None)

            if ias_col and rpm_col:
                is_flight_condition = (new_full_df[ias_col] > 30) & (new_full_df[rpm_col] > 1000)
            elif ias_col:
                is_flight_condition = new_full_df[ias_col] > 30
            else:
                is_flight_condition = new_full_df.index > -1

            new_flight_telemetry = new_full_df[is_flight_condition].copy()
            new_ground_telemetry = new_full_df[~is_flight_condition].copy()

            # Merge with existing Parquet files if available
            if FLIGHT_TELEMETRY_PARQUET.exists() and len(existing_ingested_sources) > 0:
                print("Merging new flight telemetry with existing dataset...")
                existing_flight = pd.read_parquet(FLIGHT_TELEMETRY_PARQUET)
                for c in existing_flight.columns:
                    if c in new_flight_telemetry.columns and existing_flight[c].dtype != new_flight_telemetry[c].dtype:
                        try:
                            new_flight_telemetry[c] = new_flight_telemetry[c].astype(existing_flight[c].dtype)
                        except Exception:
                            pass
                flight_telemetry = pd.concat([existing_flight, new_flight_telemetry], ignore_index=True)
            else:
                flight_telemetry = new_flight_telemetry

            if GROUND_TELEMETRY_PARQUET.exists() and len(existing_ingested_sources) > 0:
                print("Merging new ground telemetry with existing dataset...")
                existing_ground = pd.read_parquet(GROUND_TELEMETRY_PARQUET)
                for c in existing_ground.columns:
                    if c in new_ground_telemetry.columns and existing_ground[c].dtype != new_ground_telemetry[c].dtype:
                        try:
                            new_ground_telemetry[c] = new_ground_telemetry[c].astype(existing_ground[c].dtype)
                        except Exception:
                            pass
                ground_telemetry = pd.concat([existing_ground, new_ground_telemetry], ignore_index=True)
            else:
                ground_telemetry = new_ground_telemetry

            safe_write_parquet(flight_telemetry, FLIGHT_TELEMETRY_PARQUET, "Flight Telemetry Parquet")
            safe_write_parquet(ground_telemetry, GROUND_TELEMETRY_PARQUET, "Ground/Maintenance Parquet")

            # Move processed CSV files from New_Flight_Log drop folder to data/raw_csvs
            for f in drop_csv_files:
                target_p = RAW_CSV_DIR / f.name
                shutil.move(str(f), str(target_p))
                print(f"Moved processed CSV: {f.name} -> {RAW_CSV_DIR.relative_to(PROJECT_DIR)}/")

    catalog_count_str = f"{len(flights_catalog)} flights" if 'flights_catalog' in locals() and flights_catalog else ("Catalog existing" if METADATA_PARQUET.exists() else "N/A")
    flight_stat_str = f"{FLIGHT_TELEMETRY_PARQUET.stat().st_size / (1024*1024):.2f} MB" if FLIGHT_TELEMETRY_PARQUET.exists() else "Missing"
    ground_stat_str = f"{GROUND_TELEMETRY_PARQUET.stat().st_size / (1024*1024):.2f} MB" if GROUND_TELEMETRY_PARQUET.exists() else "Missing"

    print("\n" + "=" * 80)
    print("SUCCESS! Pipeline Execution Complete.")
    print(f"1. Master Catalog: {METADATA_PARQUET.name} ({METADATA_PARQUET.stat().st_size / 1024:.1f} KB, {catalog_count_str})")
    print(f"2. Flight Telemetry: {FLIGHT_TELEMETRY_PARQUET.name} ({flight_stat_str})")
    print(f"3. Ground Telemetry: {GROUND_TELEMETRY_PARQUET.name} ({ground_stat_str})")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
