# ============================================================
# BAYER LEVERKUSEN SQUAD RISK & RECRUITMENT ANALYSIS
# 2023/24 Bundesliga
#
# Python | Pandas | StatsBomb Open Data | Matplotlib
# ============================================================

from statsbombpy import sb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os


# ============================================================
# PROJECT SETTINGS
# ============================================================

TEAM = "Bayer Leverkusen"

COMPETITION_ID = 9
SEASON_ID = 281

DATA_FILE = "data/leverkusen_events.csv"

os.makedirs("data", exist_ok=True)
os.makedirs("images", exist_ok=True)


# ============================================================
# LEVERKUSEN VISUAL STYLE
# ============================================================

LEVERKUSEN_RED = "#E32221"
LEVERKUSEN_DARK_RED = "#B71918"
BLACK = "#111111"
DARK_GRAY = "#444444"
LIGHT_GRAY = "#E6E6E6"
WHITE = "#FFFFFF"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 17,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": WHITE,
    "axes.facecolor": WHITE
})


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def shorten_name(name):

    short_names = {
        "Alejandro Grimaldo García": "Alejandro Grimaldo",
        "Exequiel Alejandro Palacios": "Exequiel Palacios",
        "Edmond Fayçal Tapsoba": "Edmond Tapsoba",
        "Piero Martín Hincapié Reyna": "Piero Hincapié",
        "Victor Okoh Boniface": "Victor Boniface",
        "Odilon Kossonou": "Odilon Kossounou",
        "Arthur Augusto de Matos Soares": "Arthur",
        "Gustavo Adolfo Puerta Molano": "Gustavo Puerta"
    }

    return short_names.get(str(name), str(name))


def location_x(location):

    if pd.isna(location):
        return np.nan

    try:

        if isinstance(location, str):
            location = ast.literal_eval(location)

        return float(location[0])

    except (ValueError, SyntaxError, TypeError, IndexError):
        return np.nan


def clean_chart(ax):

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color(LIGHT_GRAY)
    ax.spines["bottom"].set_color(LIGHT_GRAY)

    ax.set_axisbelow(True)

    ax.grid(
        axis="x",
        color=LIGHT_GRAY,
        linewidth=0.8,
        alpha=0.7
    )


# ============================================================
# STEP 1: LOAD MATCHES
# ============================================================

print("\nLoading Bayer Leverkusen matches...")

matches = sb.matches(
    competition_id=COMPETITION_ID,
    season_id=SEASON_ID
)

print(
    matches[
        [
            "match_id",
            "match_date",
            "home_team",
            "away_team",
            "home_score",
            "away_score"
        ]
    ]
)

print("\nTotal matches:", len(matches))


# ============================================================
# STEP 2: LOAD EVENT DATA
# ============================================================

if os.path.exists(DATA_FILE):

    print("\nLoading saved event data...")

    events = pd.read_csv(
        DATA_FILE,
        low_memory=False
    )

else:

    print("\nDownloading event data...")

    all_events = []

    for match_id in matches["match_id"]:

        match_events = sb.events(
            match_id=match_id
        )

        all_events.append(match_events)

        print(f"Loaded match {match_id}")

    events = pd.concat(
        all_events,
        ignore_index=True
    )

    events.to_csv(
        DATA_FILE,
        index=False
    )

    print("\nSaved event data.")

print("\nTotal events:", len(events))
print("Total columns:", len(events.columns))


# ============================================================
# STEP 3: ISOLATE BAYER LEVERKUSEN EVENTS
# ============================================================

lev_events = events[
    events["team"] == TEAM
].copy()

print("\n--- LEVERKUSEN DATA ---")

print(
    "Leverkusen events:",
    len(lev_events)
)

print("\nEvent types:")

print(
    lev_events["type"]
    .value_counts()
    .head(15)
)

players = (
    lev_events["player"]
    .dropna()
    .value_counts()
)

print("\nPlayers:")
print(players)


# ============================================================
# STEP 4: BUILD PLAYER METRICS
# ============================================================

player_names = (
    lev_events["player"]
    .dropna()
    .unique()
)

player_metrics = pd.DataFrame({
    "player": player_names
})


# PASSES

