# Engineering Report: N205EN Fuel Injector Tuning & GAMI Spread Optimization

**Aircraft**: Van's RV-10 (**N205EN**)  
**Engine**: Lycoming IO-540 with Air Flow Performance (AFP) Fuel Injection System  
**Analysis Period**: Phase 2 Dataset (November 5, 2021 – Present, 143 Flights, 4.27M In-Flight Telemetry Rows)  

---

## 🎯 Executive Summary

Analysis of **143 historical cross-country flights** confirms that N205EN's current engine roughness at 50°F Lean-Of-Peak (LOP) is caused by a **systemic GAMI spread of ~1.7 to 2.0 GPH**. 

* **The Cause**: **Cylinders 4 & 6** systematically peak **first** (at high fuel flows ~11.5–11.8 GPH), while **Cylinders 1 & 5** systematically peak **last** (at low fuel flows ~9.7–10.2 GPH).
* **The Solution**: Installing a targeted set of Air Flow Performance (AFP) restrictors will re-balance fuel distribution across the cylinders, collapsing the GAMI spread down to **< 0.3 GPH** and enabling glass-smooth LOP operation.

---

## 📊 Current Injector Baseline & Peak Sequence

### Current Installed Nozzle Sizes
* **Cylinder 1**: `.0285`
* **Cylinder 2**: `.0290`
* **Cylinder 3**: `.0275`
* **Cylinder 4**: `.0265`
* **Cylinder 5**: `.0280`
* **Cylinder 6**: `.0275`

### 143-Flight Statistical Peak Order & Fuel Flow
Across 143 Phase 2 flights, the cylinder peak order is 100% consistent (no mechanical degradation drift):

| Peak Order | Cylinder | Installed Nozzle | Median Peak Fuel Flow | Systemic State during Cruise Leaning |
| :--- | :--- | :--- | :--- | :--- |
| **1st to Peak** | **Cylinder 6** | `.0275` | **11.80 GPH** | 🔴 Too Rich (Peaking way too early) |
| **2nd to Peak** | **Cylinder 4** | `.0265` | **11.50 GPH** | 🔴 Too Rich (Peaking way too early) |
| **3rd to Peak** | **Cylinder 2** | `.0290` | **10.90 GPH** | 🟡 Mid-Range |
| **4th to Peak** | **Cylinder 3** | `.0275` | **10.60 GPH** | 🟡 Mid-Range |
| **5th to Peak** | **Cylinder 5** | `.0280` | **10.20 GPH** | 🔵 **Too Lean (Peaking way too late)** |
| **6th to Peak** | **Cylinder 1** | `.0285` | **10.00 GPH** | 🔵 **Too Lean (Peaking way too late)** |

> **Root Cause of Roughness**: When leaning down to ~8.5 GPH, Cylinders 4 & 6 are deep LOP (-2.0 GPH past peak) while Cylinders 1 & 5 are just reaching peak. This power mismatch across the crankshaft causes the vibration.

---

## 🛒 Air Flow Performance (AFP) Purchase Plan

To cover the required tuning changes and maintain **spares on both the rich and lean ends** without paying multiple shipping fees:

| Quantity | Restrictor Size | Purpose |
| :--- | :--- | :--- |
| **1x** | **`.029`** | Primary enrichment for Cylinder 5 |
| **1x** | **`.027`** | Primary restriction step for Cylinder 6 |
| **1x** | **`.030`** | Spare enrichment for Cyl 1 or Cyl 5 |
| **1x** | **`.026`** | Spare restriction for Cyl 4 or Cyl 6 |
| **1x** | **`.0285`** | Spare mid-range restrictor |

* **Total Order**: **5 Restrictors** (~$190 total from Air Flow Performance).

---

## 🔧 Initial Change Set Installation Guide

Leveraging the new restrictors alongside re-using existing nozzles, install the following initial change set:

### Overview & Expected Tuning Impact

