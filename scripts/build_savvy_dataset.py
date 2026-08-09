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
import importlib.util
from pathlib import Path

# Load config module directly relative to script location
config_path = Path(__file__).parent.resolve() / "config.py"
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

DATA_DIR = config.DATA_DIR
RAW_CSV_DIR = config.RAW_CSV_DIR
METADATA_PARQUET = config.METADATA_PARQUET
FLIGHT_TELEMETRY_PARQUET = config.FLIGHT_TELEMETRY_PARQUET
GROUND_TELEMETRY_PARQUET = config.GROUND_TELEMETRY_PARQUET
SESSION_FILE = config.SESSION_FILE
SAVVY_BASE_URL = config.SAVVY_BASE_URL

AIRCRAFT_FLIGHTS_URL = f"{SAVVY_BASE_URL}/flights/aircraft/26886"

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

    print("\nPhase 4: Telemetry Harmonization & Parquet Generation...")
    csv_files = list(RAW_CSV_DIR.glob("*.csv"))
    print(f"Total raw CSV log files in repository: {len(csv_files)}")

    if not csv_files:
        print("No CSV files found in raw directory. Pipeline stopping.")
        return

    print("Loading and parsing raw CSV files into DataFrames...")
    all_dfs = []
    for csv_p in tqdm(csv_files, desc="Parsing CSVs"):
        try:
            pdf = pd.read_csv(csv_p, low_memory=False, on_bad_lines="skip")
            pdf.columns = [col.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for col in pdf.columns]
            pdf = pdf.loc[:, ~pdf.columns.duplicated()]
            pdf["source_file"] = csv_p.name
            all_dfs.append(pdf)
        except Exception as err:
            print(f"Warning: Failed to parse {csv_p.name}: {err}")

    if not all_dfs:
        print("Error: Could not load any telemetry DataFrames.")
        return

    print("Concatenating all telemetry DataFrames...")
    full_df = pd.concat(all_dfs, ignore_index=True)
    full_df = full_df.loc[:, ~full_df.columns.duplicated()]
    
    print(f"\nTotal raw telemetry points loaded: {len(full_df):,} rows, {len(full_df.columns)} columns.")

    print("Harmonizing and coercing column dtypes for PyArrow export...")
    str_cols = ["source_file", "gps_date_&_time", "system_time", "destination_waypoint_id", "cdi_source_type", "cdi_source_port", "ap_roll_mode", "transponder_status", "egt_leaning_state"]
    for col in tqdm(full_df.columns, desc="Coercing dtypes"):
        if col not in str_cols:
            num_col = pd.to_numeric(full_df[col], errors="coerce")
            if num_col.notna().sum() > 0:
                full_df[col] = num_col
            else:
                full_df[col] = full_df[col].astype(str)
        else:
            full_df[col] = full_df[col].astype(str)

    # Determine flight vs ground split
    ias_col = "indicated_airspeed_knots" if "indicated_airspeed_knots" in full_df.columns else None
    rpm_col = "rpm_l" if "rpm_l" in full_df.columns else ("rpm" if "rpm" in full_df.columns else None)

    if ias_col and rpm_col:
        is_flight_condition = (full_df[ias_col] > 30) & (full_df[rpm_col] > 1000)
    elif ias_col:
        is_flight_condition = full_df[ias_col] > 30
    else:
        is_flight_condition = full_df.index > -1

    flight_telemetry = full_df[is_flight_condition].copy()
    ground_telemetry = full_df[~is_flight_condition].copy()

    print(f"\nWriting Flight Telemetry Parquet: {len(flight_telemetry):,} rows...")
    if FLIGHT_TELEMETRY_PARQUET.exists():
        try:
            FLIGHT_TELEMETRY_PARQUET.unlink()
        except Exception:
            pass
    flight_telemetry.to_parquet(FLIGHT_TELEMETRY_PARQUET, engine="pyarrow", compression="zstd")

    print(f"Writing Ground/Maintenance Parquet: {len(ground_telemetry):,} rows...")
    if GROUND_TELEMETRY_PARQUET.exists():
        try:
            GROUND_TELEMETRY_PARQUET.unlink()
        except Exception:
            pass
    ground_telemetry.to_parquet(GROUND_TELEMETRY_PARQUET, engine="pyarrow", compression="zstd")

    catalog_count_str = f"{len(flights_catalog)} flights" if 'flights_catalog' in locals() and flights_catalog else ("Catalog existing" if METADATA_PARQUET.exists() else "N/A")

    print("\n" + "=" * 80)
    print("SUCCESS! Pipeline Execution Complete.")
    print(f"1. Master Catalog: {METADATA_PARQUET.name} ({METADATA_PARQUET.stat().st_size / 1024:.1f} KB, {catalog_count_str})")
    print(f"2. Flight Telemetry: {FLIGHT_TELEMETRY_PARQUET.name} ({FLIGHT_TELEMETRY_PARQUET.stat().st_size / (1024*1024):.2f} MB)")
    print(f"3. Ground Telemetry: {GROUND_TELEMETRY_PARQUET.name} ({GROUND_TELEMETRY_PARQUET.stat().st_size / (1024*1024):.2f} MB)")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
