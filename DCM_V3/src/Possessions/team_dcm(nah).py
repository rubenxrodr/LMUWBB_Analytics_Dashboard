import pandas as pd
from pathlib import Path


# ============================================================
# TEAM DCM — L1
# ============================================================

REQUIRED_COLUMNS = [
    "Side",
    "PTS",
    "IncompleteResult",

    "Team_AllowMiddle",
    "Team_AllowPaintTouch",
    "Team_AllowUC3",
    "Team_Deflections",
]


# ============================================================
# VALIDATION
# ============================================================

def validate_schema(df):
    """
    Confirm that the possession master contains the fields
    required to calculate the L1 Team DCM Overview.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Possession master is missing required columns: "
            f"{missing_columns}"
        )


# ============================================================
# TEAM DCM L1 CALCULATION
# ============================================================

def calculate_team_dcm(df):
    """
    Calculate the L1 Team DCM Overview.

    L1 is based exclusively on defensive possessions.

    Required metrics:

        PPP
        Stop Rate
        Middle Possession Occurrence
        UC3 Possession Occurrence
        Paint Possession Occurrence
        Deflection Possession Occurrence

    ------------------------------------------------------------
    STOP DEFINITION
    ------------------------------------------------------------

    A stop is a completed defensive possession in which the
    opponent does not score.

        Stop =
            Side == "Defense"
            AND IncompleteResult == False
            AND PTS == 0

    An incomplete possession is NOT considered a stop, even
    when PTS == 0.

    ------------------------------------------------------------
    DENOMINATOR
    ------------------------------------------------------------

    All L1 occurrence metrics use:

        Defensive Possessions

    as their denominator.
    """

    validate_schema(df)

    df = df.copy()

    # ========================================================
    # DEFENSIVE POSSESSIONS
    # ========================================================

    defensive = df[
        df["Side"] == "Defense"
    ].copy()

    defensive_possessions = len(defensive)

    if defensive_possessions == 0:
        return pd.DataFrame([{
            "Defensive Possessions": 0,
            "PPP": pd.NA,
            "Stop Rate": pd.NA,
            "Middle Possession Occurrence": pd.NA,
            "UC3 Possession Occurrence": pd.NA,
            "Paint Possession Occurrence": pd.NA,
            "Deflection Possession Occurrence": pd.NA,
        }])

    # ========================================================
    # POINTS ALLOWED
    # ========================================================

    points_allowed = defensive["PTS"].sum()

    # ========================================================
    # PPP
    # ========================================================

    ppp = (
        points_allowed
        / defensive_possessions
    )

    # ========================================================
    # STOPS
    # ========================================================
    #
    # A stop requires:
    #
    #   1. Defensive possession
    #   2. Complete result
    #   3. Zero points allowed
    #
    # Incomplete possessions are therefore excluded from
    # the numerator.
    # ========================================================

    stops = defensive[
        (~defensive["IncompleteResult"])
        & (defensive["PTS"] == 0)
    ]

    stop_count = len(stops)

    stop_rate = (
        stop_count
        / defensive_possessions
    )

    # ========================================================
    # POSSESSION OCCURRENCES
    # ========================================================

    middle_occurrences = (
        defensive["Team_AllowMiddle"].sum()
    )

    uc3_occurrences = (
        defensive["Team_AllowUC3"].sum()
    )

    paint_occurrences = (
        defensive["Team_AllowPaintTouch"].sum()
    )

    deflection_occurrences = (
        defensive["Team_Deflections"].sum()
    )

    # ========================================================
    # OCCURRENCE RATES
    # ========================================================

    middle_occurrence = (
        middle_occurrences
        / defensive_possessions
    )

    uc3_occurrence = (
        uc3_occurrences
        / defensive_possessions
    )

    paint_occurrence = (
        paint_occurrences
        / defensive_possessions
    )

    deflection_occurrence = (
        deflection_occurrences
        / defensive_possessions
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    output = pd.DataFrame([{
        "Defensive Possessions": defensive_possessions,

        "PPP": ppp,

        "Stop Rate": stop_rate,

        "Middle Possession Occurrence":
            middle_occurrence,

        "UC3 Possession Occurrence":
            uc3_occurrence,

        "Paint Possession Occurrence":
            paint_occurrence,

        "Deflection Possession Occurrence":
            deflection_occurrence,
    }])

    return output


# ============================================================
# LOAD + CALCULATE
# ============================================================

def calculate_from_master(input_file , output_file):
 

    """
    Read the possession master, calculate the L1 Team DCM
    Overview, and save the result.
    """

    input_file = Path(input_file)
    output_file = Path(output_file)

    df = pd.read_csv(input_file)

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    team_dcm = calculate_team_dcm(df)

    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------
    team_dcm = team_dcm.round(3)
    
    team_dcm.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Team DCM L1 saved to: {output_file}"
    )

    return team_dcm


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    input_file= "/Users/rrodr102/Desktop/Python/DCM_V3/data/possession/master/possession_master.csv" 
    output_file=  "/Users/rrodr102/Desktop/Python/DCM_V3/data/dcm/possession/team_dcm_l1.csv"
    
    team_dcm = calculate_from_master(input_file, output_file)

    print("\nL1 Team DCM Overview:")
    print(team_dcm.to_string(index=False))