passes = (
    lev_events[
        lev_events["type"] == "Pass"
    ]
    .groupby("player")
    .size()
    .rename("passes")
)


# CARRIES

carries = (
    lev_events[
        lev_events["type"] == "Carry"
    ]
    .groupby("player")
    .size()
    .rename("carries")
)


# SHOTS

shots = (
    lev_events[
        lev_events["type"] == "Shot"
    ]
    .groupby("player")
    .size()
    .rename("shots")
)


# EXPECTED GOALS

xg = (
    lev_events[
        lev_events["type"] == "Shot"
    ]
    .groupby("player")["shot_statsbomb_xg"]
    .sum()
    .rename("xg")
)


# PRESSURES

pressures = (
    lev_events[
        lev_events["type"] == "Pressure"
    ]
    .groupby("player")
    .size()
    .rename("pressures")
)


# BALL RECOVERIES

recoveries = (
    lev_events[
        lev_events["type"] == "Ball Recovery"
    ]
    .groupby("player")
    .size()
    .rename("recoveries")
)


# SHOT ASSISTS

shot_assists = (
    lev_events[
        (lev_events["type"] == "Pass") &
        (lev_events["pass_shot_assist"] == True)
    ]
    .groupby("player")
    .size()
    .rename("shot_assists")
)


# ============================================================
# FINAL-THIRD PASSES
# ============================================================

final_third_passes_df = (
    lev_events[
        (lev_events["type"] == "Pass") &
        (lev_events["pass_end_location"].notna())
    ]
    .copy()
)

final_third_passes_df["end_x"] = (
    final_third_passes_df[
        "pass_end_location"
    ].apply(location_x)
)

final_third_passes = (
    final_third_passes_df[
        final_third_passes_df["end_x"] >= 80
    ]
    .groupby("player")
    .size()
    .rename("final_third_passes")
)


# ============================================================
# FINAL-THIRD CARRIES
# ============================================================

final_third_carries_df = (
    lev_events[
        (lev_events["type"] == "Carry") &
        (lev_events["carry_end_location"].notna())
    ]
    .copy()
)

final_third_carries_df["end_x"] = (
    final_third_carries_df[
        "carry_end_location"
    ].apply(location_x)
)

final_third_carries = (
    final_third_carries_df[
        final_third_carries_df["end_x"] >= 80
    ]
    .groupby("player")
    .size()
    .rename("final_third_carries")
)


# ============================================================
# MERGE PLAYER METRICS
# ============================================================

metrics = [
    passes,
    carries,
    shots,
    xg,
    pressures,
    recoveries,
    shot_assists,
    final_third_passes,
    final_third_carries
]

for metric in metrics:

    player_metrics = player_metrics.merge(
        metric,
        left_on="player",
        right_index=True,
        how="left"
    )


player_metrics = player_metrics.fillna(0)


# TOTAL ACTIONS

player_metrics["total_actions"] = (
    player_metrics["passes"] +
    player_metrics["carries"] +
    player_metrics["shots"] +
    player_metrics["pressures"] +
    player_metrics["recoveries"]
)


player_metrics = player_metrics.sort_values(
    "total_actions",
    ascending=False
)


print("\n--- PLAYER METRICS ---")

print(
    player_metrics.head(20)
)


player_metrics.to_csv(
    "data/player_metrics.csv",
    index=False
)

print(
    "\nSaved player metrics to "
    "data/player_metrics.csv"
)


# ============================================================
# STEP 5: CALCULATE PLAYER DEPENDENCY
# ============================================================

dependency_metrics = [
    "passes",
    "carries",
    "shots",
    "xg",
    "pressures",
    "recoveries",
    "shot_assists",
    "final_third_passes",
    "final_third_carries"
]


for metric in dependency_metrics:

    total = player_metrics[metric].sum()

    player_metrics[
        f"{metric}_share"
    ] = (
        player_metrics[metric] /
        total *
        100
    )


# Focus on regularly involved squad players

main_squad = player_metrics[
    player_metrics["total_actions"] >= 500
].copy()


# ATTACKING DEPENDENCY

main_squad["attacking_dependency"] = (
    main_squad["xg_share"] +
    main_squad["shot_assists_share"] +
    main_squad["final_third_passes_share"] +
    main_squad["final_third_carries_share"]
) / 4


