# Project Context & Rules for N205EN Flight Data

## Conversation Start Protocol
At the beginning of any new conversation thread in this workspace:
1. Silently check Git status (`git status`).
2. If remote changes exist on GitHub, prompt the user: *"Remote updates detected on GitHub for Flight_Data. Would you like me to pull them now?"*

---

When analyzing flight data in this workspace, strictly follow the guidelines defined in [AIRCRAFT_PROFILE.md](reference/AIRCRAFT_PROFILE.md):


1. **Break-In Filtering**: Ignore data prior to **November 5, 2021** (engine break-in phase & pre-wheel-pants) when modeling current aircraft speed or fuel performance.
2. **Wheel Pants Step Change**: Performance from **November 5, 2021 onward** reflects the +12 to +15 knot speed increase from installed wheel pants (155–163 kt TAS in cruise).
3. **Flight Planning Standards**:
   - **Normal Cruise**: 155 kt TAS / 11.0 GPH (14.1 NM/gal)
   - **Economy Cruise**: 145 kt TAS / 10.0 GPH (14.5 NM/gal)
   - **Climb**: 130 kt TAS / 17.0 GPH @ 500 ft/min
   - **Usable Fuel**: 60.0 gallons (2 x 30 gal tanks L/R, 100LL, single-tank feed)
4. **Custom Tuned GAMI Injectors**:
   - Cyl 1: 0.0285" | Cyl 2: 0.0290" | Cyl 3: 0.0275" | Cyl 4: 0.0265" | Cyl 5: 0.0280" | Cyl 6: 0.0275"
5. **Savvy Cohort Benchmarks (Dated: July 26, 2026)**:
   - Cohort: **392 RV-10s / 81,862 flights**.
   - Altitude: Cohort Min 2,000 ft | Median 7,500 ft | Max 18,000 ft vs N205EN 5,190 ft MSL.
   - Speed: Cohort Min 120 KTAS | Median 158 KTAS | Max 223 KTAS vs N205EN 150–154 KTAS (163–166 KTAS > 10k ft).
   - Cruise CHT: Cohort Min 253°F | Median 372°F | Max 450°F vs N205EN (305°F–347°F) — cooler than 80% of cohort!
6. **Data & Repository Directory Layout**:
   - `scripts/`: Python dataset builders (`build_savvy_dataset.py`) and analysis scripts.
   - `reference/`: Permanent reference materials, `AIRCRAFT_PROFILE.md`, and `cockpit_cards/`.
   - `reports/`: Finished GAMI tuning, climb performance, and Savvy analysis reports.
   - `data/parquet/`: Master flight catalog and engine/ground telemetry Parquet datasets.
   - `data/raw_csvs/`: Raw EFIS / Savvy CSV flight logs.
   - `temp/`: Temporary task scratchpad directory for transient analysis files.
7. **Automated Pipeline Prompts**:
   - If user requests to update flights (e.g. *"I added a new flight into Savvy, update the parquet files"*), run `python3 scripts/build_savvy_dataset.py`.


