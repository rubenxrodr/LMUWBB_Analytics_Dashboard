# =========================================================
# 4_B — INDIVIDUAL PERFORMANCE
# =========================================================

import base64
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PATHS
# =========================================================

PAGE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = PAGE_DIR.parent

DATA_PATH = DASHBOARD_DIR.parent / "data" / "lineup" / "individual_lineupdata2.csv"
ASSETS_DIR = DASHBOARD_DIR / "assets"


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(DATA_PATH)

# Remove the * prefix from any column names.
# This keeps the dashboard clean even if older files still contain it.
df.columns = df.columns.str.lstrip("*")


# =========================================================
# PAGE TITLE
# =========================================================

st.title("Individual Performance")

st.caption(
    "Individual lineup performance measures how each player impacts "
    "team performance while they are on the floor."
)


# =========================================================
# MINIMUM POSSESSION FILTER
# =========================================================

min_possessions = st.slider(
    "Minimum Possessions",
    min_value=0,
    max_value=int(df["Total Possessions"].max()),
    value=20,
    step=5,
)

filtered_df = df[df["Total Possessions"] >= min_possessions].copy()
filtered_df.sort_values("rel_PM_p40", ascending=False, inplace=True)


# =========================================================
# PLAYER IMAGE HELPERS
# =========================================================

def get_player_image(player):
    """
    Return the local image path for a player.
    """

    image_path = ASSETS_DIR / f"{player}.webp"

    if image_path.exists():
        return str(image_path)

    return None


def image_to_data_uri(image_path):
    """
    Convert a local image into a data URI so it can be
    displayed inside Streamlit's dataframe ImageColumn.
    """

    if not image_path:
        return None

    path = Path(image_path)

    if not path.exists():
        return None

    encoded = base64.b64encode(path.read_bytes()).decode()

    return f"data:image/webp;base64,{encoded}"


# =========================================================
# LEADERBOARD DATA
# =========================================================

leaderboard = filtered_df[
    [
        "Player",
        "Minutes",
        "Total Possessions",
        "rel_PM_p40",
        "On-Off_PMp40",
        "ORTG",
        "DRTG",
        "Net_RTG",
    ]
].copy()


# ---------------------------------------------------------
# Add player image column
# ---------------------------------------------------------

leaderboard.insert(
    0,
    "Photo",
    leaderboard["Player"].apply(
        lambda player: image_to_data_uri(
            get_player_image(player)
        )
    ),
)


# =========================================================
# FORMATTING
# =========================================================

leaderboard["Minutes"] = leaderboard["Minutes"].round(0)
leaderboard["Total Possessions"] = leaderboard["Total Possessions"].round(0)

for col in [
    "rel_PM_p40",
    "On-Off_PMp40",
    "ORTG",
    "DRTG",
    "Net_RTG",
]:
    leaderboard[col] = leaderboard[col].round(0)


# =========================================================
# PLAYER PERFORMANCE LEADERBOARD
# =========================================================

st.subheader("Player Performance Leaderboard")

st.dataframe(
    leaderboard,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Photo": st.column_config.ImageColumn(
            " ",
            width="small",
        ),
        "Player": st.column_config.TextColumn(
            "Player",
            width="medium",
        ),
        "Minutes": st.column_config.NumberColumn(
            "Minutes",
            format="%.0f",
        ),
        "Total Possessions": st.column_config.NumberColumn(
            "Possessions",
            format="%.0f",
        ),
        "rel_PM_p40": st.column_config.ProgressColumn(
            "rel PM/40",
            format="%.0f",
            help="Player PM/40 relative to the team.",
            min_value=float(filtered_df["rel_PM_p40"].min()),
            max_value=float(filtered_df["rel_PM_p40"].max()),
        ),
        "On-Off_PMp40": st.column_config.NumberColumn(
            "On-Off PM/40",
            format="%.0f",
        ),
        "ORTG": st.column_config.NumberColumn(
            "ORTG",
            format="%.0f",
        ),
        "DRTG": st.column_config.NumberColumn(
            "DRTG",
            format="%.0f",
        ),
        "Net_RTG": st.column_config.NumberColumn(
            "Net RTG",
            format="%.0f",
        ),
    },
    column_order=[
        "Photo",
        "Player",
        "Minutes",
        "Total Possessions",
        "rel_PM_p40",
        "On-Off_PMp40",
        "ORTG",
        "DRTG",
        "Net_RTG",
    ],
)


# =========================================================
# RANKINGS
# =========================================================

st.divider()