# POSSESSION DEPENDENCY

main_squad["possession_dependency"] = (
    main_squad["passes_share"] +
    main_squad["carries_share"]
) / 2


# DEFENSIVE DEPENDENCY

main_squad["defensive_dependency"] = (
    main_squad["pressures_share"] +
    main_squad["recoveries_share"]
) / 2


main_squad = main_squad.sort_values(
    "attacking_dependency",
    ascending=False
)


print("\n--- SQUAD DEPENDENCY ---")

print(
    main_squad[
        [
            "player",
            "attacking_dependency",
            "possession_dependency",
            "defensive_dependency"
        ]
    ].round(2)
)


main_squad.to_csv(
    "data/squad_dependency.csv",
    index=False
)

print(
    "\nSaved squad dependency table."
)


# ============================================================
# CHART 1: ATTACKING DEPENDENCY
# ============================================================

attack_chart = (
    main_squad
    .sort_values(
        "attacking_dependency",
        ascending=False
    )
    .head(10)
    .copy()
)

attack_chart["display_name"] = (
    attack_chart["player"]
    .apply(shorten_name)
)

attack_chart = attack_chart.sort_values(
    "attacking_dependency",
    ascending=True
)


fig, ax = plt.subplots(
    figsize=(11, 6.5)
)

colors = [
    LEVERKUSEN_RED
    if player == attack_chart.iloc[-1]["player"]
    else BLACK
    for player in attack_chart["player"]
]


bars = ax.barh(
    attack_chart["display_name"],
    attack_chart["attacking_dependency"],
    color=colors,
    height=0.68
)


for bar, value in zip(
    bars,
    attack_chart["attacking_dependency"]
):

    ax.text(
        value + 0.15,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=BLACK
    )


ax.set_xlabel(
    "Attacking Dependency (%)",
    fontweight="bold"
)

ax.set_ylabel("")

ax.set_title(
    "BAYER LEVERKUSEN | ATTACKING DEPENDENCY",
    loc="left",
    fontweight="bold",
    color=BLACK,
    pad=18
)

ax.text(
    0,
    1.01,
    "2023/24 Bundesliga • Top 10 regularly involved players",
    transform=ax.transAxes,
    fontsize=10,
    color=DARK_GRAY
)

clean_chart(ax)

ax.text(
    0,
    -0.13,
    "Attacking dependency = average share of xG, shot assists, "
    "final-third passes and final-third carries.",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY
)

ax.text(
    1,
    -0.13,
    "Source: StatsBomb Open Data",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "images/attacking_dependency.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=WHITE
)

plt.close()

print(
    "\nSaved Chart 1: "
    "images/attacking_dependency.png"
)


# ============================================================
# CHART 2: FINAL-THIRD PROGRESSION
# ============================================================

main_squad["final_third_actions"] = (
    main_squad["final_third_passes"] +
    main_squad["final_third_carries"]
)


progression_chart = (
    main_squad
    .sort_values(
        "final_third_actions",
        ascending=False
    )
    .head(10)
    .copy()
)

progression_chart["display_name"] = (
    progression_chart["player"]
    .apply(shorten_name)
)

progression_chart = (
    progression_chart
    .sort_values(
        "final_third_actions",
        ascending=True
    )
)


fig, ax = plt.subplots(
    figsize=(11, 6.5)
)


ax.barh(
    progression_chart["display_name"],
    progression_chart["final_third_passes"],
    color=BLACK,
    height=0.68,
    label="Final-Third Passes"
)


ax.barh(
    progression_chart["display_name"],
    progression_chart["final_third_carries"],
    left=progression_chart["final_third_passes"],
    color=LEVERKUSEN_RED,
    height=0.68,
    label="Final-Third Carries"
)


ax.set_xlabel(
    "Final-Third Actions",
    fontweight="bold"
)

ax.set_ylabel("")


ax.set_title(
    "BAYER LEVERKUSEN | FINAL-THIRD PROGRESSION",
    loc="left",
    fontweight="bold",
    color=BLACK,
    pad=18
)


ax.text(
    0,
    1.01,
    "2023/24 Bundesliga • Passes and carries ending in the attacking third",
    transform=ax.transAxes,
    fontsize=10,
    color=DARK_GRAY
)


