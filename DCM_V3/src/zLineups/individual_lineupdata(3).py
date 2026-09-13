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
# INDIVIDUAL DATA
# ============================================================

def calculate_individuals(
    input_file,
    output_file,
    notes=None
):
    """
    Create individual player-level data from possession_master.csv.

    Parameters
    ----------
    input_file : str
        Path to possession_master.csv.

    output_file : str
        Path where individual data will be saved.

    notes : list, optional
        Values from the Notes column to include.

        Example:
            notes=["vid1", "vid2"]

        If None, all possessions are included.

    Notes
    -----
    Individual performance data only uses completed possessions.

    A player is considered ON COURT when their initials appear
    in the HeightSortedLineup column.

    On-Off:
        On-Court Net_RTG - Off-Court Net_RTG

    On-Off_PMp40:
        On-Court PM_p40 - Off-Court PM_p40
    """

    # ========================================================
    # LOAD POSSESSION MASTER
    # ========================================================

    df = pd.read_csv(input_file)

    if df.empty:
        print("No possession data found.")
        return None

    # ========================================================
    # FILTER BY NOTES / PRACTICE
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
    # ONLY COMPLETED POSSESSIONS
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
    # POSSESSION-LEVEL DERIVED VALUES
    # ========================================================

    df["FGA"] = (
        df["2FGA"] +
        df["3PA"]
    )

    df["FGM"] = (
        df["2FGM"] +
        df["3PM"]
    )

    # ========================================================
    # IDENTIFY ALL PLAYERS
    # ========================================================
    #
    # HeightSortedLineup has the form:
    #
    #     MS-SN-IK-KJ-MH
    #
    # Build the player list from every lineup appearing
    # in the selected possession data.
    #
    # ========================================================

    players = set()

    for lineup in df["HeightSortedLineup"].dropna():

        for player in str(lineup).split("-"):

            player = player.strip()

            if player:
                players.add(player)

    players = sorted(players)

    # ========================================================
    # CALCULATE INDIVIDUAL ON-COURT DATA
    # ========================================================

    rows = []

    for player in players:

        # ----------------------------------------------------
        # ON COURT
        # ----------------------------------------------------

        on_court = df[
            df["HeightSortedLineup"]
            .fillna("")
            .str.split("-")
            .apply(lambda lineup: player in lineup)
        ]

        # ----------------------------------------------------
        # OFF COURT
        # ----------------------------------------------------

        off_court = df[
            ~df["HeightSortedLineup"]
            .fillna("")
            .str.split("-")
            .apply(lambda lineup: player in lineup)
        ]

        # ====================================================
        # ON-COURT METRICS
        # ====================================================

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

        # ====================================================
        # OFF-COURT METRICS
        # ====================================================

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

        # ====================================================
        # ON-OFF
        # ====================================================

        on_off = (
            on_net_rtg -
            off_net_rtg
        )

        on_off_pm_p40 = (
            on_pm_p40 -
            off_pm_p40
        )

        # ====================================================
        # RELATIVE METRICS
        # ====================================================
        #
        # Team baselines are calculated later from the same
        # filtered completed-possession dataset.
        #
        # Temporarily calculate the team values below.
        #
        # ====================================================

        rows.append({

            "Player": player,

            # Exposure
            "Minutes": on_minutes,
            "Off Min": on_off_min,
            "Def Min": on_def_min,
            "Off Poss": on_off_poss,
            "Def Poss": on_def_poss,
            "Total Possessions": (
                on_off_poss +
                on_def_poss
            ),

            # On-court performance
            "Plus_Minus": on_plus_minus,
            "PM_p40": on_pm_p40,
            "ORTG": on_ortg,
            "DRTG": on_drtg,
            "Net_RTG": on_net_rtg,

            # Off-court values
            "Off-Court PM_p40": off_pm_p40,
            "Off-Court ORTG": off_ortg,
            "Off-Court DRTG": off_drtg,
            "Off-Court Net_RTG": off_net_rtg,

            # On-Off
            "On-Off": on_off,
            "On-Off_PMp40": on_off_pm_p40,

        })



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
        "#22 Ali'a Matavao":    {"name": "Ali'a Matavao",     "jerseynum": 22, "initial": "A'M", "height": 72},
        "#24 Kayla Jones":      {"name": "Kayla Jones",       "jerseynum": 24, "initial": "KJ",  "height": 75},
        "#30 Janay Brantley":   {"name": "Janay Brantley",    "jerseynum": 30, "initial": "JB",  "height": 73},
        "#55 Maya Hernandez":   {"name": "Maya Hernandez",    "jerseynum": 55, "initial": "MH",  "height": 78},
    }

    # Map initials to full names
    initial_to_name = {
        info.get("initial"): info.get("name")
        for info in PLAYER_INFO.values()
        if info.get("initial") is not None
    }

    # Replace Player initials in rows with full names when available
    for row in rows:
        p = row.get("Player")
        if p in initial_to_name:
            row["Player"] = initial_to_name[p]






    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    individual_df = pd.DataFrame(rows)

    if individual_df.empty:
        print("No individual data generated.")
        return None

    # ========================================================
    # TEAM BASELINES
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

    # ========================================================
    # RELATIVE METRICS
    # ========================================================

    individual_df["rel_PM_p40"] = (
        individual_df["PM_p40"] -
        team_pm_p40
    )

    individual_df["rel_Off_RTG"] = (
        individual_df["ORTG"] -
        team_ortg
    )

    individual_df["rel_Def_RTG"] = (
        individual_df["DRTG"] -
        team_drtg
    )

    individual_df["rel_Net_RTG"] = (
        individual_df["Net_RTG"] -
        team_net_rtg
    )

    # ========================================================
    # TEAM BASELINE COLUMNS
    # ========================================================

    individual_df["Team Minutes"] = team_minutes
    individual_df["Team Plus_Minus"] = team_plus_minus
    individual_df["Team Off Poss"] = team_off_poss
    individual_df["Team Def Poss"] = team_def_poss
    individual_df["Team Total Possessions"] = (
        team_off_poss +
        team_def_poss
    )
    individual_df["Team ORTG"] = team_ortg
    individual_df["Team DRTG"] = team_drtg
    individual_df["Team Net_RTG"] = team_net_rtg
    individual_df["Team PM_p40"] = team_pm_p40

    # ========================================================
    # COLUMN ORDER
    # ========================================================


    primary_columns = [

        "Player",

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
    ]

    team_columns = [

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

    other_columns = [
        col
        for col in individual_df.columns
        if col not in primary_columns
        and col not in team_columns
    ]

    individual_df = individual_df[
        primary_columns +
        other_columns +
        team_columns
    ]

    # ========================================================
    # ROUND NUMERIC COLUMNS
    # ========================================================

    numeric_columns = (
        individual_df
        .select_dtypes(
            include=["float64", "int64"]
        )
        .columns
    )

    individual_df[numeric_columns] = (
        individual_df[numeric_columns]
        .round(3)
    )

    # ========================================================
    # SORT
    # ========================================================

    individual_df = (
        individual_df
        .sort_values(
            by="On-Off",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # ========================================================
    # SAVE
    # ========================================================

    individual_df.to_csv(
        output_file,
        index=False
    )

    print(
        "Individual data generated successfully."
    )

    print(
        f"Total players: {len(individual_df)}"
    )

    print(
        f"Individual data saved to: {output_file}"
    )

    return individual_df


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
        "individual_lineupdata2.csv"
    )

    individual_data = calculate_individuals(
        input_file=input_file,
        output_file=output_file,
        notes=None
    )

    if individual_data is not None:

        print("\nIndividual Data:")

        print(
            individual_data
        .iloc[:, :14]
        )