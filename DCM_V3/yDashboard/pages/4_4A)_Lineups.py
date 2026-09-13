import pandas as pd
import streamlit as st
from pathlib import Path
from html import escape
from textwrap import dedent
from matplotlib import cm
from matplotlib.colors import Normalize, to_hex


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Lineups | DCM Dashboard",
    layout="wide",
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LINEUP_PATH = PROJECT_ROOT / "data" / "lineup" / "lineup_data.csv"


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_lineup_data():

    df = pd.read_csv(LINEUP_PATH)

    # Remove leading * from column names.
    # This keeps the displayed dashboard names clean while
    # preserving the underlying data.
    df.columns = df.columns.str.lstrip("*")

    return df


df = load_lineup_data()


# =========================================================
# TITLE
# =========================================================

st.title("Lineup Performance")

st.markdown(
    """
    Evaluate how five-player lineups perform together across
    offensive, defensive, and overall team outcomes.
    """
)


# =========================================================
# FILTERS
# =========================================================

st.subheader("Lineup Filters")

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])


with filter_col1:

    min_minutes = st.number_input(
        "Minimum Minutes",
        min_value=0.0,
        max_value=float(df["Minutes"].max()),
        value=1.0,
        step=0.5,
    )


with filter_col2:

    min_possessions = st.number_input(
        "Minimum Possessions",
        min_value=0,
        max_value=int(df["Total Possessions"].max()),
        value=8,
        step=2,
    )


with filter_col3:

    st.markdown("**Sample Requirement**")
    st.caption(
        "Only lineups meeting both minimum thresholds are included."
    )


# Apply filters
filtered_df = df[
    (df["Minutes"] >= min_minutes)
    & (df["Total Possessions"] >= min_possessions)
].copy()


# =========================================================
# HANDLE EMPTY FILTER
# =========================================================

if filtered_df.empty:

    st.warning(
        "No lineups meet the current sample requirements. "
        "Try lowering the minimum minutes or possessions."
    )

    st.stop()


# =========================================================
# SORT
# =========================================================

filtered_df = filtered_df.sort_values(
    "rel_PM_p40",
    ascending=False
).reset_index(drop=True)


# =========================================================
# HELPER — RED / YELLOW / GREEN
# =========================================================

def rel_pm_color(value, max_abs):

    if pd.isna(value):
        return ""

    if max_abs == 0:
        return "background-color: #fff3b0;"

    normalized = (value + max_abs) / (2 * max_abs)

    cmap = cm.get_cmap("RdYlGn")
    color = to_hex(cmap(normalized))

    return f"background-color: {color};"


# =========================================================
# COLUMN SELECTOR
# =========================================================

st.subheader("Lineup Leaderboard")

# Preserve the order from lineup_data.csv
all_columns = list(filtered_df.columns)

default_columns = [
    "Lineup",
    "Minutes",
    "Total Possessions",
    "PM_p40",
    "Net_RTG",
    "ORTG",
    "DRTG",
    "rel_PM_p40",
    "rel_Off_RTG",
    "rel_Def_RTG",
    "rel_Net_RTG",
]


# Only use defaults that actually exist
default_columns = [
    col for col in default_columns
    if col in all_columns
]


selected_columns = st.multiselect(
    "Select Columns",
    options=all_columns,
    default=default_columns,
)


# Always make sure Lineup is displayed
if "Lineup" not in selected_columns:

    selected_columns = ["Lineup"] + selected_columns


display_df = filtered_df[selected_columns].copy()


# =========================================================
# COLOR SCALE
# =========================================================

if "rel_PM_p40" in display_df.columns:

    max_abs = max(
        abs(filtered_df["rel_PM_p40"].min()),
        abs(filtered_df["rel_PM_p40"].max()),
    )

    styled_df = (
        display_df.style
        .apply(
            lambda col: [
                rel_pm_color(value, max_abs)
                for value in col
            ],
            subset=["rel_PM_p40"],
        )
        .format(
            {
                col: "{:.2f}"
                for col in display_df.select_dtypes(
                    include="number"
                ).columns
            }
        )
    )

else:

    styled_df = display_df.style.format(
        {
            col: "{:.2f}"
            for col in display_df.select_dtypes(
                include="number"
            ).columns
        }
    )


st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# BEST / WORST LINEUPS
# =========================================================

st.divider()

st.subheader("Best & Worst Lineups // Later I need to make everything one decimal point")

best_col, worst_col = st.columns(2)


best_columns = [
    "Lineup",
    "Total Possessions",
    "rel_PM_p40",
    "rel_Off_RTG",
    "rel_Def_RTG",
]