clean_chart(ax)


legend = ax.legend(
    frameon=False,
    loc="lower right"
)


ax.text(
    0,
    -0.13,
    "Attacking third begins at x = 80 on the StatsBomb 120 × 80 pitch.",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY
)


ax.text(
    1,
    -0.13,
    "Source: StatsBomb Open Data",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY,
    ha="right"
)


plt.tight_layout()

plt.savefig(
    "images/final_third_progression.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=WHITE
)

plt.close()

print(
    "Saved Chart 2: "
    "images/final_third_progression.png"
)


# ============================================================
# CHART 3: SQUAD RISK MATRIX
# ============================================================

risk_chart = main_squad.copy()


risk_chart["involvement_share"] = (
    risk_chart["total_actions"] /
    risk_chart["total_actions"].sum() *
    100
)


risk_chart["involvement_share"] = pd.to_numeric(
    risk_chart["involvement_share"],
    errors="coerce"
)


risk_chart["attacking_dependency"] = pd.to_numeric(
    risk_chart["attacking_dependency"],
    errors="coerce"
)


risk_chart = risk_chart.dropna(
    subset=[
        "involvement_share",
        "attacking_dependency"
    ]
)


avg_involvement = float(
    risk_chart["involvement_share"].mean()
)

avg_attack = float(
    risk_chart["attacking_dependency"].mean()
)


fig, ax = plt.subplots(
    figsize=(11, 7)
)


# Highlight upper-right risk area

ax.axvspan(
    avg_involvement,
    risk_chart["involvement_share"].max() + 1,
    ymin=(
        avg_attack /
        (risk_chart["attacking_dependency"].max() + 1)
    ),
    alpha=0.04,
    color=LEVERKUSEN_RED
)


# Plot all players

ax.scatter(
    risk_chart["involvement_share"].to_numpy(),
    risk_chart["attacking_dependency"].to_numpy(),
    s=85,
    color=BLACK,
    alpha=0.75
)


# Highlight highest attacking dependency player

priority_player = risk_chart.loc[
    risk_chart[
        "attacking_dependency"
    ].idxmax()
]


ax.scatter(
    float(priority_player["involvement_share"]),
    float(priority_player["attacking_dependency"]),
    s=145,
    color=LEVERKUSEN_RED,
    edgecolor=WHITE,
    linewidth=1.5,
    zorder=5
)


for _, row in risk_chart.iterrows():

    label = shorten_name(row["player"])

    # Make matrix labels shorter
    label = (
        label
        .replace("Alejandro ", "")
        .replace("Exequiel ", "")
        .replace("Edmond ", "")
        .replace("Piero ", "")
        .replace("Victor ", "")
        .replace("Jeremie ", "")
        .replace("Florian ", "")
        .replace("Granit ", "")
        .replace("Robert ", "")
        .replace("Jonas ", "")
        .replace("Josip ", "")
        .replace("Odilon ", "")
    )

    ax.text(
        float(row["involvement_share"]) + 0.08,
        float(row["attacking_dependency"]) + 0.08,
        label,
        fontsize=8.5,
        color=BLACK
    )


ax.axvline(
    avg_involvement,
    linestyle="--",
    linewidth=1,
    color=DARK_GRAY,
    alpha=0.6
)


ax.axhline(
    avg_attack,
    linestyle="--",
    linewidth=1,
    color=DARK_GRAY,
    alpha=0.6
)


ax.text(
    0.985,
    0.965,
    "HIGHER DEPENDENCY\nHIGHER INVOLVEMENT",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=8,
    color=LEVERKUSEN_DARK_RED,
    fontweight="bold"
)


ax.set_xlabel(
    "Share of Team Involvement (%)",
    fontweight="bold"
)

ax.set_ylabel(
    "Attacking Dependency (%)",
    fontweight="bold"
)


ax.set_title(
    "BAYER LEVERKUSEN | SQUAD RISK MATRIX",
    loc="left",
    fontweight="bold",
    color=BLACK,
    pad=18
)