st.subheader("Performance Rankings")

rank_col1, rank_col2 = st.columns(2)


# ---------------------------------------------------------
# ORTG RANKING
# ---------------------------------------------------------

with rank_col1:

    st.markdown("### Offensive Rating")

    ortg_df = (
        filtered_df[
            ["Player", "Total Possessions", "ORTG"]
        ]
        .sort_values("ORTG", ascending=False)
        .copy()
    )

    ortg_df["Total Possessions"] = ortg_df["Total Possessions"].round(0)
    ortg_df["ORTG"] = ortg_df["ORTG"].round(0)

    st.dataframe(
        ortg_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Player": st.column_config.TextColumn("Player"),
            "Total Possessions": st.column_config.NumberColumn(
                "Poss.",
                format="%.0f",
            ),
            "ORTG": st.column_config.NumberColumn(
                "ORTG",
                format="%.0f",
            ),
        },
    )


# ---------------------------------------------------------
# DRTG RANKING
# ---------------------------------------------------------

with rank_col2:

    st.markdown("### Defensive Rating")

    drtg_df = (
        filtered_df[
            ["Player", "Total Possessions", "DRTG"]
        ]
        .sort_values("DRTG", ascending=True)
        .copy()
    )

    drtg_df["Total Possessions"] = drtg_df["Total Possessions"].round(0)
    drtg_df["DRTG"] = drtg_df["DRTG"].round(0)

    st.dataframe(
        drtg_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Player": st.column_config.TextColumn("Player"),
            "Total Possessions": st.column_config.NumberColumn(
                "Poss.",
                format="%.0f",
            ),
            "DRTG": st.column_config.NumberColumn(
                "DRTG",
                format="%.0f",
            ),
        },
    )


# =========================================================
# SELECTED PLAYER
# =========================================================

st.divider()

st.subheader("Selected Player")

selected_player = st.selectbox(
    "Choose a player",
    filtered_df["Player"].tolist(),
)


player = filtered_df[
    filtered_df["Player"] == selected_player
].iloc[0]


# =========================================================
# PLAYER HEADER
# =========================================================

header_col1, header_col2 = st.columns([1, 3])


# ---------------------------------------------------------
# PLAYER PHOTO
# ---------------------------------------------------------

with header_col1:

    image_path = get_player_image(selected_player)

    if image_path:
        st.image(
            image_path,
            width=180,
        )
    else:
        st.info("No player image")


# ---------------------------------------------------------
# PLAYER INFORMATION
# ---------------------------------------------------------

with header_col2:

    st.subheader(selected_player)

    st.caption(
        f"{player['Minutes']:.0f} minutes • "
        f"{player['Total Possessions']:.0f} possessions"
    )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "rel PM/40",
            f"{player['rel_PM_p40']:.0f}",
        )

    with metric2:
        st.metric(
            "On-Off PM/40",
            f"{player['On-Off_PMp40']:.0f}",
        )

    with metric3:
        st.metric(
            "Net RTG",
            f"{player['Net_RTG']:.0f}",
        )


# =========================================================
# SELECTED PLAYER — OFFENSE / DEFENSE
# =========================================================

off_col, def_col = st.columns(2)


# ---------------------------------------------------------
# OFFENSE
# ---------------------------------------------------------

with off_col:

    st.markdown("### Offensive Performance")

    off1, off2 = st.columns(2)

    with off1:
        st.metric(
            "ORTG",
            f"{player['ORTG']:.0f}",
        )

    with off2:
        st.metric(
            "Relative ORTG",
            f"{player['rel_Off_RTG']:.0f}",
        )


# ---------------------------------------------------------
# DEFENSE
# ---------------------------------------------------------

with def_col:

    st.markdown("### Defensive Performance")

    def1, def2 = st.columns(2)

    with def1:
        st.metric(
            "DRTG",
            f"{player['DRTG']:.0f}",
        )

    with def2:
        st.metric(
            "Relative DRTG",
            f"{player['rel_Def_RTG']:.0f}",
        )


# =========================================================
# SELECTED PLAYER — ADDITIONAL IMPACT
# =========================================================

st.markdown("### Additional Impact")

impact1, impact2, impact3 = st.columns(3)

with impact1:
    st.metric(
        "PM/40",
        f"{player['PM_p40']:.0f}",
    )

with impact2:
    st.metric(
        "On-Off",
        f"{player['On-Off']:.0f}",
    )

with impact3:
    st.metric(
        "Plus / Minus",
        f"{player['Plus_Minus']:.0f}",
    )