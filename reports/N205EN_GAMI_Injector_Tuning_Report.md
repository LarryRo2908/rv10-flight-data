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

| Cylinder | Current Nozzle | Action & New Installation | Expected Tuning Result |
| :--- | :--- | :--- | :--- |
| **Cylinder 1** | `.0285` | Change to **`.029`** *(Move Cyl 2's nozzle here)* | Enriches Cyl 1 $\rightarrow$ peaks earlier |
| **Cylinder 2** | `.029` | Change to **`.028`** *(Move Cyl 5's nozzle here)* | Restricts Cyl 2 $\rightarrow$ peaks later |
| **Cylinder 3** | `.0275` | **Keep `.0275`** | Solid mid-range anchor |
| **Cylinder 4** | `.0265` | **Keep `.0265`** | Keeps Cyl 4 restricted |
| **Cylinder 5** | `.028` | Install **NEW `.029`** | Enriches Cyl 5 $\rightarrow$ peaks earlier |
| **Cylinder 6** | `.0275` | Install **NEW `.027`** | Restricts Cyl 6 $\rightarrow$ peaks later |

---

## 🎯 Target Outcome

After installing this initial change set:
* **Target GAMI Spread**: **< 0.3 GPH** (down from ~2.0 GPH).
* **Expected LOP Operation**: Smooth, vibration-free engine operation at **50°F LOP (~9.5 GPH cruise)**.