ax.text(
    0,
    1.01,
    "2023/24 Bundesliga • Functional concentration vs. overall involvement",
    transform=ax.transAxes,
    fontsize=10,
    color=DARK_GRAY
)


ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color(LIGHT_GRAY)
ax.spines["bottom"].set_color(LIGHT_GRAY)

ax.grid(
    color=LIGHT_GRAY,
    linewidth=0.7,
    alpha=0.45
)

ax.set_axisbelow(True)


ax.text(
    0,
    -0.12,
    "Dashed lines represent main-squad averages. "
    "The matrix indicates functional concentration, not injury probability.",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY
)


ax.text(
    1,
    -0.12,
    "Source: StatsBomb Open Data",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY,
    ha="right"
)


plt.tight_layout()

plt.savefig(
    "images/squad_risk_matrix.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=WHITE
)

plt.close()

print(
    "Saved Chart 3: "
    "images/squad_risk_matrix.png"
)


# ============================================================
# CHART 4: RECRUITMENT PRIORITY PROFILE
# ============================================================

priority_player = main_squad.loc[
    main_squad[
        "attacking_dependency"
    ].idxmax()
]


profile_metrics = {
    "Chance Creation":
        priority_player[
            "shot_assists_share"
        ],

    "Final-Third Passing":
        priority_player[
            "final_third_passes_share"
        ],

    "Final-Third Carrying":
        priority_player[
            "final_third_carries_share"
        ],

    "Shot / xG Threat":
        priority_player[
            "xg_share"
        ]
}


profile_df = pd.DataFrame({
    "Metric": profile_metrics.keys(),
    "Dependency": profile_metrics.values()
})


profile_df = profile_df.sort_values(
    "Dependency",
    ascending=True
)


fig, ax = plt.subplots(
    figsize=(10.5, 6)
)


colors = [
    LEVERKUSEN_RED
    if value == profile_df["Dependency"].max()
    else BLACK
    for value in profile_df["Dependency"]
]


bars = ax.barh(
    profile_df["Metric"],
    profile_df["Dependency"],
    color=colors,
    height=0.62
)


for bar, value in zip(
    bars,
    profile_df["Dependency"]
):

    ax.text(
        value + 0.15,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}%",
        va="center",
        fontsize=10,
        fontweight="bold",
        color=BLACK
    )


ax.set_xlabel(
    "Share of Team Output (%)",
    fontweight="bold"
)

ax.set_ylabel("")


priority_name = shorten_name(
    priority_player["player"]
)


ax.set_title(
    "BAYER LEVERKUSEN | RECRUITMENT PRIORITY PROFILE",
    loc="left",
    fontweight="bold",
    color=BLACK,
    pad=18
)


ax.text(
    0,
    1.01,
    f"Attacking functions most dependent on {priority_name}",
    transform=ax.transAxes,
    fontsize=10,
    color=DARK_GRAY
)


clean_chart(ax)


ax.text(
    0,
    -0.15,
    "Interpretation: depth recruitment should help reproduce the "
    "highest-concentration attacking functions — not replicate the player exactly.",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY
)


ax.text(
    1,
    -0.15,
    "Source: StatsBomb Open Data",
    transform=ax.transAxes,
    fontsize=8.5,
    color=DARK_GRAY,
    ha="right"
)


plt.tight_layout()

plt.savefig(
    "images/recruitment_priority_profile.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=WHITE
)

plt.close()


print(
    "Saved Chart 4: "
    "images/recruitment_priority_profile.png"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)

print(
    "BAYER LEVERKUSEN ANALYSIS COMPLETE"
)

print("=" * 60)


print(
    "\nHighest attacking dependency:",
    priority_name
)


print(
    "\nAttacking dependency:",
    f"{priority_player['attacking_dependency']:.1f}%"
)


print("\nRecruitment priority profile:")

print(
    profile_df
    .sort_values(
        "Dependency",
        ascending=False
    )
    .round(2)
    .to_string(index=False)
)


print("\nFiles created:")

print(
    "  data/player_metrics.csv"
)

print(
    "  data/squad_dependency.csv"
)

print(
    "  images/attacking_dependency.png"
)

print(
    "  images/final_third_progression.png"
)

print(
    "  images/squad_risk_matrix.png"
)

print(
    "  images/recruitment_priority_profile.png"
)

print(
    "\nProject analysis successfully completed."
)