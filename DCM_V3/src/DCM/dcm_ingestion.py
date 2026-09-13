from pathlib import Path
import pandas as pd


# ============================================================
# DCM V3 SCHEMA
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

MASTER_COLUMNS = ["Week"] + DCM_COLUMNS


# ============================================================
# VALIDATION
# ============================================================

def validate_dcm_schema(df):
    """
    Confirm that a parsed DCM file contains the expected
    V3 columns.
    """

    missing_columns = [
        column
        for column in DCM_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "DCM file is missing required columns: "
            f"{missing_columns}"
        )


# ============================================================
# WEEK EXTRACTION
# ============================================================

def extract_week(input_file):
    """
    Extract the week number from a filename.

    Examples:
        DCM_boxscore_week1.csv -> 1
        DCM_boxscore_week_01.csv -> 1
        DCM_week12.csv -> 12
    """

    filename = Path(input_file).stem.lower()

    import re

    match = re.search(r"week[_-]?(\d+)", filename)

    if not match:
        raise ValueError(
            f"Could not determine week from filename: {input_file}"
        )

    return int(match.group(1))


# ============================================================
# INGESTION
# ============================================================

def ingest_dcm_week(
    input_file,
    master_file
):
    """
    Add one parsed weekly DCM file to the season DCM master.

    Responsibilities:
        1. Read parsed weekly DCM data
        2. Validate the V3 schema
        3. Extract the week number
        4. Add Week to every row
        5. Append to the master
        6. Remove duplicate player/week rows
        7. Save the updated master

    This function does NOT:
        - calculate frequencies
        - calculate per-possession values
        - calculate z-scores
        - calculate percentiles
        - calculate DCM scores
        - aggregate season totals
    """

    input_file = Path(input_file)
    master_file = Path(master_file)

    # --------------------------------------------------------
    # READ WEEKLY FILE
    # --------------------------------------------------------

    weekly = pd.read_csv(input_file)

    # --------------------------------------------------------
    # VALIDATE SCHEMA
    # --------------------------------------------------------

    validate_dcm_schema(weekly)

    # Keep only the standardized DCM columns.
    weekly = weekly[DCM_COLUMNS].copy()

    # --------------------------------------------------------
    # WEEK
    # --------------------------------------------------------

    week = extract_week(input_file)

    weekly.insert(0, "Week", week)

    # --------------------------------------------------------
    # CREATE MASTER DIRECTORY
    # --------------------------------------------------------

    master_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # LOAD EXISTING MASTER
    # --------------------------------------------------------

    if master_file.exists():

        master = pd.read_csv(master_file)

        # Validate existing master.
        missing_columns = [
            column
            for column in MASTER_COLUMNS
            if column not in master.columns
        ]

        if missing_columns:
            raise ValueError(
                "Existing DCM master is missing columns: "
                f"{missing_columns}"
            )

        master = master[MASTER_COLUMNS].copy()

    else:

        master = pd.DataFrame(
            columns=MASTER_COLUMNS
        )

    # --------------------------------------------------------
    # APPEND
    # --------------------------------------------------------

    master = pd.concat(
        [master, weekly],
        ignore_index=True,
    )

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------
    #
    # A player should have one parsed DCM row per week.
    #
    # If the same week is ingested again, the new weekly
    # version replaces the old one.
    # --------------------------------------------------------

    master = (
        master
        .drop_duplicates(
            subset=["Week", "Player"],
            keep="last",
        )
        .sort_values(
            ["Week", "Player"]
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [
        column
        for column in DCM_COLUMNS
        if column != "Player"
    ]

    master[numeric_columns] = (
        master[numeric_columns]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    master.to_csv(
        master_file,
        index=False,
    )

    print(
        f"Week {week} ingested successfully."
    )
    print(
        f"DCM master saved to: {master_file}"
    )

    return master


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    ingest_dcm_week(
        input_file= "/Users/rrodr102/Desktop/Python/DCM_V3/data/dcm/parsed/DCM_boxscore_week02.csv",
        master_file="data/dcm/master/dcm_master.csv",
    )