"""
===============================================================================
N205EN GAMI MIXTURE SWEEP ANALYSIS SCRIPT
===============================================================================
This script queries the authoritative Parquet database (n205en_engine_telemetry.parquet)
to analyze GAMI mixture sweeps, detect cruise altitude plateaus, compute peak EGT
fuel flows for all 6 cylinders, determine cylinder peak order, and calculate
overall GAMI spread.

Usage:
  python3 scripts/analyze_gami_sweeps.py
  python3 scripts/analyze_gami_sweeps.py --date 2026-08-09
===============================================================================
"""

import sys
import argparse
import importlib.util
from pathlib import Path
import pandas as pd
import numpy as np

# Load config module
config_path = Path(__file__).parent.resolve() / "config.py"
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

FLIGHT_TELEMETRY_PARQUET = config.FLIGHT_TELEMETRY_PARQUET
METADATA_PARQUET = config.METADATA_PARQUET

def analyze_gami_sweeps(target_date_str=None):
    print("=" * 80)
    print("N205EN GAMI MIXTURE SWEEP TELEMETRY ANALYSIS")
    print("=" * 80)
    print(f"Authoritative Parquet Source: {FLIGHT_TELEMETRY_PARQUET}")

    if not FLIGHT_TELEMETRY_PARQUET.exists():
        print(f"Error: Parquet file not found at {FLIGHT_TELEMETRY_PARQUET}")
        sys.exit(1)

    print("Loading telemetry database...")
    df = pd.read_parquet(FLIGHT_TELEMETRY_PARQUET)
    
    # Standardize column names
    col_map = {c: c.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("&", "and") for c in df.columns}
    df = df.rename(columns=col_map)
    
    time_col = 'gps_date_and_time' if 'gps_date_and_time' in df.columns else 'timestamp'
    df['dt'] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=['dt']).sort_values('dt').reset_index(drop=True)

    # Determine target flight date
    if target_date_str is None:
        target_date = df['dt'].dt.date.max()
        print(f"No date specified. Analyzing latest flight in database: {target_date}")
    else:
        target_date = pd.to_datetime(target_date_str).date()
        print(f"Target Flight Date: {target_date}")

    df_flight = df[df['dt'].dt.date == target_date].copy()
    if len(df_flight) == 0:
        print(f"No telemetry records found for date {target_date}.")
        sys.exit(1)

    print(f"Loaded {len(df_flight):,} rows for {target_date}.")
    print(f"Time Range: {df_flight['dt'].min().strftime('%H:%M:%S')} - {df_flight['dt'].max().strftime('%H:%M:%S')} UTC")

    # Clean numerical columns
    ff_col = 'fuel_flow_1_gal_hr' if 'fuel_flow_1_gal_hr' in df_flight.columns else [c for c in df_flight.columns if 'fuel_flow' in c][0]
    alt_col = 'pressure_altitude_ft' if 'pressure_altitude_ft' in df_flight.columns else [c for c in df_flight.columns if 'altitude' in c][0]
    
    cols_to_num = [ff_col, alt_col] + [f'egt_{i}_deg_c' for i in range(1, 7)] + [f'cht_{i}_deg_c' for i in range(1, 7)]
    for c in cols_to_num:
        if c in df_flight.columns:
            df_flight[c] = pd.to_numeric(df_flight[c], errors='coerce')

    # Identify cruise plateaus (alt > 5000 ft)
    df_cruise = df_flight[df_flight[alt_col] > 5000].copy()
    df_cruise['alt_bin'] = (df_cruise[alt_col] / 500).round() * 500

    plateaus = df_cruise.groupby('alt_bin')['dt'].agg(['min', 'max', 'count']).reset_index()
    plateaus = plateaus[plateaus['count'] >= 300].sort_values('min') # At least ~1.25 minutes at 4Hz

    if len(plateaus) == 0:
        print("No sustained cruise plateaus found above 5,000 ft MSL.")
        sys.exit(0)

    print("\n" + "=" * 80)
    print("DETECTED CRUISE ALTITUDE BLOCKS & GAMI SWEEP RESULTS")
    print("=" * 80)

    summary_rows = []

    for idx, p in plateaus.iterrows():
        alt_lvl = p['alt_bin']
        t_start = p['min']
        t_end = p['max']
        
        sub = df_flight[(df_flight['dt'] >= t_start) & (df_flight['dt'] <= t_end)].copy()
        
        # Filter for active fuel flow range (8.5 - 13.5 GPH)
        sub_sweep = sub[(sub[ff_col] >= 8.5) & (sub[ff_col] <= 13.5)].copy()
        if len(sub_sweep) < 20:
            continue

        # Find empirical peak per cylinder (0.1 GPH binning for robustness)
        sub_sweep['ff_bin'] = sub_sweep[ff_col].round(1)
        bins = sub_sweep.groupby('ff_bin')[[f'egt_{i}_deg_c' for i in range(1, 7)]].mean()

        peaks = {}
        for cyl in range(1, 7):
            c_col = f'egt_{cyl}_deg_c'
            if c_col in bins.columns and not bins[c_col].isna().all():
                peak_ff = bins[c_col].idxmax()
                peak_egt = bins[c_col].max()
                peaks[cyl] = (peak_ff, peak_egt)

        if len(peaks) < 6:
            continue

        sorted_peaks = sorted(peaks.items(), key=lambda x: x[1][0], reverse=True)
        richest_cyl, (richest_ff, richest_egt) = sorted_peaks[0]
        leanest_cyl, (leanest_ff, leanest_egt) = sorted_peaks[-1]
        gami_spread = richest_ff - leanest_ff

        print(f"\n📍 Altitude Block: {alt_lvl:,.0f} FT MSL ({t_start.strftime('%H:%M:%S')} - {t_end.strftime('%H:%M:%S')} UTC)")
        print(f"   Fuel Flow Range: {sub[ff_col].min():.1f} -> {sub[ff_col].max():.1f} GPH")
        print(f"   Peak Order (Richest to Leanest):")
        for rank, (cyl, (p_ff, p_egt)) in enumerate(sorted_peaks, 1):
            print(f"     {rank}. Cylinder {cyl}: Peak at {p_ff:.2f} GPH (EGT {p_egt:.1f}°C)")
        print(f"   ==> GAMI SPREAD: {gami_spread:.2f} GPH (Richest Cyl {richest_cyl} @ {richest_ff:.2f} GPH | Leanest Cyl {leanest_cyl} @ {leanest_ff:.2f} GPH)")

        summary_rows.append({
            'Altitude_ft': alt_lvl,
            'Richest_Cyl': f"Cyl {richest_cyl} ({richest_ff:.2f} GPH)",
            'Leanest_Cyl': f"Cyl {leanest_cyl} ({leanest_ff:.2f} GPH)",
            'GAMI_Spread_GPH': round(gami_spread, 2)
        })

    if summary_rows:
        print("\n" + "=" * 80)
        print("SUMMARY TABLE ACROSS TEST ALTITUDES")
        print("=" * 80)
        df_sum = pd.DataFrame(summary_rows)
        print(df_sum.to_string(index=False))

        avg_spread = df_sum['GAMI_Spread_GPH'].mean()
        print("-" * 80)
        print(f"Average GAMI Spread Across Altitude Runs: {avg_spread:.2f} GPH")
        if avg_spread < 0.3:
            print("Status: 🟢 TARGET ACHIEVED (< 0.3 GPH Spread)")
        else:
            print("Status: 🔴 TUNING REQUIRED (Target < 0.3 GPH Spread)")
        print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="N205EN GAMI Mixture Sweep Analysis")
    parser.add_argument("--date", type=str, help="Target flight date (YYYY-MM-DD)")
    args = parser.parse_args()
    analyze_gami_sweeps(args.date)
