# Aircraft Profile & Operational History: N205EN

This document defines the core specification, operational history, and performance baselines for Van's RV-10 **N205EN**. AI agents inspecting or querying flight logs in this repository should reference these parameters to ensure contextually accurate analysis.

---

## 🛩️ Aircraft Identity & Specifications

* **Tail Number**: N205EN
* **Aircraft Model**: Van's RV-10 (4-Seat Homebuilt Aircraft)
* **Home Base**: Millville Executive Airport (**KMIV**) — Millville, New Jersey
* **Engine & Avionics**: Lycoming IO-540 with Dual Dynon SkyView EFIS / EMS Screens
* **Fuel System & Fuel Management**:
  - **Usable Fuel Capacity**: **60.0 Gallons Usable**
  - **Tanks**: 2 Independent Tanks (**30.0 Gallons Left Tank** / **30.0 Gallons Right Tank**)
  - **Selector**: Feeds from **one tank at a time** (manual tank switching management)
  - **Fuel Grade**: **100LL Aviation Gasoline**

### 🔧 Custom Tuned GAMI Fuel Injector Nozzles
Custom-tuned GAMIjectors installed during initial flight testing to balance cylinder-to-cylinder fuel flow and tighten GAMI spread:

| Cylinder | GAMI Nozzle Orifice Size | Relative Sizing Context |
| :--- | :--- | :--- |
| **Cylinder 1** | **0.0285"** *(Stamp 28.5)* | Standard mid-size |
| **Cylinder 2** | **0.0290"** *(Stamp 29.0)* | Largest nozzle (enrichment for Cyl 2) |
| **Cylinder 3** | **0.0275"** *(Stamp 27.5)* | Mid-lean nozzle |
| **Cylinder 4** | **0.0265"** *(Stamp 26.5)* | Smallest nozzle (balances hot Cyl 4) |
| **Cylinder 5** | **0.0280"** *(Stamp 28.0)* | Standard mid-size |
| **Cylinder 6** | **0.0275"** *(Stamp 27.5)* | Mid-lean nozzle |

---

## 🌐 Van's RV-10 Fleet Cohort Benchmark Database (Dated: July 26, 2026)

Master operational baseline extracted from Savvy Analysis reports covering **81,862 flights across 392 Van's RV-10 aircraft**. AI agents should use this table as the fleet benchmark when evaluating aircraft performance.

| Parameter | Min (0%) | 25th % | Fleet Median (50%) | 75th % | Max (100%) | Fleet Operational Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cruising Altitude (MSL)** | 2,000 ft | 5,470 ft | **7,500 ft** | 9,400 ft | 18,000 ft | Fleet cruises mostly between 5,500 ft and 9,500 ft MSL |
| **True Airspeed (TAS)** | 120 KTAS | 150 KTAS | **158 KTAS** | 164 KTAS | 223 KTAS | 50% of fleet cruises between 150 and 164 KTAS |
| **Percent Power (%PWR)** | 45.0% | 57.1% | **62.3%** | 67.8% | 89.8% | Fleet median power setting is 62.3% |
| **Fuel Efficiency (NM/Gal)** | 10.0 | 12.6 | **13.8** | 14.8 | 21.9 | 50% of fleet gets 12.6 to 14.8 NM/gal in cruise |
| **Max Cruise CHT (°F)** | 253°F | 353°F | **372°F** | 388°F | 450°F | Fleet median cruise CHT is 372°F (Redline 405°F+) |
| **Max Flight CHT (°F)** | 300°F | 370°F | **388°F** | 405°F | 450°F | Fleet max climb CHT median is 388°F |
| **Cruise CHT Spread (°F)** | 0.0°F | 24.0°F | **31.0°F – 34.0°F**| 38.0°F | 148.0°F | Fleet median cylinder CHT spread is 31°F – 34°F |
| **Oil Temp in Cruise (°F)** | 100°F | 176°F | **184°F** | 190°F | 234°F | Fleet median oil temp is 184°F |
| **Oil Press in Cruise (PSI)**| 10.1 psi | 70.7 psi | **74.3 psi** | 77.8 psi | 122.0 psi | Fleet median oil pressure is 74.3 psi |
| **Max Fuel Flow (Takeoff)** | 10.0 GPH | 23.1 GPH | **24.4 GPH** | 25.6 GPH | 45.0 GPH | Fleet median takeoff fuel flow is 24.4 GPH |
| **Max Engine RPM (Takeoff)** | 1,530 RPM | 2,640 RPM | **2,670 RPM** | 2,690 RPM | 3,490 RPM | Fleet median takeoff RPM is 2,670 RPM |
| **Max Manifold Press (MAP)**| 15.0 inHg | 27.8 inHg | **28.8 inHg** | 29.5 inHg | 40.4 inHg | Fleet median takeoff MAP is 28.8 inHg |
| **Inactivity Period (Days)** | 1.0 day | 2.68 days | **5.95 days** | 13.0 days | 728 days | Fleet median time between flights is ~6 days |
| **Ground Speed in Cruise** | 120 kt | 146 kt | **157 kt** | 168 kt | 224 kt | Fleet median cruise ground speed is 157 kt |