| Cylinder | Current Nozzle | Action & New Installation | Expected Tuning Result |
| :--- | :--- | :--- | :--- |
| **Cylinder 1** | `.0285` | Change to **`.029`** *(Move Cyl 2's nozzle here)* | Enriches Cyl 1 → peaks earlier |
| **Cylinder 2** | `.029` | Change to **`.028`** *(Move Cyl 5's nozzle here)* | Restricts Cyl 2 → peaks later |
| **Cylinder 3** | `.0275` | **Keep `.0275`** | Solid mid-range anchor |
| **Cylinder 4** | `.0265` | **Keep `.0265`** | Keeps Cyl 4 restricted |
| **Cylinder 5** | `.028` | Install **NEW `.029`** | Enriches Cyl 5 → peaks earlier |
| **Cylinder 6** | `.0275` | Install **NEW `.027`** | Restricts Cyl 6 → peaks later |

### 🛠️ Installation Work Sequence (Steps 1–4)

Perform moves and new nozzle additions in the following step-by-step physical sequence:

| Step | Target Cylinder | Action Required | Installed Nozzle | Nozzle Source / Origin |
| :--- | :--- | :--- | :--- | :--- |
| **Step 1** | **Cylinder 6** | Install New Restrictor | **`.027`** | **NEW** (Air Flow Performance order) |
| **Step 2** | **Cylinder 5** | Install New Restrictor | **`.029`** | **NEW** (Air Flow Performance order) |
| **Step 3** | **Cylinder 2** | Install Relocated Nozzle | **`.028`** | Removed from **Cylinder 5** |
| **Step 4** | **Cylinder 1** | Install Relocated Nozzle | **`.029`** | Removed from **Cylinder 2** |

> *Note: Cylinders 3 and 4 require no physical changes and remain at `.0275` and `.0265` respectively.*

### 📋 Final Installed Nozzle Configuration (Cylinders 1–6)

Final nozzle sizes across all 6 cylinders following completion of Steps 1–4:

| Cylinder | Final Nozzle Size | Baseline Size | Net Size Adjustment | Origin / Source |
| :--- | :--- | :--- | :--- | :--- |
| **Cylinder 1** | **`.0290`** | `.0285` | +`.0005` (Enriched) | Relocated from Cylinder 2 |
| **Cylinder 2** | **`.0280`** | `.0290` | -`.0010` (Restricted) | Relocated from Cylinder 5 |
| **Cylinder 3** | **`.0275`** | `.0275` | `0.0000` (Unchanged) | Retained Baseline |
| **Cylinder 4** | **`.0265`** | `.0265` | `0.0000` (Unchanged) | Retained Baseline |
| **Cylinder 5** | **`.0290`** | `.0280` | +`.0010` (Enriched) | NEW Restrictor |
| **Cylinder 6** | **`.0270`** | `.0275` | -`.0005` (Restricted) | NEW Restrictor |

---

## ✈️ Post-Installation Flight Test & Evaluation Protocol

### Procedure Overview
Savvy Aviation GAMI Mixture Sweep flight test protocol for N205EN across **3 VFR altitudes**: **7,500 ft**, **9,500 ft**, and **11,500 ft MSL**. All sweeps are performed at Wide Open Throttle (WOT) and 2350 RPM.

* **Sweep Rate**: 8 GPH delta over 90 seconds (1 GPH every 10 seconds).
* **Step Pauses**: 5 to 10 minutes between steps for thermal stabilization and pilot workload.

---

### Cockpit Flight Test Checklist

#### Pre-Flight Configuration
* Dynon SkyView engine data logging rate: **1 second (1 Hz)**

---

#### Step 1: Sweep 1 at 7,500 ft MSL
* **1.1** **Climb** **7,500** FT MSL
* **1.2** **Level**, **trim**, **WOT**, **2350** RPM
* **1.3** **14.0** GPH → **Pause** 5–10 min (stabilize CHTs)
* **1.4** **Lean** **8.0** GPH over 90 sec (1 GPH every 10 sec)
* **1.5** **Pause** **8.0** GPH
* **1.6** **Enrich** **8.0** **14.0** GPH over 90 sec (1 GPH every 10 sec)
* **1.7** **Pause** 5–10 min

---

#### Step 2: Sweep 2 at 9,500 ft MSL
* **2.1** **Climb** **9,500** FT MSL
* **2.2** **Level**, **trim**, **WOT**, **2350** RPM
* **2.3** **13.0** GPH → **Pause** 5–10 min (stabilize CHTs)
* **2.4** **Lean** **8.0** GPH over 90 sec (1 GPH every 10 sec)
* **2.5** **Pause** **8.0** GPH
* **2.6** **Enrich** **8.0** **13.0** GPH over 90 sec (1 GPH every 10 sec)
* **2.7** **Pause** 5–10 min

---

#### Step 3: Sweep 3 at 11,500 ft MSL
* **3.1** **Climb** **11,500** FT MSL
* **3.2** **Level**, **trim**, **WOT**, **2350** RPM
* **3.3** **12.0** GPH → **Pause** 5–10 min (stabilize CHTs)
* **3.4** **Lean** **8.0** GPH over 90 sec (1 GPH every 10 sec)
* **3.5** **Pause** **8.0** GPH
* **3.6** **Enrich** **8.0** **12.0** GPH over 90 sec (1 GPH every 10 sec)
* **3.7** **Pause** 5–10 min

---

#### Step 4: Post-Flight Data Analysis
* **4.1** Download Dynon engine log (or upload to Savvy Aviation)
* **4.2** Execute dataset pipeline: `python3 scripts/build_savvy_dataset.py`
* **4.3** Target GAMI Spread result: **< 0.3 GPH**

---

## 🎯 Target Outcome

After installing this initial change set:
* **Target GAMI Spread**: **< 0.3 GPH** (down from ~2.0 GPH).
* **Expected LOP Operation**: Smooth, vibration-free engine operation at **50°F LOP (~9.5 GPH cruise)**.

---

## 📅 Round 1 Test Flight Results & Tuning Iteration (August 9, 2026)

### 🛠️ Actual Installed Configuration (Round 1)
On August 9, 2026, the Round 1 restrictor modifications were installed with minor variations from the initial plan:
* **Cylinder 1**: Installed **`.0290`** *(relocated from Cyl 2)*
* **Cylinder 2**: Installed **`.0280`** *(relocated unmarked nozzle from Cyl 5, presumed `.0280`)*
* **Cylinder 3**: Retained **`.0275`** *(baseline)*
* **Cylinder 4**: Retained **`.0265`** *(baseline)*
* **Cylinder 5**: Installed **`.0290`** *(new restrictor)*
* **Cylinder 6**: Retained **`.0270`** *(installed restrictor)*

---

### ✈️ Flight Test Execution & Empirical Results
GAMI mixture sweep flight tests were conducted across **4 pressure altitudes** (10.5k, 11.5k, 12.5k, and 9.5k ft MSL) at WOT / 2350 RPM. Telemetry was logged by the Dynon SkyView EFIS and ingested into the Parquet database (`n205en_engine_telemetry.parquet`).

#### Empirical Peak Fuel Flows & Cylinder Order:
Across the 4 altitude runs, individual cylinder peak fuel flows shifted significantly compared to historical baseline:

| Cylinder | Round 1 Restrictor | Baseline Peak FF | Round 1 Peak FF | Shift / Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Cylinder 4** | `.0265` | 11.50 GPH | **10.70 – 11.10 GPH** | 🔴 **Rich Outlier** (Now 1st/2nd to peak) |
| **Cylinder 2** | `.0280` | 10.90 GPH | **10.60 – 11.30 GPH** | 🔴 **Rich Outlier** (Now 1st/2nd to peak) |
| **Cylinder 5** | `.0290` | 10.20 GPH | **10.40 – 10.60 GPH** | 🟢 Enriched off lean bottom (+0.3 GPH) |
| **Cylinder 3** | `.0275` | 10.60 GPH | **10.30 – 10.50 GPH** | 🟢 Mid-pack anchor |
| **Cylinder 1** | `.0290` | 10.00 GPH | **10.10 – 10.40 GPH** | 🟢 Enriched off lean bottom (+0.3 GPH) |
| **Cylinder 6** | `.0270` | 11.80 GPH | **9.60 – 10.40 GPH** | 🟢 Restricted from extreme rich (-1.5 GPH) |

#### Key Findings:
1. **Successful Compression of Outer Extremes**: Enriching Cylinders 1 & 5 to `.0290` and restricting Cylinder 6 to `.0270` successfully collapsed the old 2.0 GPH outer boundary.
2. **New Rich Outliers Identified**: Cylinders 2 (`.0280`) and 4 (`.0265`) are now left hanging out on the rich end (~10.7 – 11.3 GPH), leaving an overall residual GAMI spread of **~0.70 to 1.10 GPH** above the main 4-cylinder pack (~10.1 – 10.5 GPH).

---

### 🚀 Path Forward: Round 2 Restrictor Optimization Plan

To collapse Cylinders 2 and 4 into the ~10.30 GPH target cluster, execute Round 2 changes leveraging existing spare restrictor inventory (`.026`, `.027`, `.0285`, `.0285`, `.029`):

#### Proposed Round 2 Adjustments:
1. **Cylinder 4**: Restrict from `.0265` down to **`.0260`** *(using NEW `.026` from inventory)*.  
   * *Impact*: Shifts Cyl 4 peak down by ~0.50 GPH to **~10.30 GPH** (exact theoretical ideal).
2. **Cylinder 2**: Restrict from `.0280` down to **`.0270`** *(using NEW `.027` from inventory)*.  
   * *Impact*: Shifts Cyl 2 peak down by ~0.85 GPH to **~9.95 – 10.00 GPH** (or ideal `.0275` if ordered for ~10.35 GPH).

#### Final Target Configuration (Round 2):
* **Cyl 1**: `.0290` | **Cyl 2**: **`.0270`** *(or `.0275`)* | **Cyl 3**: `.0275` | **Cyl 4**: **`.0260`** | **Cyl 5**: `.0290` | **Cyl 6**: `.0270`

#### Target Outcome:
Collapse all 6 cylinders into the **10.0 – 10.4 GPH peak cluster**, yielding a final GAMI Spread **< 0.3 GPH**.
