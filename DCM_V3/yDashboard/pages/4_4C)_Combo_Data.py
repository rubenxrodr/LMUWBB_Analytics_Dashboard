# =========================================================
# 4_C — COMBO DATA
# =========================================================

from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# PATHS
# =========================================================

PAGE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = PAGE_DIR.parent

DATA_PATH = (
    DASHBOARD_DIR.parent
    / "data"
    / "lineup"
    / "combo_data.csv"
)

ASSETS_DIR = DASHBOARD_DIR / "assets"


# =========================================================
# PLAYER INFO
# =========================================================

PLAYER_INFO = {
    "#0 Sarah Deng":        {"name": "Sarah Deng",        "jerseynum": 0,  "initial": "SD",  "height": 66},
    "#2 Mari Somvichian":   {"name": "Mari Somvichian",   "jerseynum": 2,  "initial": "MS",  "height": 64},
    "#3 Danae Powell":      {"name": "Danae Powell",      "jerseynum": 3,  "initial": "DP",  "height": 68},
    "#4 Allison Clarke":    {"name": "Allison Clarke",    "jerseynum": 4,  "initial": "AC",  "height": 70},
    "#6 Shawnee Nordstrom": {"name": "Shawnee Nordstrom", "jerseynum": 6,  "initial": "SN",  "height": 66},
    "#7 Ana Milanovic":     {"name": "Ana Milanovic",     "jerseynum": 7,  "initial": "AM7", "height": 74},
    "#8 Shanayka Ismar":    {"name": "Shanayka Ismar",    "jerseynum": 8,  "initial": "SI",  "height": 69},
    "10 Lova Lagerlid":     {"name": "Lova Lagerlid",     "jerseynum": 10, "initial": "LL",  "height": 72},
    "#11 Erica Finney":     {"name": "Erica Finney",      "jerseynum": 11, "initial": "EF",  "height": 73},
    "#13 Ivana Krajina":    {"name": "Ivana Krajina",     "jerseynum": 13, "initial": "IK",  "height": 71},
    "#22 Ali'a Matavao":    {"name": "Ali'a Matavao",     "jerseynum": 22, "initial": "A'M",  "height": 72},
    "#24 Kayla Jones":      {"name": "Kayla Jones",       "jerseynum": 24, "initial": "KJ",  "height": 75},
    "#30 Janay Brantley":   {"name": "Janay Brantley",    "jerseynum": 30, "initial": "JB",  "height": 73},
    "#55 Maya Hernandez":   {"name": "Maya Hernandez",    "jerseynum": 55, "initial": "MH",  "height": 78},
}


# =========================================================
# INITIAL → FULL NAME
# =========================================================

initial_to_name = {
    info["initial"]: info["name"]
    for info in PLAYER_INFO.values()
}


def combo_to_full_names(combo):
    """
    Convert:
        DP-KJ

    into:
        Danae Powell + Kayla Jones
    """

    initials = combo.split("-")

    names = [
        initial_to_name.get(initial, initial)
        for initial in initials
    ]

    return " + ".join(names)


def combo_players(combo):
    """
    Return the individual full names contained in a combo.
    """

    initials = combo.split("-")

    return [
        initial_to_name.get(initial, initial)
        for initial in initials
    ]


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(DATA_PATH)

# Remove * prefixes from column names
df.columns = df.columns.str.lstrip("*")


# =========================================================
# CLEAN / ADD DISPLAY COLUMNS
# =========================================================

df["Combo"] = df["Player Combo"].apply(combo_to_full_names)

df["Combo Size"] = df["Player Combo"].str.count("-") + 1


# =========================================================
# PAGE HEADER
# =========================================================

st.title("Combo Performance")

st.caption(
    "Evaluate how player combinations perform when sharing the floor."
)


# =========================================================
# MINIMUM POSSESSION FILTER
# =========================================================

max_possessions = int(df["Total Possessions"].max())

min_possessions = st.slider(
    "Minimum Possessions",
    min_value=0,
    max_value=max_possessions,
    value=min(20, max_possessions),
    step=1,
)


# =========================================================
# FILTER COMBOS
# =========================================================

filtered_df = df[
    df["Total Possessions"] >= min_possessions
].copy()


