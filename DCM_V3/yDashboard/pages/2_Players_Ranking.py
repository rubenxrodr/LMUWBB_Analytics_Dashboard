import streamlit as st
import pandas as pd
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Players — DCM Ranking",
    page_icon="🏀",
    layout="wide",
)


# =========================================================
# LOAD DATA
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "dcm"
    / "master"
    / "dcm_metric.csv"
)

df = pd.read_csv(DATA_PATH)


# =========================================================
# TITLE
# =========================================================

st.title("Players — Defensive Completeness")

st.caption(
    "L2 — Player-level Defensive Completeness ranking"
)

st.divider()


# =========================================================
# WHAT IS DCM?
# =========================================================

st.header("What is Defensive Completeness?")

st.markdown(
    """
    **Defensive Completeness Metric (DCM)** is a program-specific
    measure of defensive execution.

    Traditional defensive statistics tell us **what happened** —
    points allowed, rebounds, turnovers, etc. DCM is designed to
    capture **how completely we execute the defensive behaviors
    that we value**.
    """
)

st.markdown(
    """
    DCM incorporates defensive actions and outcomes that are not
    fully represented in the traditional box score, including:

    - Middle Drives
    - Uncontested 3s
    - Paint Touches
    - Fouls
    - Deflections
    - Charges Taken
    - Loose Balls Recovered
    - Successful Boxouts
    - O-Boards Allowed
    """
)

st.divider()




# =========================================================
# 9 DCM Process Metrics Further Explained
# =========================================================


st.markdown(
    """
   9 DCM Process Metrics Further Explained
    """
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2: 

    st.image(
        "yDashboard/assets/9DCM.png",
        use_container_width=False,
        
)
st.divider()


# =========================================================
# HOW DCM WORKS
# =========================================================

st.header("How DCM Works")

st.markdown(
    """
    DCM is built in three stages:
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Defensive Events")
    st.write(
        "Track the defensive behaviors and outcomes that "
        "define our defensive standard."
    )

with col2:
    st.subheader("2. Normalize")
    st.write(
        "Convert those events into frequencies and "
        "per-possession measures so players can be compared "
        "across different workloads."
    )

with col3:
    st.subheader("3. Combine")
    st.write(
        "Standardize the components and combine them into "
        "a single Defensive Completeness Metric."
    )


st.divider()


# =========================================================
# INTERPRETING DCM
# =========================================================

st.header("Interpreting DCM")

st.markdown(
    """
    **Higher DCM indicates more complete defensive execution.**

    DCM is not simply a count of defensive events. Each component
    is evaluated relative to the player population and contributes
    to an overall measure of defensive completeness.

    This means the DCM score should be interpreted alongside the
    underlying defensive profile and the number of defensive
    possessions on which the player was evaluated.
    """
)


st.divider()


# =========================================================
# RANKING
# =========================================================

st.header("Player DCM Ranking")

st.caption(
    "Players are ranked by overall Defensive Completeness Metric. // Notes: I need to add pictures. Get rid of rank"
)


# ---------------------------------------------------------
# MINIMUM POSSESSION FILTER
# ---------------------------------------------------------

min_possessions = st.number_input(
    "Minimum Defensive Possessions",
    min_value=0,
    max_value=int(df["Defensive Possessions"].max()),
    value=20,
    step=10,
)

ranking_df = df[
    df["Defensive Possessions"] >= min_possessions
].copy()


# ---------------------------------------------------------
# SORT
# ---------------------------------------------------------

ranking_df = (
    ranking_df
    .sort_values(
        "DCM",
        ascending=False,
    )
    .reset_index(drop=True)
)

ranking_df.insert(
    0,
    "Rank",
    ranking_df.index + 1,
)


# =========================================================
# RANKING TABLE
# =========================================================

display_columns = [
    "Rank",
    "Player",
    "Defensive Possessions",
    "On-Ball Opportunities",
    "DCM",
    "DCM_Z",
]

display_df = ranking_df[display_columns].copy()

display_df["DCM"] = display_df["DCM"].map(
    lambda x: f"{x:.2f}"
)

display_df["DCM_Z"] = display_df["DCM_Z"].map(
    lambda x: f"{x:.2f}"
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


st.divider()


# =========================================================
# TOP PLAYER
# =========================================================

if not ranking_df.empty:

    leader = ranking_df.iloc[0]

    st.header("Current DCM Leader")

    col1, col2, col3, col4 = st.columns(4)
 
    leader_name = leader["Player"].split(" ",1)[1]
    with col1:
        image_path = Path("yDashboard/assets") / f"{leader_name}.webp"
        st.image(image_path, width=150)

    with col2:
        st.metric(
            "Player",
            leader["Player"],
        )

    with col3:
        st.metric(
            "DCM",
            f"{leader['DCM']:.2f}",
        )

    with col4:
        st.metric(
            "Defensive Possessions",
            f"{leader['Defensive Possessions']:.0f}",
        )

st.divider()


# =========================================================
# DEFENSIVE PROFILE
# =========================================================

st.header("DCM Component Profile")

st.caption(
    "The overall DCM score is built from the following defensive components."
)


component_columns = [
    ("Middle Drives", "Middle Drives"),
    ("Uncontested 3s", "Uncontested 3s"),
    ("Paint Touches", "Paint Touches"),
    ("Fouls", "Fouls"),
    ("Deflections", "Deflections"),
    ("Charges Taken", "Charges Taken"),
    ("Loose Balls Recovered", "Loose Balls Recovered"),
    ("Successful Boxouts", "Successful Boxouts"),
    ("Missed Boxouts", "Missed Boxouts"),
    ("O-Boards Allowed", "O-Boards Allowed"),
]


profile_columns = [
    "Player",
    "DCM",
]

for label, column in component_columns:

    if column in ranking_df.columns:
        profile_columns.append(column)


profile_df = ranking_df[profile_columns].copy()


# ---------------------------------------------------------
# FRIENDLY COLUMN NAMES
# ---------------------------------------------------------

profile_df = profile_df.rename(
    columns={
        "Uncontested 3s": "Uncontested 3s",
        "Loose Balls Recovered": "Loose Balls Recovered",
    }
)


# ---------------------------------------------------------
# FORMAT
# ---------------------------------------------------------

if "DCM" in profile_df.columns:
    profile_df["DCM"] = profile_df["DCM"].map(
        lambda x: f"{x:.2f}"
    )


st.dataframe(
    profile_df,
    use_container_width=True,
    hide_index=True,
)