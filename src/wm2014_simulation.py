"""
FIFA World Cup 2014 Monte Carlo Simulation

"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# SETTINGS 
# -------------------------
N_SIMULATIONS = 20000
SEED = 42
BASE_GOALS = 1.3  # controls typical goal level

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "teams_strengths_pre_wc_2014.csv"
REPORTS_DIR = Path("reports")
FIGURES_DIR = Path("figures")
REPORTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

rng = np.random.default_rng(SEED)

# -------------------------
# WORLD CUP 2014 TEAMS
# -------------------------
WC2014_TEAMS = [
    "Brazil", "Croatia", "Mexico", "Cameroon",
    "Spain", "Netherlands", "Chile", "Australia",
    "Colombia", "Greece", "Côte d'Ivoire", "Japan",
    "Uruguay", "Costa Rica", "England", "Italy",
    "Switzerland", "Ecuador", "France", "Honduras",
    "Argentina", "Bosnia and Herzegovina", "IR Iran", "Nigeria",
    "Germany", "Portugal", "Ghana", "USA",
    "Belgium", "Algeria", "Russia", "Korea Republic",
]


# -------------------------
# LOAD TEAM STRENGTHS
# -------------------------
df = pd.read_csv(DATA_PATH)
if not {"team", "strength"}.issubset(df.columns):
    raise ValueError("Expected columns in teams file: team, strength")

STRENGTH = dict(zip(df["team"], df["strength"]))

# -------------------------
# WC 2014 STRUCTURE
# -------------------------
GROUPS = {
    "A": ["Brazil", "Croatia", "Mexico", "Cameroon"],
    "B": ["Spain", "Netherlands", "Chile", "Australia"],
    "C": ["Colombia", "Greece", "Côte d'Ivoire", "Japan"],
    "D": ["Uruguay", "Costa Rica", "England", "Italy"],
    "E": ["Switzerland", "Ecuador", "France", "Honduras"],
    "F": ["Argentina", "Bosnia and Herzegovina", "IR Iran", "Nigeria"],
    "G": ["Germany", "Portugal", "Ghana", "USA"],
    "H": ["Belgium", "Algeria", "Russia", "Korea Republic"],
}

ROUND_OF_16 = [
    ("A1", "B2"), ("C1", "D2"),
    ("B1", "A2"), ("D1", "C2"),
    ("E1", "F2"), ("G1", "H2"),
    ("F1", "E2"), ("H1", "G2"),
]

# -------------------------
# MATCH MODEL (Poisson goals)
# -------------------------
def simulate_match(team_a: str, team_b: str) -> tuple[int, int]:
    """
    Simulates a single football match between two teams.

    The number of goals for each team is generated using a Possion distribution.
    The expected goals depend on the realative team strengths derived from FIFA rankings.

    Parameters:
    team_a : str
        Name of the first team
    team_b : str
        Name of the second team

    Returns:
    ga : int
        Goals scored by team A
    gb: int
        Goals scored by team B
    """
    sa = float(STRENGTH[team_a])
    sb = float(STRENGTH[team_b])

    # simple strength share
    denom = sa + sb + 1e-12
    share_a = sa / denom
    share_b = sb / denom

    lam_a = max(0.05, BASE_GOALS * share_a)
    lam_b = max(0.05, BASE_GOALS * share_b)

    ga = int(rng.poisson(lam_a))
    gb = int(rng.poisson(lam_b))
    return ga, gb

def knockout_winner(team_a: str, team_b: str) -> str:
    """
    Determines the winner of a knockout match between two teams.

    If the match ends in a draw, the winner is decided by a strength-weight penalty 
    shootout.

    Parameters:
    team_a: str
        Name of the first team.
    team_b: str
        Name of the second team.

    Returns:
    winner: str
        Name of the winning team
    """
    ga, gb = simulate_match(team_a, team_b)

    if ga > gb:
        return team_a
    if gb > ga:
        return team_b

    # draw -> penalties 
    sa = float(STRENGTH[team_a])
    sb = float(STRENGTH[team_b])
    p_a = sa / (sa + sb + 1e-12)
    return team_a if rng.random() < p_a else team_b

# -------------------------
# GROUP STAGE
# -------------------------
def simulate_group(teams: list[str]) -> tuple[str, str]:
    """
    Simulates the group stage for a group of four teams.

    Each team plays against every other team once.
    Teams are ranked by points, then goal difference.
    Remaining ties are broken randomly.

    Parameters:
    teams: list of str
        List of four team names in the group.

    Returns:
    winner: str
        Group winnner.
    runner_up : str
        Second place of the group
    """
    # table: points and goal difference only 
    table = {t: {"pts": 0, "gd": 0} for t in teams}

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            a, b = teams[i], teams[j]
            ga, gb = simulate_match(a, b)

            table[a]["gd"] += ga - gb
            table[b]["gd"] += gb - ga

            if ga > gb:
                table[a]["pts"] += 3
            elif gb > ga:
                table[b]["pts"] += 3
            else:
                table[a]["pts"] += 1
                table[b]["pts"] += 1

    # sort by pts, gd, then random to break full ties
    ranking = sorted(
        teams,
        key=lambda t: (table[t]["pts"], table[t]["gd"], rng.random()),
        reverse=True,
    )
    return ranking[0], ranking[1]

# -------------------------
# TOURNAMENT 
# -------------------------
def simulate_world_cup_2014() -> tuple[str, str]:
    """ 
    Simulates one complete FIFA World Cup 2014 tournament.

    The simulation includes the group stage and all knockout rounds.
    Group winners and runner-up advance according to the official tournement bracket.

    Returns

    champion: str
        World Cup winner.
    runner_up : str
        Losing finalist
    """
    slots = {}

    # group stage -> slots A1, A2, ...
    for g, teams in GROUPS.items():
        w, r = simulate_group(teams)
        slots[f"{g}1"] = w
        slots[f"{g}2"] = r

    # Round of 16 winners
    winners = []
    for a_slot, b_slot in ROUND_OF_16:
        winners.append(knockout_winner(slots[a_slot], slots[b_slot]))

    # Quarterfinals -> Semifinals -> Final
    while len(winners) > 2:
        winners = [knockout_winner(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]

    finalist1, finalist2 = winners[0], winners[1]
    champion = knockout_winner(finalist1, finalist2)
    runner_up = finalist2 if champion == finalist1 else finalist1
    return champion, runner_up

# -------------------------
# MONTE CARLO LOOP
# -------------------------
champions = []
finalists = []

for _ in range(N_SIMULATIONS):
    champ, runner_up = simulate_world_cup_2014()
    champions.append(champ)
    finalists.append(champ)
    finalists.append(runner_up)

# -------------------------
# RESULTS 
# -------------------------

champ_series = pd.Series(champions)

# Probability of winning the title 
p_title = champ_series.value_counts(normalize=True)

result = pd.DataFrame({
    "team": sorted(set(STRENGTH.keys()))
})
result["p_title"] = result["team"].map(p_title).fillna(0.0)

result = result[result["team"].isin(WC2014_TEAMS)]
result = result.sort_values("p_title", ascending=False)


# save CSV
out_csv = REPORTS_DIR / "wm2014_title_probabilities.csv"
result.to_csv(out_csv, index=False)

# short summary text
summary = (
    "WM 2014 Monte Carlo Simulation (student version)\n"
    f"N simulations: {N_SIMULATIONS}\n"
    f"Seed: {SEED}\n"
    f"BASE_GOALS: {BASE_GOALS}\n"
    "Output:\n"
    "- reports/wm2014_title_probabilities.csv\n"
    "- figures/wm2014_title_probabilities.png\n"
    "\nModel notes:\n"
    "- Group tie-break simplified: points, goal difference, then random.\n"
    "- Knockout draws resolved by strength-weighted penalties.\n"
)
(REPORTS_DIR / "wm2014_summary.txt").write_text(summary, encoding="utf-8")

# -------------------------
# PLOT 
# -------------------------
TOP_N = 15
top = result.head(TOP_N).copy()

plt.figure(figsize=(12, 6))
x = np.arange(len(top))

plt.bar(x, top["p_title"], color="orange", label="Win Title (P)")
plt.xticks(x, top["team"], rotation=45, ha="right")
plt.ylabel("Probability")
plt.title("World Cup 2014 Monte Carlo: Probability to Win the Title (Top Teams)")
plt.legend()
plt.tight_layout()

fig_path = FIGURES_DIR / "wm2014_title_probabilities.png"
plt.savefig(fig_path, dpi=200)
plt.close()

print(" Done.")
print(f"Saved: {out_csv}")
print(f"Saved: {fig_path}")
print(result.to_string(index=False))