two_player = filtered_df[
    filtered_df["Combo Size"] == 2
].copy()


four_player = filtered_df[
    filtered_df["Combo Size"] == 4
].copy()


# =========================================================
# TABLE PREPARATION
# =========================================================

TABLE_COLUMNS = [
    "Combo",
    "Minutes",
    "Total Possessions",
    "rel_PM_p40",
    "ORTG",
    "DRTG",
    "Net_RTG",
]


def prepare_table(data):
    """
    Prepare coach-facing combo table.
    """

    table = data[TABLE_COLUMNS].copy()

    table["Minutes"] = table["Minutes"].round(0)
    table["Total Possessions"] = table["Total Possessions"].round(0)

    for col in [
        "rel_PM_p40",
        "ORTG",
        "DRTG",
        "Net_RTG",
    ]:
        table[col] = table[col].round(0)

    return table


# =========================================================
# REL PM/40 COLOR SCALE
# =========================================================

def rel_pm_color(value):
    """
    Red → Yellow → Green color scale centered at 0.
    """

    if pd.isna(value):
        return ""

    # Clamp to a reasonable range
    value = max(-100, min(100, float(value)))

    # Negative: red → yellow
    if value < 0:

        ratio = (value + 100) / 100

        red = 255
        green = int(255 * ratio)
        blue = 0

    # Positive: yellow → green
    else:

        ratio = value / 100

        red = int(255 * (1 - ratio))
        green = 255
        blue = 0

    return (
        f"background-color: rgb({red}, {green}, {blue});"
        f"color: black;"
        f"font-weight: 700;"
    )


def style_combo_table(table):
    """
    Apply visual styling only to rel_PM_p40.
    """

    return (
        table.style
        .map(
            rel_pm_color,
            subset=["rel_PM_p40"],
        )
        .format(
            {
                "Minutes": "{:.0f}",
                "Total Possessions": "{:.0f}",
                "rel_PM_p40": "{:.0f}",
                "ORTG": "{:.0f}",
                "DRTG": "{:.0f}",
                "Net_RTG": "{:.0f}",
            }
        )
    )


# =========================================================
# TABLE DISPLAY
# =========================================================

def display_combo_table(data):

    if data.empty:
        st.info(
            "No combos meet the minimum possession requirement."
        )
        return

    table = prepare_table(data)

    table = style_combo_table(table)

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Combo": st.column_config.TextColumn(
                "Combo",
                width="large",
            ),
            "Minutes": st.column_config.NumberColumn(
                "Minutes",
                format="%.0f",
            ),
            "Total Possessions": st.column_config.NumberColumn(
                "Possessions",
                format="%.0f",
            ),
            "rel_PM_p40": st.column_config.NumberColumn(
                "rel PM/40",
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
    )


# =========================================================
# 2-PLAYER COMBOS
# =========================================================

st.divider()

st.header("2-Player Combos")


# ---------------------------------------------------------
# TOP 2-PLAYER COMBOS
# ---------------------------------------------------------

st.subheader("Top 2-Player Combos")

top_two = (
    two_player
    .sort_values("rel_PM_p40", ascending=False)
    .head(10)
)

display_combo_table(top_two)


# ---------------------------------------------------------
# WORST 2-PLAYER COMBOS
# ---------------------------------------------------------

st.subheader("Worst 2-Player Combos")

worst_two = (
    two_player
    .sort_values("rel_PM_p40", ascending=True)
    .head(10)
)

display_combo_table(worst_two)


# =========================================================
# 4-PLAYER COMBOS
# =========================================================

st.divider()

st.header("4-Player Combos")


# ---------------------------------------------------------
# TOP 4-PLAYER COMBOS
# ---------------------------------------------------------

st.subheader("Top 4-Player Combos")

top_four = (
    four_player
    .sort_values("rel_PM_p40", ascending=False)
    .head(10)
)

display_combo_table(top_four)


# ---------------------------------------------------------
# WORST 4-PLAYER COMBOS
# ---------------------------------------------------------

st.subheader("Worst 4-Player Combos")

worst_four = (
    four_player
    .sort_values("rel_PM_p40", ascending=True)
    .head(10)
)

display_combo_table(worst_four)









