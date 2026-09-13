import itertools
import numpy as np
import pandas as pd


# ============================================================
# SAFE DIVISION
# ============================================================

def safe_div(numerator, denominator):
    """
    Safely divide two values.

    Returns 0 when the denominator is zero.
    """
    if denominator == 0 or pd.isna(denominator):
        return 0.0

    return numerator / denominator


# ============================================================
# DURATION PARSER
# ============================================================

def parse_duration(duration):
    """
    Convert Duration from M:SS.s format to seconds.

    Examples:
        0:18.7 -> 18.7
        0:03.7 -> 3.7
        1:22.3 -> 82.3
    """

    if pd.isna(duration):
        return 0.0

    duration = str(duration).strip()

    if duration == "":
        return 0.0

    try:
        minutes, seconds = duration.split(":")
        return int(minutes) * 60 + float(seconds)

    except (ValueError, TypeError):
        return 0.0


# ============================================================
# LINEUP PLAYER PARSER
# ============================================================

def parse_lineup(lineup):
    """
    Convert a height-sorted lineup string into a list of players.

    Example:
        "MS-SN-IK-KJ-MH"

    becomes:
        ["MS", "SN", "IK", "KJ", "MH"]
    """

    if pd.isna(lineup):
        return []

    lineup = str(lineup).strip()

    if lineup == "":
        return []

    return [
        player.strip()
        for player in lineup.split("-")
        if player.strip()
    ]


# ============================================================
# CREATE COMBINATIONS
# ============================================================

def create_combos(lineup):
    """
    Create 2-player and 4-player combinations from a lineup.

    Because the possession master already stores lineups in
    height-sorted order, the resulting combinations retain
    that ordering.

    Example:
        MS-SN-IK-KJ-MH

    produces combinations such as:

        MS-SN
        MS-IK
        MS-KJ
        MS-MH
        ...
        MS-SN-IK-KJ
        MS-SN-IK-MH
        ...
    """

    players = parse_lineup(lineup)

    combos = []

    for size in [2, 4]:

        for combo in itertools.combinations(players, size):

            combos.append(
                (
                    "-".join(combo),
                    size == 2
                )
            )

    return combos


# ============================================================
# CALCULATE COMBO METRICS
# ============================================================

