# FIFA World Cup 2014 – Monte Carlo Simulation Project

## About this project
This project implements a Monte Carlo simulation of football matches
for the FIFA World Cup 2014.

FIFA World Ranking data is used to derive simple team strength parameters.
Based on these strengths, full World Cup tournaments (group stage and
knockout stage) are simulated repeatedly.

The goal is to estimate the probability that a team wins the World Cup.

---

## Project contents
This repository contains:
- a clean data pipeline (raw → interim → processed)
- scripts for creating a pre-World-Cup ranking snapshot
- transformation of FIFA ranking points into team strengths
- a complete Monte Carlo simulation of the World Cup 2014
- result tables and visualizations
- documentation and explanation notebooks

---

## Data source
The raw data is a public dataset based on official FIFA ranking releases.

The snapshot used for the World Cup 2014 is:
- **2014-06-05** (last ranking date before the tournament start on 2014-06-12)

---

## Folder structure
- `configs/` – configuration files (prepared for future extensions)
- `data/raw/` – original FIFA ranking data (unchanged)
- `data/interim/` – filtered snapshot (pre-WC 2014 ranking)
- `data/processed/` – final data for the simulation (team strengths)
- `figures/` – plots generated from simulation results
- `notebooks/` – exploration and explanation notebooks
- `reports/` – result tables and short written summaries
- `src/` – Python scripts for data processing and simulation
- `tests/` – optional consistency checks (documented)

---

## How the data was created
1. The full FIFA ranking dataset is placed in `data/raw/`
2. `src/make_pre_wc_2014_snapshot.py` extracts the last ranking before the World Cup
3. `src/make_team_strengths.py` transforms ranking points into normalized team strengths

---

## Simulation
The FIFA World Cup 2014 is simulated using a Monte Carlo approach.

Each simulation run represents one full tournament (group stage and knockout stage).
Match outcomes are random but weighted by team strengths derived from FIFA rankings.

Title probabilities are estimated using relative frequencies from repeated simulations.