# =========================================================
# HELPER — DISPLAY SELECTED COMBO
# =========================================================

def display_selected_combo(combo_df, selected_combo):
    combo = combo_df[
        combo_df["Player Combo"] == selected_combo
    ].iloc[0]

    # -----------------------------------------------------
    # COMBO HEADER
    # -----------------------------------------------------

    players = combo_players(selected_combo)

    image_cols = st.columns(len(players))

    for col, player_name in zip(image_cols, players):

        image_path = ASSETS_DIR / f"{player_name}.webp"

        with col:

            if image_path.exists():
                st.image(
                    str(image_path),
                    width=130,
                )
            else:
                st.write(player_name)

    st.subheader(
        combo_to_full_names(selected_combo)
    )

    st.caption(
        f"{combo['Minutes']:.0f} minutes • "
        f"{combo['Total Possessions']:.0f} possessions"
    )

    # -----------------------------------------------------
    # IMPACT
    # -----------------------------------------------------

    st.markdown("### Impact")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "rel PM/40",
            f"{combo['rel_PM_p40']:.0f}",
        )

    with metric2:
        st.metric(
            "On-Off PM/40",
            f"{combo['On-Off_PMp40']:.0f}",
        )

    with metric3:
        st.metric(
            "Net RTG",
            f"{combo['Net_RTG']:.0f}",
        )

    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    st.markdown("### Performance")

    perf1, perf2 = st.columns(2)

    with perf1:
        st.metric(
            "ORTG",
            f"{combo['ORTG']:.0f}",
        )

    with perf2:
        st.metric(
            "DRTG",
            f"{combo['DRTG']:.0f}",
        )


# =========================================================
# HELPER — FIND CANONICAL COMBO
# =========================================================

def find_combo_by_players(df, selected_initials):
    """
    Find the actual Player Combo string in the dataframe,
    regardless of the order supplied by the builder.

    The returned string remains in the original
    height-sorted format from the dataset.
    """

    selected_set = set(selected_initials)

    for combo_string in df["Player Combo"]:

        combo_set = set(combo_string.split("-"))

        if combo_set == selected_set:
            return combo_string

    return None


# =========================================================
# 2-PLAYER COMBOS
# =========================================================

st.divider()
st.header("2-Player Combos")

combo_2p = two_player.copy()

# ---------------------------------------------------------
# MINIMUM POSSESSION FILTER
# ---------------------------------------------------------

min_poss_2p = st.slider(
    "Minimum possessions",
    min_value=0,
    max_value=int(combo_2p["Total Possessions"].max()),
    value=15,
    step=1,
    key="combo_2p_min_poss",
)

eligible_2p = combo_2p[
    combo_2p["Total Possessions"] >= min_poss_2p
].copy()


if eligible_2p.empty:

    st.info(
        "No 2-player combos meet the minimum possession requirement."
    )

else:

    # -----------------------------------------------------
    # BUILD PLAYER LIST
    # -----------------------------------------------------

    player_initials_2p = set()

    for combo_string in eligible_2p["Player Combo"]:

        for initial in combo_string.split("-"):

            if initial in initial_to_name:
                player_initials_2p.add(initial)

    anchor_players_2p = sorted(
        initial_to_name[p]
        for p in player_initials_2p
    )

    # -----------------------------------------------------
    # ANCHOR
    # -----------------------------------------------------

    anchor_2p = st.selectbox(
        "Choose an anchor",
        anchor_players_2p,
        key="combo_2p_anchor",
    )

    anchor_initial_2p = next(
        (
            info["initial"]
            for info in PLAYER_INFO.values()
            if info["name"] == anchor_2p
        ),
        None,
    )

    # -----------------------------------------------------
    # FIND VALID PARTNERS
    # -----------------------------------------------------

    partner_initials_2p = []

    for combo_string in eligible_2p["Player Combo"]:

        initials = combo_string.split("-")

        if anchor_initial_2p in initials:

            for initial in initials:

                if initial != anchor_initial_2p:
                    partner_initials_2p.append(initial)

    partner_players_2p = sorted(
        {
            initial_to_name[p]
            for p in partner_initials_2p
            if p in initial_to_name
        }
    )

    # -----------------------------------------------------
    # PARTNER
    # -----------------------------------------------------

    if not partner_players_2p:

        st.info(
            "No qualifying 2-player combos with this anchor "
            "under the current minimum-possession filter."
        )

    else:

        partner_2p = st.selectbox(
            "Choose a teammate",
            partner_players_2p,
            key="combo_2p_partner",
        )

        partner_initial_2p = next(
            (
                info["initial"]
                for info in PLAYER_INFO.values()
                if info["name"] == partner_2p
            ),
            None,
        )

        # -------------------------------------------------
        # FIND ACTUAL DATASET COMBO
        # -------------------------------------------------

        selected_combo_2p = find_combo_by_players(
            eligible_2p,
            [
                anchor_initial_2p,
                partner_initial_2p,
            ],
        )

        if selected_combo_2p is not None:

            display_selected_combo(
                eligible_2p,
                selected_combo_2p,
            )