---

## 📅 Logged Flight History & Timeline

The database contains **485 flights** (~10.2 million telemetry data points) spanning **October 30, 2020 to Present**, representing ~99% of all flights and engine runs since construction completion.

```
[Oct 30, 2020: First Flight] ──► [Phase 1: Break-in / No Pants] ──► [Nov 5, 2021: Wheel Pants (+12-15 kt)] ──► [Phase 2: Modern Cruise]
```

### 1. Phase 1: Engine Break-In & Pre-Wheel-Pants (October 30, 2020 – November 4, 2021)
* **Status**: Aircraft flown without wheel pants during initial flight testing, flight envelope expansion, and engine break-in.
* **Observed Performance**:
  - **Median Cruise Speed**: **~134 – 139 kt TAS** (118 – 128 kt IAS)
* **Analytical Rule**: **Do NOT use pre-November 5, 2021 data for current performance benchmarks.** Ignore break-in fuel burn and speeds when modeling current aircraft capabilities.

### 2. Phase 2: Post Wheel-Pants Installation (November 5, 2021 – Present)
* **Exact Transition Date**: **November 5, 2021** (Wheel pants installed ~1 year after initial flight).
* **Observed Performance**:
  - **Step Change**: Instant **+12 to +15 knot increase in True Airspeed** under identical engine power settings!
  - **Median Cruise Speed**: **155 – 163 kt TAS** (133 – 139 kt IAS) depending on cruise altitude (6,000 to 13,900 ft).
* **Analytical Rule**: All current performance modeling, ETE estimations, and fuel planning must be derived strictly from **Phase 2 data (November 5, 2021 to Present)**.

---

## 📋 Standard Flight Planning Baselines

Use these empirical baselines for flight planning and range calculations:

| Mode / Phase | Speed (TAS) | Fuel Flow | Efficiency | Altitude / Context |
| :--- | :--- | :--- | :--- | :--- |
| **Normal Cruise** *(Recommended)* | **155 kt TAS** | **11.0 GPH** | **14.1 NM/gal** | Standard cross-country cruise (6,000–10,000 ft, ~62% Power). |
| **Economy Cruise** | **145 kt TAS** | **10.0 GPH** | **14.5 NM/gal** | Deep lean / low power cruise (~50–55% Power). |
| **High Altitude Cruise** | **163 kt TAS** | **10.8 GPH** | **15.1 NM/gal** | Cruising > 10,500 ft MSL. |
| **En-Route Climb** | **130 kt TAS** | **17.0 GPH** | **500 ft/min** | En-route climb from SL to cruise altitude. |

---

## 💡 Notes for AI Analysis & Queries

1. **Filtering Ground vs. Flight**: Active flight data is isolated in `n205en_engine_telemetry.parquet` (`IAS > 30 kt` & `RPM > 1000`). Ground, taxiing, and hangar maintenance runs are preserved in `n205en_ground_maintenance.parquet`.
2. **Savvy Alignment**: All 485 flights align 1:1 with Savvy Aviation Flight IDs and airport identifiers in `flights_metadata.parquet`.