def calculate_combo_metrics(
    combo,
    is_two_player,
    df,
    team_metrics
):
    """
    Calculate on-court, off-court, relative, and on-off metrics
    for one player combination.

    combo:
        String representation of the combo.

    is_two_player:
        True for 2-player combinations.
        False for 4-player combinations.

    df:
        Completed possession dataframe.

    team_metrics:
        Team-level baseline metrics.
    """

    combo_players = combo.split("-")

    # ========================================================
    # IDENTIFY POSSESSIONS WHERE ENTIRE COMBO IS ON COURT
    # ========================================================

    on_court = df[
        df["LineupPlayers"].apply(
            lambda lineup:
            all(
                player in lineup
                for player in combo_players
            )
        )
    ]

    # ========================================================
    # IDENTIFY POSSESSIONS WHERE ENTIRE COMBO IS OFF COURT
    # ========================================================

    off_court = df[
        df["LineupPlayers"].apply(
            lambda lineup:
            all(
                player not in lineup
                for player in combo_players
            )
        )
    ]

    # ========================================================
    # ON-COURT
    # ========================================================

    on_offense = on_court[
        on_court["Side"] == "Offense"
    ]

    on_defense = on_court[
        on_court["Side"] == "Defense"
    ]

    on_off_poss = len(on_offense)
    on_def_poss = len(on_defense)

    on_off_min = (
        on_offense["DurationSeconds"].sum() / 60
    )

    on_def_min = (
        on_defense["DurationSeconds"].sum() / 60
    )

    on_minutes = (
        on_off_min +
        on_def_min
    )

    on_pts_for = (
        on_offense["PTS"].sum()
    )

    on_pts_against = (
        on_defense["PTS"].sum()
    )

    on_plus_minus = (
        on_pts_for -
        on_pts_against
    )

    on_ortg = (
        safe_div(
            on_pts_for,
            on_off_poss
        ) * 100
    )

    on_drtg = (
        safe_div(
            on_pts_against,
            on_def_poss
        ) * 100
    )

    on_net_rtg = (
        on_ortg -
        on_drtg
    )

    on_pm_p40 = safe_div(
        on_plus_minus * 40,
        on_minutes
    )

    # ========================================================
    # OFF-COURT
    # ========================================================

    off_offense = off_court[
        off_court["Side"] == "Offense"
    ]

    off_defense = off_court[
        off_court["Side"] == "Defense"
    ]

    off_off_poss = len(off_offense)
    off_def_poss = len(off_defense)

    off_off_min = (
        off_offense["DurationSeconds"].sum() / 60
    )

    off_def_min = (
        off_defense["DurationSeconds"].sum() / 60
    )

    off_minutes = (
        off_off_min +
        off_def_min
    )

    off_pts_for = (
        off_offense["PTS"].sum()
    )

    off_pts_against = (
        off_defense["PTS"].sum()
    )

    off_plus_minus = (
        off_pts_for -
        off_pts_against
    )

    off_ortg = (
        safe_div(
            off_pts_for,
            off_off_poss
        ) * 100
    )

    off_drtg = (
        safe_div(
            off_pts_against,
            off_def_poss
        ) * 100
    )

    off_net_rtg = (
        off_ortg -
        off_drtg
    )

    off_pm_p40 = safe_div(
        off_plus_minus * 40,
        off_minutes
    )

    # ========================================================
    # ON-OFF
    # ========================================================

    on_off = (
        on_net_rtg -
        off_net_rtg
    )

    on_off_pm_p40 = (
        on_pm_p40 -
        off_pm_p40
    )

    # ========================================================
    # RELATIVE TEAM METRICS
    # ========================================================

    rel_pm_p40 = (
        on_pm_p40 -
        team_metrics["PM_p40"]
    )

    rel_off_rtg = (
        on_ortg -
        team_metrics["ORTG"]
    )

    rel_def_rtg = (
        on_drtg -
        team_metrics["DRTG"]
    )

    rel_net_rtg = (
        on_net_rtg -
        team_metrics["Net_RTG"]
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "Player Combo": combo,
        "isTwoPlayer": is_two_player,

        "Minutes": on_minutes,
        "Off Min": on_off_min,
        "Def Min": on_def_min,

        "Off Poss": on_off_poss,
        "Def Poss": on_def_poss,
        "Total Possessions": (
            on_off_poss +
            on_def_poss
        ),

        "rel_PM_p40": rel_pm_p40,
        "On-Off_PMp40": on_off_pm_p40,

        "ORTG": on_ortg,
        "DRTG": on_drtg,
        "Net_RTG": on_net_rtg,

        "On-Off": on_off,

        "PM_p40": on_pm_p40,

        "rel_Off_RTG": rel_off_rtg,
        "rel_Def_RTG": rel_def_rtg,
        "rel_Net_RTG": rel_net_rtg,

        "Plus_Minus": on_plus_minus,

        "Off-Court PM_p40": off_pm_p40,
        "Off-Court ORTG": off_ortg,
        "Off-Court DRTG": off_drtg,
        "Off-Court Net_RTG": off_net_rtg,

        "Team Minutes": team_metrics["Minutes"],
        "Team Plus_Minus": team_metrics["Plus_Minus"],
        "Team Off Poss": team_metrics["Off Poss"],
        "Team Def Poss": team_metrics["Def Poss"],
        "Team Total Possessions": team_metrics["Total Possessions"],
        "Team ORTG": team_metrics["ORTG"],
        "Team DRTG": team_metrics["DRTG"],
        "Team Net_RTG": team_metrics["Net_RTG"],
        "Team PM_p40": team_metrics["PM_p40"],
    }


# ============================================================
# MAIN CALCULATION
# ============================================================

