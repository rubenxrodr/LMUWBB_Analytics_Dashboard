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
    Convert possession Duration from M:SS.s format to seconds.

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
# FOUR FACTORS
# ============================================================

def calculate_four_factors(
    fga,
    fgm,
    fta,
    tov,
    orb,
    possessions
):
    """
    Calculate the four factors for a side of the ball.

    eFG% = (FGM + 0.5 * 3PM) / FGA
    TOV% = TOV / Possessions
    ORB% = ORB / Possessions
    FTR  = FTA / FGA

    Returns:
        eFG%
        TOV%
        ORB%
        FTR
    """

    efg = safe_div(
        fgm,
        fga
    )

    tov_rate = safe_div(
        tov,
        possessions
    )

    orb_rate = safe_div(
        orb,
        possessions
    )

    ftr = safe_div(
        fta,
        fga
    )

    return efg, tov_rate, orb_rate, ftr


# ============================================================
# LINEUP DATA
# ============================================================

def calculate_lineups(
    input_file,
    output_file,
    notes=None
):
    """
    Create lineup-level data from the possession master.

    Parameters
    ----------
    input_file : str
        Path to possession_master.csv.

    output_file : str
        Path where lineup data will be saved.

    notes : list, optional
        Values from the Notes column to include.

        Example:
            notes=["vid1", "vid2"]

        If None, all possessions are included.

    Notes
    -----
    Lineup analysis only uses completed possessions.

    Unlike DCM[4], incomplete possessions are NOT retained.
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
    # GROUP BY LINEUP
    # ========================================================

    lineup_rows = []

    for lineup, lineup_df in df.groupby(
        "HeightSortedLineup"
    ):

        # ----------------------------------------------------
        # OFFENSE
        # ----------------------------------------------------

        off = lineup_df[
            lineup_df["Side"] == "Offense"
        ]

        off_poss = len(off)

        off_min = (
            off["DurationSeconds"].sum() / 60
        )

        off_pts = off["PTS"].sum()

        off_fga = off["FGA"].sum()
        off_fgm = off["FGM"].sum()

        off_3pa = off["3PA"].sum()
        off_3pm = off["3PM"].sum()

        off_fta = off["FTA"].sum()
        off_tov = off["TOV"].sum()
        off_orb = off["ORB"].sum()

        off_scores = (
            off["PTS"] > 0
        ).sum()

        # ----------------------------------------------------
        # DEFENSE
        # ----------------------------------------------------

        defense = lineup_df[
            lineup_df["Side"] == "Defense"
        ]

        def_poss = len(defense)

        def_min = (
            defense["DurationSeconds"].sum() / 60
        )

        def_pts = defense["PTS"].sum()

        def_fga_allowed = defense["FGA"].sum()
        def_fgm_allowed = defense["FGM"].sum()

        def_3pa_allowed = defense["3PA"].sum()
        def_3pm_allowed = defense["3PM"].sum()

        def_fta_allowed = defense["FTA"].sum()
        def_tov_forced = defense["TOV"].sum()
        def_orb_allowed = defense["ORB"].sum()

        def_stops = (
            defense["PTS"] == 0
        ).sum()

        # ----------------------------------------------------
        # EXPOSURE
        # ----------------------------------------------------

        total_poss = (
            off_poss +
            def_poss
        )

        minutes = (
            off_min +
            def_min
        )

        # ----------------------------------------------------
        # FOUR FACTORS — OFFENSE
        # ----------------------------------------------------

        o_eFG, o_TOV, o_ORB, o_FTR = (
            calculate_four_factors(
                off_fga,
                off_fgm,
                off_fta,
                off_tov,
                off_orb,
                off_poss
            )
        )

        # ----------------------------------------------------
        # FOUR FACTORS — DEFENSE
        # ----------------------------------------------------

        d_eFG, d_TOV, d_ORB, d_FTR = (
            calculate_four_factors(
                def_fga_allowed,
                def_fgm_allowed,
                def_fta_allowed,
                def_tov_forced,
                def_orb_allowed,
                def_poss
            )
        )

        # ----------------------------------------------------
        # RATINGS
        # ----------------------------------------------------

        off_ppp = safe_div(
            off_pts,
            off_poss
        )

        def_ppp = safe_div(
            def_pts,
            def_poss
        )

        ortg = (
            off_ppp * 100
        )

        drtg = (
            def_ppp * 100
        )

        net_rtg = (
            ortg -
            drtg
        )

        # ----------------------------------------------------
        # PLUS / MINUS
        # ----------------------------------------------------

        plus_minus = (
            off_pts -
            def_pts
        )

        pm_p40 = safe_div(
            plus_minus * 40,
            minutes
        )

        # ----------------------------------------------------
        # STOP / SCORE
        # ----------------------------------------------------

        stop_rate = safe_div(
            def_stops,
            def_poss
        )

        score_rate = safe_div(
            off_scores,
            off_poss
        )

        # ----------------------------------------------------
        # RAW COLUMNS
        # ----------------------------------------------------

        raw = {
            "2FGA": off["2FGA"].sum(),
            "2FGM": off["2FGM"].sum(),
            "3PA": off["3PA"].sum(),
            "3PM": off["3PM"].sum(),
            "FTA": off["FTA"].sum(),
            "FTM": off["FTM"].sum(),
            "TOV": off["TOV"].sum(),
            "ORB": off["ORB"].sum(),

            "FGA": off_fga,
            "FGM": off_fgm,

            "2FGA Allowed": defense["2FGA"].sum(),
            "2FGM Allowed": defense["2FGM"].sum(),
            "3PA Allowed": def_3pa_allowed,
            "3PM Allowed": def_3pm_allowed,
            "FTA Allowed": def_fta_allowed,
            "FTM Allowed": defense["FTM"].sum(),
            "TOV Forced": def_tov_forced,
            "O-Boards Allowed": def_orb_allowed,

            "FGA Allowed": def_fga_allowed,
            "FGM Allowed": def_fgm_allowed,

            "Points For": off_pts,
            "Points Against": def_pts,
        }

        # ----------------------------------------------------
        # LINEUP ROW
        # ----------------------------------------------------

        row = {
            "Lineup": lineup,

            # Exposure
            "Minutes": minutes,
            "Off Min": off_min,
            "Def Min": def_min,
            "Total Possessions": total_poss,
            "Off Poss": off_poss,
            "Def Poss": def_poss,

            # Overall performance
            "PM_p40": pm_p40,
            "Net_RTG": net_rtg,
            "Off PPP": off_ppp,
            "Def PPP": def_ppp,
            "ORTG": ortg,
            "DRTG": drtg,
            "Plus_Minus": plus_minus,

            # Offensive four factors
            "O_eFG%": o_eFG,
            "O_TOV%": o_TOV,
            "O_ORB%": o_ORB,
            "O_FTR": o_FTR,

            # Defensive four factors
            "D_eFG%": d_eFG,
            "D_TOV%": d_TOV,
            "D_ORB%": d_ORB,
            "D_FTR": d_FTR,

            # Outcome
            "Stop Rate": stop_rate,
            "Score Rate": score_rate,
            "Stops": def_stops,
            "Scores": off_scores,

            # Raw
            **raw,
        }

        lineup_rows.append(row)

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    lineup_df = pd.DataFrame(
        lineup_rows
    )

    if lineup_df.empty:
        print("No lineup data generated.")
        return None

    # ========================================================
    # TEAM BASELINES
    # ========================================================
    #
    # These are calculated from the SAME filtered,
    # completed-possession dataset used above.
    #
    # This gives us the team context needed for:
    #
    #     rel_PM_p40
    #     rel_Off_RTG
    #     rel_Def_RTG
    #     rel_Net_RTG
    #
    # ========================================================

    team_off = df[
        df["Side"] == "Offense"
    ]

    team_def = df[
        df["Side"] == "Defense"
    ]

    team_off_poss = len(team_off)
    team_def_poss = len(team_def)

    team_off_min = (
        team_off["DurationSeconds"].sum() / 60
    )

    team_def_min = (
        team_def["DurationSeconds"].sum() / 60
    )

    team_minutes = (
        team_off_min +
        team_def_min
    )

    team_pts_for = (
        team_off["PTS"].sum()
    )

    team_pts_against = (
        team_def["PTS"].sum()
    )

    team_off_rtg = (
        safe_div(
            team_pts_for,
            team_off_poss
        ) * 100
    )

    team_def_rtg = (
        safe_div(
            team_pts_against,
            team_def_poss
        ) * 100
    )

    team_net_rtg = (
        team_off_rtg -
        team_def_rtg
    )

    team_plus_minus = (
        team_pts_for -
        team_pts_against
    )

    team_pm_p40 = safe_div(
        team_plus_minus * 40,
        team_minutes
    )

    # ========================================================
    # RELATIVE METRICS
    # ========================================================

    lineup_df["rel_PM_p40"] = (
        lineup_df["PM_p40"] -
        team_pm_p40
    )

    lineup_df["rel_Off_RTG"] = (
        lineup_df["ORTG"] -
        team_off_rtg
    )

    lineup_df["rel_Def_RTG"] = (
        lineup_df["DRTG"] -
        team_def_rtg
    )

    lineup_df["rel_Net_RTG"] = (
        lineup_df["Net_RTG"] -
        team_net_rtg
    )

    # ========================================================
    # TEAM BASELINE COLUMNS
    # ========================================================
    #
    # Retain these so every lineup row can be interpreted
    # against the team context.
    #
    # ========================================================

    lineup_df["Team Minutes"] = team_minutes
    lineup_df["Team Plus_Minus"] = team_plus_minus
    lineup_df["Team Off Poss"] = team_off_poss
    lineup_df["Team Def Poss"] = team_def_poss
    lineup_df["Team Total Possessions"] = (
        team_off_poss +
        team_def_poss
    )
    lineup_df["Team ORTG"] = team_off_rtg
    lineup_df["Team DRTG"] = team_def_rtg
    lineup_df["Team Net_RTG"] = team_net_rtg
    lineup_df["Team PM_p40"] = team_pm_p40

    # ========================================================
    # COLUMN ORDER
    # ========================================================

    primary_columns = [
        "Lineup",

        "Minutes",
        "Off Min",
        "Def Min",
        "Total Possessions",
        "Off Poss",
        "Def Poss",

        "PM_p40",
        "Net_RTG",
        "Off PPP",
        "Def PPP",
        "ORTG",
        "DRTG",
        "Plus_Minus",

        "rel_PM_p40",
        "rel_Off_RTG",
        "rel_Def_RTG",
        "rel_Net_RTG",

        "O_eFG%",
        "O_TOV%",
        "O_ORB%",
        "O_FTR",

        "D_eFG%",
        "D_TOV%",
        "D_ORB%",
        "D_FTR",

        "Stop Rate",
        "Score Rate",
        "Stops",
        "Scores",
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

    raw_columns = [
        col
        for col in lineup_df.columns
        if col not in primary_columns
        and col not in team_columns
    ]

    lineup_df = lineup_df[
        primary_columns +
        raw_columns +
        team_columns
    ]

    # ========================================================
    # ROUND NUMERIC COLUMNS
    # ========================================================

    numeric_columns = (
        lineup_df
        .select_dtypes(
            include=["float64", "int64"]
        )
        .columns
    )

    lineup_df[numeric_columns] = (
        lineup_df[numeric_columns]
        .round(3)
    )

    # ========================================================
    # SORT
    # ========================================================

    lineup_df = (
        lineup_df
        .sort_values(
            by="Minutes",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # ========================================================
    # SAVE
    # ========================================================

    lineup_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Lineup data generated successfully."
    )

    print(
        f"Total lineups: {len(lineup_df)}"
    )

    print(
        f"Lineup data saved to: {output_file}"
    )

    return lineup_df


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
        "lineup_data.csv"
    )

    lineup_data = calculate_lineups(
        input_file=input_file,
        output_file=output_file,
        notes=None
    )
    #notes = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10'] # first 10 practices 

    if lineup_data is not None:

        print("\nLineup Data:")

        print(
            lineup_data.head(10)
        )