# =========================================================
# 4-PLAYER COMBOS
# =========================================================

st.divider()
st.header("4-Player Combos")

combo_4p = four_player.copy()

# ---------------------------------------------------------
# MINIMUM POSSESSION FILTER
# ---------------------------------------------------------

min_poss_4p = st.slider(
    "Minimum possessions",
    min_value=0,
    max_value=int(combo_4p["Total Possessions"].max()),
    value=15,
    step=1,
    key="combo_4p_min_poss",
)

eligible_4p = combo_4p[
    combo_4p["Total Possessions"] >= min_poss_4p
].copy()


if eligible_4p.empty:

    st.info(
        "No 4-player combos meet the minimum possession requirement."
    )

else:

    # -----------------------------------------------------
    # BUILD PLAYER LIST
    # -----------------------------------------------------

    player_initials_4p = set()

    for combo_string in eligible_4p["Player Combo"]:

        for initial in combo_string.split("-"):

            if initial in initial_to_name:
                player_initials_4p.add(initial)

    anchor_players_4p = sorted(
        initial_to_name[p]
        for p in player_initials_4p
    )

    # -----------------------------------------------------
    # ANCHOR
    # -----------------------------------------------------

    anchor_4p = st.selectbox(
        "Choose an anchor",
        anchor_players_4p,
        key="combo_4p_anchor",
    )

    anchor_initial_4p = next(
        (
            info["initial"]
            for info in PLAYER_INFO.values()
            if info["name"] == anchor_4p
        ),
        None,
    )

    # -----------------------------------------------------
    # FIND VALID TEAMMATES
    # -----------------------------------------------------

    possible_teammates_4p = set()

    for combo_string in eligible_4p["Player Combo"]:

        initials = combo_string.split("-")

        if anchor_initial_4p in initials:

            for initial in initials:

                if initial != anchor_initial_4p:
                    possible_teammates_4p.add(initial)

    teammate_players_4p = sorted(
        initial_to_name[p]
        for p in possible_teammates_4p
        if p in initial_to_name
    )

    # -----------------------------------------------------
    # TEAMMATES
    # -----------------------------------------------------

    if len(teammate_players_4p) < 3:

        st.info(
            "Not enough qualifying teammates for a 4-player "
            "combo with this anchor."
        )

    else:

        selected_teammates_4p = st.multiselect(
            "Choose 3 teammates",
            teammate_players_4p,
            max_selections=3,
            key="combo_4p_teammates",
        )

        # -------------------------------------------------
        # FIND ACTUAL DATASET COMBO
        # -------------------------------------------------

        if len(selected_teammates_4p) == 3:

            teammate_initials_4p = []

            for player_name in selected_teammates_4p:

                initial = next(
                    (
                        info["initial"]
                        for info in PLAYER_INFO.values()
                        if info["name"] == player_name
                    ),
                    None,
                )

                if initial is not None:
                    teammate_initials_4p.append(initial)

            selected_combo_4p = find_combo_by_players(
                eligible_4p,
                [anchor_initial_4p] + teammate_initials_4p,
            )

            if selected_combo_4p is not None:

                display_selected_combo(
                    eligible_4p,
                    selected_combo_4p,
                )

            else:

                st.info(
                    "That 4-player combination does not meet "
                    "the minimum possession requirement."
                )