def calculate_combos(
    input_file,
    output_file,
    notes=None
):
    """
    Create 2-player and 4-player combo data from
    possession_master.csv.

    Parameters
    ----------
    input_file : str
        Path to possession_master.csv.

    output_file : str
        Path where combo_data.csv will be saved.

    notes : list, optional
        Values from the Notes column to include.

        Example:
            notes=["vid1", "vid2"]

        If None, all possessions are included.

    Notes
    -----
    Only completed possessions are used.

    A combo is considered ON COURT when every player in the
    combo appears in the lineup.

    A combo is considered OFF COURT when none of the players
    in the combo appears in the lineup.
    """

    # ========================================================
    # LOAD DATA
    # ========================================================

    df = pd.read_csv(input_file)

    if df.empty:
        print("No possession data found.")
        return None

    # ========================================================
    # FILTER BY NOTES
    # ========================================================

    if notes is not None:

        df = df[
            df["Notes"].astype(str).isin(
                [str(note) for note in notes]
            )
        ].copy()

    if df.empty:
        print("No possessions match the selected Notes.")
        return None

    # ========================================================
    # COMPLETED POSSESSIONS ONLY
    # ========================================================

    df = df[
        df["IncompleteResult"] == False
    ].copy()

    if df.empty:
        print("No completed possessions found.")
        return None

    # ========================================================
    # PARSE DURATION
    # ========================================================

    df["DurationSeconds"] = df["Duration"].apply(
        parse_duration
    )

    # ========================================================
    # NUMERIC COLUMNS
    # ========================================================

    numeric_columns = [
        "2FGA",
        "2FGM",
        "3PA",
        "3PM",
        "FTA",
        "FTM",
        "TOV",
        "ORB",
        "PTS",
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    # ========================================================
    # PARSE LINEUPS
    # ========================================================

    df["LineupPlayers"] = (
        df["HeightSortedLineup"]
        .apply(parse_lineup)
    )

    # ========================================================
    # TEAM METRICS
    # ========================================================

    team_offense = df[
        df["Side"] == "Offense"
    ]

    team_defense = df[
        df["Side"] == "Defense"
    ]

    team_off_poss = len(team_offense)
    team_def_poss = len(team_defense)

    team_off_min = (
        team_offense["DurationSeconds"].sum() / 60
    )

    team_def_min = (
        team_defense["DurationSeconds"].sum() / 60
    )

    team_minutes = (
        team_off_min +
        team_def_min
    )

    team_pts_for = (
        team_offense["PTS"].sum()
    )

    team_pts_against = (
        team_defense["PTS"].sum()
    )

    team_plus_minus = (
        team_pts_for -
        team_pts_against
    )

    team_ortg = (
        safe_div(
            team_pts_for,
            team_off_poss
        ) * 100
    )

    team_drtg = (
        safe_div(
            team_pts_against,
            team_def_poss
        ) * 100
    )

    team_net_rtg = (
        team_ortg -
        team_drtg
    )

    team_pm_p40 = safe_div(
        team_plus_minus * 40,
        team_minutes
    )

    team_metrics = {

        "Minutes": team_minutes,
        "Plus_Minus": team_plus_minus,

        "Off Poss": team_off_poss,
        "Def Poss": team_def_poss,

        "Total Possessions": (
            team_off_poss +
            team_def_poss
        ),

        "ORTG": team_ortg,
        "DRTG": team_drtg,
        "Net_RTG": team_net_rtg,
        "PM_p40": team_pm_p40,
    }

    # ========================================================
    # FIND ALL UNIQUE COMBOS
    # ========================================================

    combo_set = set()

    for lineup in df["HeightSortedLineup"].dropna():

        for combo, is_two_player in create_combos(
            lineup
        ):

            combo_set.add(
                (
                    combo,
                    is_two_player
                )
            )

    # ========================================================
    # CALCULATE EACH COMBO
    # ========================================================

    rows = []

    for combo, is_two_player in sorted(
        combo_set,
        key=lambda x: (
            not x[1],
            x[0]
        )
    ):

        result = calculate_combo_metrics(
            combo=combo,
            is_two_player=is_two_player,
            df=df,
            team_metrics=team_metrics
        )

        rows.append(result)

    combo_df = pd.DataFrame(rows)

    if combo_df.empty:
        print("No combo data generated.")
        return None

    # ========================================================
    # COLUMN ORDER
    # ========================================================

    columns = [

        "Player Combo",
        "isTwoPlayer",

        "Minutes",
        "Off Min",
        "Def Min",
        "Off Poss",
        "Def Poss",
        "Total Possessions",

        "rel_PM_p40",
        "On-Off_PMp40",

        "ORTG",
        "DRTG",
        "Net_RTG",

        "On-Off",

        "PM_p40",

        "rel_Off_RTG",
        "rel_Def_RTG",
        "rel_Net_RTG",

        "Plus_Minus",

        "Off-Court PM_p40",
        "Off-Court ORTG",
        "Off-Court DRTG",
        "Off-Court Net_RTG",

        "Team Minutes",
        "Team Plus_Minus",
        "Team Off Poss",
        "Team Def Poss",
        "Team Total Possessions",
        "Team ORTG",
        "Team DRTG",
        "Team Net_RTG",
        "Team PM_p40",
    ]

    combo_df = combo_df[columns]

    # ========================================================
    # ROUND NUMERIC COLUMNS
    # ========================================================

    numeric_columns = (
        combo_df
        .select_dtypes(
            include=["float64", "int64"]
        )
        .columns
    )

    combo_df[numeric_columns] = (
        combo_df[numeric_columns]
        .round(3)
    )

    # ========================================================
    # SORT
    # ========================================================

    combo_df = (
        combo_df
        .sort_values(
            by=[
                "isTwoPlayer",
                "Minutes","On-Off"
            ],
            ascending=[
                False,
                False, 
                False
            ]
        )
        .reset_index(drop=True)
    )

    # ========================================================
    # SAVE
    # ========================================================

    combo_df.to_csv(
        output_file,
        index=False
    )

    print(
        "Combo data generated successfully."
    )

    print(
        f"Total combos: {len(combo_df)}"
    )

    print(
        f"2-player combos: "
        f"{combo_df['isTwoPlayer'].sum()}"
    )

    print(
        f"4-player combos: "
        f"{(~combo_df['isTwoPlayer']).sum()}"
    )

    print(
        f"Combo data saved to: {output_file}"
    )

    return combo_df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    input_file = (
        "/Users/rrodr102/Desktop/Python/"
        "DCM_V3/data/possession/master/"
        "possession_master.csv"
    )

    output_file = (
        "/Users/rrodr102/Desktop/Python/"
        "DCM_V3/data/lineup/"
        "combo_data.csv"
    )

    combo_data = calculate_combos(
        input_file=input_file,
        output_file=output_file,
        notes=None
    )

    if combo_data is not None:

        print("\nCombo Data:")

        print(
            combo_data
            .iloc[:, :15]
        )