best_columns = [
    col for col in best_columns
    if col in filtered_df.columns
]


best_df = (
    filtered_df[best_columns]
    .head(5)
    .copy()
)


worst_df = (
    filtered_df[best_columns]
    .tail(5)
    .sort_values(
        "rel_PM_p40",
        ascending=True
    )
    .copy()
)


# ---------------------------------------------------------
# BEST
# ---------------------------------------------------------

with best_col:

    st.markdown("### Best Lineups")

    st.dataframe(
        best_df.style.format(
            {
                "rel_PM_p40": "{:+.2f}",
                "rel_Off_RTG": "{:+.2f}",
                "rel_Def_RTG": "{:+.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------
# WORST
# ---------------------------------------------------------

with worst_col:

    st.markdown("### Worst Lineups")

    st.dataframe(
        worst_df.style.format(
            {
                "rel_PM_p40": "{:+.2f}",
                "rel_Off_RTG": "{:+.2f}",
                "rel_Def_RTG": "{:+.2f}",
            }
        ).background_gradient(
            subset=["rel_PM_p40"],
            cmap="RdYlGn",
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# SELECTED LINEUP
# =========================================================

st.divider()

st.subheader("Selected Lineup")


lineup_options = filtered_df["Lineup"].tolist()


selected_lineup = st.selectbox(
    "Choose a lineup",
    lineup_options,
)


lineup = filtered_df[
    filtered_df["Lineup"] == selected_lineup
].iloc[0]


# =========================================================
# SELECTED LINEUP — HEADER
# =========================================================

st.markdown(
    f"""
<div style="padding: 18px; border-radius: 10px; border: 1px solid rgba(128,128,128,0.25); margin-bottom: 20px;">
    <div style="font-size: 28px; font-weight: 800;">
        {escape(selected_lineup)}
    </div>
    <div style="font-size: 15px; margin-top: 5px; opacity: 0.7;">
        {lineup["Minutes"]:.2f} minutes &nbsp;•&nbsp; {int(lineup["Total Possessions"])} possessions
    </div>
</div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SELECTED LINEUP — KEY METRICS
# =========================================================

metric1, metric2, metric3 = st.columns(3)


with metric1:

    st.metric(
        "rel PM/40",
        f'{lineup["rel_PM_p40"]:+.2f}',
    )


with metric2:

    st.metric(
        "rel ORTG",
        f'{lineup["rel_Off_RTG"]:+.2f}',
    )


with metric3:

    st.metric(
        "rel DRTG",
        f'{lineup["rel_Def_RTG"]:+.2f}',
    )

# =========================================================
# SELECTED LINEUP — FOUR FACTORS
# =========================================================

st.markdown("### Four Factors")

ff_spacer1, ff_off, ff_def, ff_spacer2 = st.columns(
    [1, 2, 2, 1],
    gap="large",
)


# ---------------------------------------------------------
# OFFENSIVE FOUR FACTORS
# ---------------------------------------------------------

with ff_off:

    html = (
        f'<div style="text-align:center;">'
        f'<div style="font-size:20px;font-weight:800;margin-bottom:20px;">'
        f'Offensive Four Factors'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'eFG%'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;margin-bottom:14px;">'
        f'{lineup["O_eFG%"]:.1%}'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'TOV%'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;margin-bottom:14px;">'
        f'{lineup["O_TOV%"]:.1%}'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'ORB%'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;margin-bottom:14px;">'
        f'{lineup["O_ORB%"]:.1%}'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'FTR'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;">'
        f'{lineup["O_FTR"]:.1%}'
        f'</div>'

        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# DEFENSIVE FOUR FACTORS
# ---------------------------------------------------------

with ff_def:

    html = (
        f'<div style="text-align:center;">'
        f'<div style="font-size:20px;font-weight:800;margin-bottom:20px;">'
        f'Defensive Four Factors'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'eFG%'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;margin-bottom:14px;">'
        f'{lineup["D_eFG%"]:.1%}'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'TOV%'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;margin-bottom:14px;">'
        f'{lineup["D_TOV%"]:.1%}'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'ORB%'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;margin-bottom:14px;">'
        f'{lineup["D_ORB%"]:.1%}'
        f'</div>'

        f'<div style="font-size:16px;font-weight:700;margin-bottom:2px;">'
        f'FTR'
        f'</div>'

        f'<div style="font-size:28px;font-weight:800;">'
        f'{lineup["D_FTR"]:.1%}'
        f'</div>'

        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )