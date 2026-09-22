import streamlit as st
import pandas as pd
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Team Overview",
    page_icon="🏀",
    layout="wide",
)


# =========================================================
# LOAD DATA
# =========================================================



DATA_PATH = "DCM_V3/data/lineup/team_overview_4a.csv"

df = pd.read_csv(DATA_PATH)


# =========================================================
# TEAM
# =========================================================

team = df.iloc[0]


# =========================================================
# TITLE
# =========================================================

col1, col2 = st.columns([5, 1])

with col1:
    st.title("Team Overview")

with col2:
    st.image("DCM_V3/yDashboard/assets/athletics.png", width=100)

st.caption(
    "4A — Team-level offensive, defensive, and process performance"
)

st.divider()

# =========================================================
# TEAM SNAPSHOT
# =========================================================

st.subheader("Team Snapshot")

col1, col2, col3, col4, col5,col6 = st.columns(6)

with col1:
    st.metric(
        "Minutes",
        f"{team['Minutes']:.1f}"
    )
teamtotalposs = team["Completed Def Poss"] + team["Completed Off Poss"]
with col2:
    st.metric(
        "Possessions",
        f"{teamtotalposs:.0f}"
    )

with col3 : 
    st.metric(
        "Defensive Possessions",
        f"{team['Completed Def Poss']:.0f}"
    )
with col4:
    st.metric(
        "PM / 40",
        f"{team['PM_p40']:.1f}"
    )

with col5:
    st.metric(
        "Net RTG",
        f"{team['Net_RTG']:.1f}"
    )

with col6:
    st.metric(
        "Plus / Minus",
        f"{team['Plus_Minus']:.0f}"
    )


st.divider()


# =========================================================
# OFFENSE
# =========================================================

st.header("Offense")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "ORTG",
        f"{team['ORTG']:.1f}"
    )

with col2:
    st.metric(
        "Off PPP",
        f"{team['Off PPP']:.3f}"
    )

with col3:
    st.metric(
        "Score Rate",
        f"{team['Score Rate']:.1%}"
    )

with col4:
    st.metric(
        "Completed Off Poss",
        f"{team['Completed Off Poss']:.0f}"
    )


# ---------------------------------------------------------
# OFFENSIVE FOUR FACTORS
# ---------------------------------------------------------

st.subheader("Offensive Four Factors")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "eFG%",
        f"{team['O_eFG%']:.1%}"
    )

with col2:
    st.metric(
        "TOV%",
        f"{team['O_TOV%']:.1%}"
    )

with col3:
    st.metric(
        "ORB%",
        f"{team['O_ORB%']:.1%}"
    )

with col4:
    st.metric(
        "FTR",
        f"{team['O_FTR']:.1%}"
    )


st.divider()


# =========================================================
# DEFENSE
# =========================================================

st.header("Defense")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "DRTG",
        f"{team['DRTG']:.1f}"
    )

with col2:
    st.metric(
        "Def PPP",
        f"{team['Def PPP']:.3f}"
    )

with col3:
    st.metric(
        "Stop Rate",
        f"{team['Stop Rate']:.1%}"
    )

with col4:
    st.metric(
        "Completed Def Poss",
        f"{team['Completed Def Poss']:.0f}"
    )


# ---------------------------------------------------------
# DEFENSIVE FOUR FACTORS
# ---------------------------------------------------------

st.subheader("Defensive Four Factors")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "eFG% Allowed",
        f"{team['D_eFG%']:.1%}"
    )

with col2:
    st.metric(
        "TOV% Forced",
        f"{team['D_TOV%']:.1%}"
    )

with col3:
    st.metric(
        "ORB% Allowed",
        f"{team['D_ORB%']:.1%}"
    )

with col4:
    st.metric(
        "FTR Allowed",
        f"{team['D_FTR']:.1%}"
    )


st.divider()


# =========================================================
# DEFENSIVE PROCESS
# =========================================================

st.header("Defensive Process")

st.caption(
    "How frequently our defensive behaviors occurred across defensive possessions. 
    Note that this is counts for how many possessions contained at least one of these occurrences. 
    So even though it may say '25 paint touches' that's the number of possessions with a paint touch not the total number of paint touches allowed by our team."
)


# ---------------------------------------------------------
# POSSESSION OCCURRENCE
# ---------------------------------------------------------

st.subheader("Defensive Possession Occurrence")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Defensive Possessions",
        f"{team['All Def Poss']:.0f}"
    )
with col2:
    st.metric(
        "Middle",
        f"{team['Middle Possession Occurrence']:.1%}"
    )

with col3:
    st.metric(
        "Uncontested 3",
        f"{team['UC3 Possession Occurrence']:.1%}"
    )

with col4:
    st.metric(
        "Paint Touch",
        f"{team['Paint Touch Possession Occurrence']:.1%}"
    )

with col5:
    st.metric(
        "Deflection",
        f"{team['Deflection Possession Occurrence']:.1%}"
    )


# ---------------------------------------------------------
# RAW DEFENSIVE EVENTS
# ---------------------------------------------------------

st.subheader("Defensive Events")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Middle",
        f"{team['Middle']:.0f}"
    )

with col2:
    st.metric(
        "UC3",
        f"{team['UC3']:.0f}"
    )

with col3:
    st.metric(
        "Paint Touch",
        f"{team['Paint Touch']:.0f}"
    )

with col4:
    st.metric(
        "Deflections",
        f"{team['Deflection']:.0f}"
    )


st.divider()


# =========================================================
# DEFENSIVE OUTCOMES
# =========================================================

#st.header("Defensive Outcomes")
st.header("Later I'm changing this to TOV Forced, Stop Rate, Turnovers, Score Rate")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "O-Boards Allowed",
        f"{team['ORB Allowed']:.0f}"
    )

with col2:
    st.metric(
        "TOV Forced",
        f"{team['TOV Forced']:.0f}"
    )

with col3:
    st.metric(
        "Points Allowed",
        f"{team['PTS Allowed']:.0f}"
    )

with col4:
    st.metric(
        "Completed Def Poss",
        f"{team['Completed Def Poss']:.0f}"
    )
