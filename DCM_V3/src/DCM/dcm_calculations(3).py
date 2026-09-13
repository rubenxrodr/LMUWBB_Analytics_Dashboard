import pandas as pd
from pathlib import Path


# ============================================================
# DCM V3 COLUMNS
# ============================================================

DCM_COLUMNS = [
    "Player",

    "Defensive Possessions",
    "On-Ball Opportunities",
    "Boxout Opportunities",

    "Middle Drives",
    "Uncontested 3s",
    "Paint Touches",
    "Fouls",
    "Deflections",
    "Charges Taken",
    "Loose Balls Recovered",
    "Successful Boxouts",
    "O-Boards Allowed",
    "Missed Boxouts",
]


# ============================================================
# CALCULATE DCM FREQUENCIES
# ============================================================

def calculate_dcm_frequencies(df):
    """
    Calculate DCM normalized metrics from counts and
    opportunities.

    The calculations use the DCM V3 denominators:

        Middle Drives / On-Ball Opportunities
        Uncontested 3s / On-Ball Opportunities

        Paint Touches / Defensive Possessions
        Fouls / Defensive Possessions
        Deflections / Defensive Possessions
        Charges Taken / Defensive Possessions
        Loose Balls Recovered / Defensive Possessions

        Successful Boxouts / Boxout Opportunities
        O-Boards Allowed / Boxout Opportunities

    No z-scores, percentiles, or DCM ratings are calculated here.
    """

    df = df.copy()

    # --------------------------------------------------------
    # MIDDLE DRIVE
    # --------------------------------------------------------

    df["Middle Drive Frequency"] = (
        df["Middle Drives"]
        / df["On-Ball Opportunities"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # UNCONTESTED 3
    # --------------------------------------------------------

    df["UC3 Frequency"] = (
        df["Uncontested 3s"]
        / df["On-Ball Opportunities"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # PAINT TOUCH
    # --------------------------------------------------------

    df["Paint Touch Per Poss."] = (
        df["Paint Touches"]
        / df["Defensive Possessions"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # FOUL
    # --------------------------------------------------------

    df["Foul Frequency"] = (
        df["Fouls"]
        / df["Defensive Possessions"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # DEFLECTION
    # --------------------------------------------------------

    df["Deflection Per Poss."] = (
        df["Deflections"]
        / df["Defensive Possessions"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # CHARGE
    # --------------------------------------------------------

    df["Charge Frequency"] = (
        df["Charges Taken"]
        / df["Defensive Possessions"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # LOOSE BALL
    # --------------------------------------------------------

    df["Loose Ball Recovered Frequency"] = (
        df["Loose Balls Recovered"]
        / df["Defensive Possessions"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # SUCCESSFUL BOXOUT
    # --------------------------------------------------------

    df["Successful Boxout Frequency"] = (
        df["Successful Boxouts"]
        / df["Boxout Opportunities"].replace(0, pd.NA)
    )

    # --------------------------------------------------------
    # O-BOARD ALLOWED
    # --------------------------------------------------------

    df["OBoard Allowed Frequency"] = (
        df["O-Boards Allowed"]
        / df["Boxout Opportunities"].replace(0, pd.NA)
    )

    return df


# ============================================================
# SEASON AGGREGATION
# ============================================================

def aggregate_season_dcm(df):
    """
    Aggregate weekly DCM counts/opportunities into one
    season-long row per player.

    Frequencies are calculated AFTER aggregation.

    This prevents an unweighted average of weekly frequencies
    from being used as the season frequency.
    """

    count_columns = [
        "Defensive Possessions",
        "On-Ball Opportunities",
        "Boxout Opportunities",

        "Middle Drives",
        "Uncontested 3s",
        "Paint Touches",
        "Fouls",
        "Deflections",
        "Charges Taken",
        "Loose Balls Recovered",
        "Successful Boxouts",
        "O-Boards Allowed",
        "Missed Boxouts",
    ]

    season = (
        df.groupby("Player", as_index=False)[count_columns]
        .sum()
    )

    season = calculate_dcm_frequencies(season)

    return season


# ============================================================
# WEEKLY DCM
# ============================================================

def calculate_weekly_dcm(df):
    """
    Calculate DCM frequencies for each weekly observation.

    The Week column is preserved.
    """

    weekly = calculate_dcm_frequencies(df)

    return weekly


# ============================================================
# SAVE SEASON DCM
# ============================================================

def save_season_dcm(
   master_file, output_file
):
    """
    Read the DCM master, aggregate the season, calculate
    frequencies, and save the season-long DCM dataset.
    """

    master_file = Path(master_file)
    output_file = Path(output_file)

    df = pd.read_csv(master_file)

    # --------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in DCM_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "DCM master is missing required columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # AGGREGATE SEASON
    # --------------------------------------------------------

    season = aggregate_season_dcm(df)
    season= season.round(3)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    season.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Season DCM saved to: {output_file}"
    )

    return season


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":


    master_file="/Users/rrodr102/Desktop/Python/DCM_V3/data/dcm/master/dcm_master.csv"
    output_file="data/dcm/master/season_dcm.csv"

     
    season_dcm = save_season_dcm(master_file,output_file)

    print(season_dcm)