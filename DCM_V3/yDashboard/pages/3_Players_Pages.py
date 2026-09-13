import streamlit as st
import pandas as pd
from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Individual DCM",
    page_icon="🏀",
    layout="wide",
)


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "dcm"
    / "master"
    / "dcm_metric.csv"
)

ASSETS_PATH = (
    PROJECT_ROOT
    / "yDashboard"
    / "assets"
    / "players"
)


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(DATA_PATH)

# Remove leading "*" from column names.
# This keeps the dashboard terminology clean while allowing
# the existing CSV to retain its current schema.
df.columns = df.columns.str.lstrip("*")


# =========================================================
# PLAYER SELECTOR
# =========================================================

st.title("Individual Defensive Completeness")

st.caption(
    "L3 — Individual DCM profile"
)

player_names = df["Player"].tolist()

selected_player = st.selectbox(
    "Player",
    player_names,
)

player = df[
    df["Player"] == selected_player
].iloc[0]


# =========================================================
# PLAYER NAME
# =========================================================

player_name = player["Player"]

# Extract jersey number if the name begins with #number
if isinstance(player_name, str) and player_name.startswith("#"):
    parts = player_name.split(" ", 1)
    jersey_number = parts[0]
    display_name = parts[1] if len(parts) > 1 else player_name
else:
    jersey_number = ""
    display_name = player_name


st.divider()


player_image = (
    PROJECT_ROOT
    / "yDashboard"
    / "assets"
    / f"{display_name}.webp"
)
# =========================================================













# =========================================================
# PLAYER HEADER
# =========================================================

scale_img_path = (
    PROJECT_ROOT
    / "yDashboard"
    / "assets"
    / "dcm_rating_scale.png"
)

header_col1, header_col2, header_col3 = st.columns(
    [1.1, 2.2, 1.1],
    gap="large"
)


# ---------------------------------------------------------
# LEFT — PLAYER PHOTO
# ---------------------------------------------------------

with header_col1:

    if player_image.exists():
        st.image(
            player_image,
            use_container_width=True
        )


# ---------------------------------------------------------
# CENTER — PLAYER INFO
# ---------------------------------------------------------

