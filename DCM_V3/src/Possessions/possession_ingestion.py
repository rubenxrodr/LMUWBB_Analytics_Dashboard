from pathlib import Path
import re
import pandas as pd


# ============================================================
# POSSESSION V3 SCHEMA
# ============================================================

POSSESSION_COLUMNS = [
    "PossessionID",
    "Side",

    "Notes",
    "HeightSortedLineup",

    "IncompleteResult",
    "Duration",

    "2FGA",
    "2FGM",
    "3PA",
    "3PM",

    "FTA",
    "FTM",

    "TOV",
    "ORB",
    "FOUL",
    "PTS",

    "Team_DefPoss",

    "Team_AllowMiddle",
    "Team_AllowPaintTouch",
    "Team_AllowUC3",
    "Team_AllowOBoard",
    "Team_Deflections",
]

MASTER_COLUMNS = [
    "Week",
] + POSSESSION_COLUMNS


# ============================================================
# VALIDATION
# ============================================================

def validate_possession_schema(df):
    """
    Confirm that a parsed possession file contains all
    required DCM V3 possession columns.
    """

    missing_columns = [
        column
        for column in POSSESSION_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Possession file is missing required columns: "
            f"{missing_columns}"
        )


# ============================================================
# WEEK EXTRACTION
# ============================================================

def extract_week(input_file):
    """
    Extract the week number from a filename.

    Examples:
        possession_week_01.csv -> 1
        possession_week_02.csv -> 2
        possession_week_12.csv -> 12
    """

    filename = Path(input_file).stem.lower()

    match = re.search(
        r"week[_-]?(\d+)",
        filename,
    )

    if not match:
        raise ValueError(
            f"Could not determine week from filename: "
            f"{input_file}"
        )

    return int(match.group(1))


# ============================================================
# INGESTION
# ============================================================

def ingest_possession_week(
    input_file,
    master_file,
):
    """
    Add one parsed weekly possession file to the
    season-long possession master.

    Responsibilities:
        1. Read parsed weekly possession data
        2. Validate the V3 schema
        3. Extract the week number
        4. Add Week to every possession
        5. Append to the master
        6. Deduplicate
        7. Sort
        8. Save the updated master

    This function does NOT:
        - calculate possessions
        - calculate PPP
        - calculate DCM frequencies
        - calculate DCM scores
        - calculate lineup statistics
        - perform L1/L4 analysis
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

    validate_possession_schema(weekly)

    # Keep only the standardized possession columns.
    weekly = weekly[POSSESSION_COLUMNS].copy()

    # --------------------------------------------------------
    # IDENTIFY WEEK
    # --------------------------------------------------------

    week = extract_week(input_file)

    weekly.insert(
        0,
        "Week",
        week,
    )

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

        missing_columns = [
            column
            for column in MASTER_COLUMNS
            if column not in master.columns
        ]

        if missing_columns:
            raise ValueError(
                "Existing possession master is missing "
                f"required columns: {missing_columns}"
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
    # IMPORTANT:
    #
    # We do not currently have a PossessionID in the parsed
    # output. Therefore, we cannot safely identify individual
    # duplicate possessions.
    #
    # For now, duplicates are identified using the complete
    # possession row.
    #
    # This prevents an identical possession from being added
    # twice while allowing distinct possessions to remain.
    # --------------------------------------------------------

    master = master.drop_duplicates(
        subset=["Week", "PossessionID"],
        keep="last",
)

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    master = master.sort_values(
        by=["Week","PossessionID"],
        ascending=[True, True]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [

        "2FGA",
        "2FGM",
        "3PA",
        "3PM",

        "FTA",
        "FTM",

        "TOV",
        "ORB",
        "FOUL",
        "PTS",
    ]

    for column in numeric_columns:
        master[column] = pd.to_numeric(
            master[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # BOOLEAN COLUMNS
    # --------------------------------------------------------

    boolean_columns = [
        "IncompleteResult",
        "Team_DefPoss",
        "Team_AllowMiddle",
        "Team_AllowPaintTouch",
        "Team_AllowUC3",
        "Team_AllowOBoard",
        "Team_Deflections",
    ]

    for column in boolean_columns:
        master[column] = (
            master[column]
            .fillna(False)
            .astype(bool)
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    master.to_csv(
        master_file,
        index=False,
    )

    print(
        f"Week {week} possession data ingested successfully."
    )

    print(
        f"Total possessions in week {week}: {len(weekly)}"
    )
    print(
        f"Total possessions in master: {len(master)}"
    )

    print(
        f"Possession master saved to: {master_file}"
    )

    return master


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    ingest_possession_week(
        input_file=(
            "/Users/rrodr102/Desktop/Python/DCM_V3/data/possession/parsed/parsed_possessions_week02.csv"
        ),
        master_file = (
            "/Users/rrodr102/Desktop/Python/DCM_V3/data/possession/master/possession_master.csv"
        )
    )