with header_col2:

   
    st.markdown(
        f"""
        <h1 style="
            margin-bottom:0px;
            font-size:42px;
        ">
            {display_name.upper()}
        </h1>
        """,
        unsafe_allow_html=True,
    )

    if jersey_number:
        st.markdown(
            f"""
            <div style="
                font-size:20px;
                margin-bottom:20px;
            ">
                {jersey_number}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Defensive Profile")

    st.write(
        f"""
        **Defensive Possessions:** 
        {player["Defensive Possessions"]:.0f}
        """
    )

    st.divider()

    score_col, rating_col = st.columns(2)

    with score_col:

        st.markdown(
            """
            <div style="
                font-size:16px;
                font-weight:600;
            ">
                DCM SCORE
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="
                font-size:64px;
                font-weight:800;
                line-height:1;
            ">
                {player["DCM"]:.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("OUT OF 7")


    with rating_col:

        dcm_rating = round(player["DCM"])

        # Keep rating inside the 1–7 scale
        dcm_rating = max(1, min(7, dcm_rating))

        st.markdown(
            """
            <div style="
                font-size:16px;
                font-weight:600;
            ">
                DCM RATING
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="
                font-size:64px;
                font-weight:800;
                line-height:1;
            ">
                {dcm_rating}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("1–7 SCALE")




# ---------------------------------------------------------
# RIGHT — DCM RATING SCALE
# ---------------------------------------------------------

with header_col3:

    if scale_img_path.exists():
        st.markdown(
            "<div style='height:80px;'></div>",
            unsafe_allow_html=True
        )

        st.image(
            scale_img_path,
            use_container_width=True
        )
       
# =========================================================
# NINE DCM METRICS
# =========================================================

st.header("The 9 DCM Process Metrics")


st.caption(
    "Each metric evaluates a specific defensive behavior relative "
    "to the opportunity available to the player."
)
st.caption(
    "Z-score measures how far a player's performance is from the team "
    "average in standard deviation units. Percentile shows the player's "
    "relative standing within the team. A z-score of 0 represents the "
    "team average, while a percentile of 50 represents the team median. "
    "Higher values indicate better defensive performance. When dealing with small sample sizes, " \
    "z-scores are more reliable than percentiles, which can be skewed by outliers."
)

# =========================================================
# METRIC DEFINITIONS
# =========================================================

metrics = [
    {
        
        "name": "Middle Drive Frequency",
        "count": "Middle Drives",
        "frequency": "Middle Drive Frequency",
        "z": "Middle Drive Frequency Z-Score",
        "percentile": "Middle Drive Frequency Percentile",
        "direction": "↓ better",
        "description": "Limits dribble penetration into the middle.",
    },
    {
        
        "name": "Uncontested 3 Frequency",
        "count": "Uncontested 3s",
        "frequency": "UC3 Frequency",
        "z": "UC3 Frequency Z-Score",
        "percentile": "UC3 Frequency Percentile",
        "direction": "↓ better",
        "description": "Limits open threes off the closeout.",
    },
    {
        
        "name": "Paint Touches per Poss.",
        "count": "Paint Touches",
        "frequency": "Paint Touch Per Poss.",
        "z": "Paint Touch Per Poss. Z-Score",
        "percentile": "Paint Touch Per Poss. Percentile",
        "direction": "↓ better",
        "description": "Limits touches in the paint.",
    },
    {
        
        "name": "Foul Frequency",
        "count": "Fouls",
        "frequency": "Foul Frequency",
        "z": "Foul Frequency Z-Score",
        "percentile": "Foul Frequency Percentile",
        "direction": "↓ better",
        "description": "Limits free throws and keeps the defense on the floor.",
    },
    {
        
        "name": "Deflections per Poss.",
        "count": "Deflections",
        "frequency": "Deflection Per Poss.",
        "z": "Deflection Per Poss. Z-Score",
        "percentile": "Deflection Per Poss. Percentile",
        "direction": "↑ better",
        "description": "Disrupts passes and creates turnovers.",
    },
    {
        
        "name": "Charge Frequency",
        "count": "Charges Taken",
        "frequency": "Charge Frequency",
        "z": "Charge Frequency Z-Score",
        "percentile": "Charge Frequency Percentile",
        "direction": "↑ better",
        "description": "Takes charges and stops drives.",
    },
    {
        
        "name": "Loose Ball Frequency",
        "count": "Loose Balls Recovered",
        "frequency": "Loose Ball Recovered Frequency",
        "z": "Loose Ball Recovered Frequency Z-Score",
        "percentile": "Loose Ball Recovered Frequency Percentile",
        "direction": "↑ better",
        "description": "Creates extra possessions by securing loose balls.",
    },
    {
        
        "name": "Successful Boxout %",
        "count": "Successful Boxouts",
        "frequency": "Successful Boxout Frequency",
        "z": "Successful Boxout Frequency Z-Score",
        "percentile": "Successful Boxout Frequency Percentile",
        "direction": "↑ better",
        "description": "Executes boxouts to prevent second chances.",
    },
    {
        
        "name": "O-Board Allowed Frequency",
        "count": "O-Boards Allowed",
        "frequency": "OBoard Allowed Frequency",
        "z": "OBoard Allowed Frequency Z-Score",
        "percentile": "OBoard Allowed Frequency Percentile",
        "direction": "↓ better",
        "description": "Limits offensive rebounds given up.",
    },
]


# =========================================================
# BUILD METRIC TABLE
# =========================================================

metric_rows = []

for metric in metrics:

    frequency_value = player[metric["frequency"]]
    z_value = player[metric["z"]]
    percentile_value = player[metric["percentile"]]

    # Format frequency based on the type of metric
    if metric["name"] == "Successful Boxout %":
        frequency_display = f"{frequency_value:.1%}"
    else:
        frequency_display = f"{frequency_value:.2f}"

    metric_rows.append(
        {
            "DCM Metric": metric["name"],
            #"Count": int(player[metric["count"]]),
            "Frequency": frequency_display,
            "Z-Score": f"{z_value:+.2f}",
            "Percentile": f"{percentile_value:.0f}",
            "Direction": metric["direction"],
        }
    )

metric_table = pd.DataFrame(metric_rows)


# =========================================================
# DISPLAY TABLE
# =========================================================

st.dataframe(
    metric_table,
    use_container_width=True,
    hide_index=True,
    column_config={

        "DCM Metric": st.column_config.TextColumn(
            width="large"
        ),
        "Count": st.column_config.NumberColumn(
            width="small"
        ),
        "Frequency": st.column_config.TextColumn(
            width="medium"
        ),
        "Z-Score": st.column_config.TextColumn(
            width="small"
        ),
        "Percentile": st.column_config.ProgressColumn(
            min_value=0,
            max_value=100,
            format="%d",
        ),
        "Direction": st.column_config.TextColumn(
            width="small"
        ),
    },
)


st.divider()


# =========================================================
# OPPORTUNITY CONTEXT
# =========================================================

st.header("Defensive Opportunity Context")

st.caption(
    "DCM uses different opportunity denominators depending on the defensive behavior being measured."
)


col1, col2, col3 = st.columns(3)


with col1:

    st.subheader("On-Ball Opportunities")

    st.metric(
        "Opportunities",
        f"{player['On-Ball Opportunities']:.0f}",
    )

    st.write(
        """
        Times the player was the primary defender on the
        ball or was required to defend an on-ball action.
        """
    )


with col2:

    st.subheader("Defensive Possessions")

    st.metric(
        "Possessions",
        f"{player['Defensive Possessions']:.0f}",
    )

    st.write(
        """
        All opponent possessions while the player was
        on the court.
        """
    )


with col3:

    st.subheader("Boxout Opportunities")

    st.metric(
        "Opportunities",
        f"{player['Boxout Opportunities']:.0f}",
    )

    st.write(
        """
        Times the player had a defensive rebounding
        responsibility requiring a boxout.
        """
    )


st.divider()


# =========================================================
# BOXOUT DETAIL
# =========================================================

st.header("Boxout Detail")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Successful Boxouts",
        f"{player['Successful Boxouts']:.0f}",
    )

with col2:
    st.metric(
        "Missed Boxouts",
        f"{player['Missed Boxouts']:.0f}",
    )

with col3:
    st.metric(
        "O-Boards Allowed",
        f"{player['O-Boards Allowed']:.0f}",
    )