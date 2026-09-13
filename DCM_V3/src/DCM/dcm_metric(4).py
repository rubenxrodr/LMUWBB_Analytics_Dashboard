import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# DCM V3 EVENT DEFINITIONS
# ============================================================

EVENTS = {

    "Middle Drive Frequency": {
        "direction": "bad"
    },

    "UC3 Frequency": {
        "direction": "bad"
    },

    "Paint Touch Per Poss.": {
        "direction": "bad"
    },

    "Foul Frequency": {
        "direction": "bad"
    },

    "Deflection Per Poss.": {
        "direction": "good"
    },

    "Charge Frequency": {
        "direction": "good"
    },

    "Loose Ball Recovered Frequency": {
        "direction": "good"
    },

    "Successful Boxout Frequency": {
        "direction": "good"
    },

    "OBoard Allowed Frequency": {
        "direction": "bad"
    },
}


# ============================================================
# DCM WEIGHTS
# ============================================================
#
# Weight hierarchy:
#
# Tier 1: Middle Drive + Paint Touch
# Tier 2: Foul + Deflections
# Tier 3: Everything else
# ============================================================

BASE_WEIGHTS = {

    "Middle Drive Frequency": 2,

    "Paint Touch Per Poss.": 2,

    "Foul Frequency": 2,

    "Deflection Per Poss.": 1,

    "Charge Frequency": 1,

    "Loose Ball Recovered Frequency": 1,

    "UC3 Frequency": 2,

    "Successful Boxout Frequency": 1,

    "OBoard Allowed Frequency": 1,
}


# ============================================================
# CALCULATE EVENT Z-SCORES
# ============================================================

def calculate_event_z_scores(df):
    """
    Calculate Z-scores for each DCM event.

    TEAM is excluded from the population used to calculate
    the mean and standard deviation.

    For "bad" events, the Z-score sign is reversed so that
    a higher Z-score always represents a better defensive
    outcome.

    Example:

        Lower Middle Drive Frequency = better

        Therefore:
            raw Z = -1.0
            directional Z = +1.0
    """

    df = df.copy()

    players = df[
        df["Player"] != "TEAM"
    ].copy()

    for event, info in EVENTS.items():

        z_col = f"{event} Z-Score"

        mean = players[event].mean()

        std = players[event].std(
            ddof=0
        )

        if std == 0 or pd.isna(std):

            df[z_col] = 0.0

        else:

            df[z_col] = (
                df[event] - mean
            ) / std

        # ----------------------------------------------------
        # Reverse "bad" events
        # ----------------------------------------------------

        if info["direction"] == "bad":

            df[z_col] = -df[z_col]

    return df


# ============================================================
# CALCULATE DCM Z-SCORE
# ============================================================

def calculate_dcm_z(weights, data):
    """
    Calculate the weighted DCM Z-score.

    Only measurable event Z-scores are included.

    This allows a player to receive a DCM based on the
    measurable events available for that player.
    """

    dcm_scores = pd.Series(
        index=data.index,
        dtype=float,
    )

    for idx, player in data.iterrows():

        weighted_sum = 0.0
        total_weight = 0.0

        for event, weight in weights.items():

            z_col = f"{event} Z-Score"

            z = player[z_col]

            # ------------------------------------------------
            # Only include measurable metrics
            # ------------------------------------------------

            if pd.notna(z):

                weighted_sum += z * weight

                total_weight += weight

        if total_weight > 0:

            dcm_scores.loc[idx] = (
                weighted_sum / total_weight
            )

        else:

            dcm_scores.loc[idx] = np.nan

    return dcm_scores


# ============================================================
# CALCULATE DCM SCORE
# ============================================================

def calculate_dcm_score(dcm_z):
    """
    Convert DCM_Z into the final 1–7 DCM scale.

        DCM_Z = 0
            -> DCM = 4

        Each standard deviation
            -> 1.5 DCM points

    Final DCM is clipped to [1, 7].
    """

    return (
        4 + 1.5 * dcm_z
    ).clip(
        1,
        7,
    ).round(3)


# ============================================================
# CALCULATE PERCENTILES
# ============================================================

def calculate_percentiles(df):
    """
    Calculate player percentiles for DCM and each DCM event.

    TEAM is excluded from percentile calculations.

    Percentile represents the percentage of players a player
    performs better than.

    Higher is always better because the event Z-scores have
    already been directionally adjusted.
    """

    df = df.copy()

    players = df[
        df["Player"] != "TEAM"
    ].copy()

    # --------------------------------------------------------
    # DCM PERCENTILE
    # --------------------------------------------------------

    df["DCM Percentile"] = np.nan

    if len(players) > 1:

        df.loc[
            players.index,
            "DCM Percentile"
        ] = (
            players["DCM"]
            .rank(
                pct=True,
                method="average"
            )
            * 100
        )

    elif len(players) == 1:

        df.loc[
            players.index,
            "DCM Percentile"
        ] = 100.0

    # --------------------------------------------------------
    # EVENT PERCENTILES
    # --------------------------------------------------------

    for event in EVENTS:

        z_col = f"{event} Z-Score"

        percentile_col = f"{event} Percentile"

        df[percentile_col] = np.nan

        if len(players) > 1:

            df.loc[
                players.index,
                percentile_col
            ] = (
                players[z_col]
                .rank(
                    pct=True,
                    method="average"
                )
                * 100
            )

        elif len(players) == 1:

            df.loc[
                players.index,
                percentile_col
            ] = 100.0

    return df


# ============================================================
# CALCULATE DCM METRIC
# ============================================================

def calculate_dcm_metric(df):
    """
    Calculate the complete DCM metric from season DCM data.

    Steps:

        1. Calculate event Z-scores
        3. Calculate DCM_Z
        4. Calculate DCM
        5. Calculate percentiles

    TEAM is excluded from the player population used for
    Z-scores, DCM_Z, and percentiles.
    """

    df = df.copy()

    # --------------------------------------------------------
    # EVENT Z-SCORES
    # --------------------------------------------------------

    df = calculate_event_z_scores(df)

  

    # --------------------------------------------------------
    # PLAYER DATA
    # --------------------------------------------------------

    players = df[
        df["Player"] != "TEAM"
    ].copy()

    # --------------------------------------------------------
    # DCM_Z
    # --------------------------------------------------------

    players["DCM_Z"] = calculate_dcm_z(
        BASE_WEIGHTS,
        players,
    )

    # --------------------------------------------------------
    # DCM
    # --------------------------------------------------------

    players["DCM"] = calculate_dcm_score(
        players["DCM_Z"]
    )

    # Put calculated player values back into df.
    df.loc[
        players.index,
        "DCM_Z"
    ] = players["DCM_Z"]

    df.loc[
        players.index,
        "DCM"
    ] = players["DCM"]

    # --------------------------------------------------------
    # PERCENTILES
    # --------------------------------------------------------

    df = calculate_percentiles(df)

    # --------------------------------------------------------
    # ROUND NUMERIC OUTPUT
    # --------------------------------------------------------

    numeric_columns = [
        "DCM",
        "DCM_Z",
        "DCM Percentile",
    ]

    for event in EVENTS:

        numeric_columns += [
            f"{event} Z-Score",
            f"{event} Percentile",
        ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = df[column].round(3)

    return df


# ============================================================
# SAVE DCM METRIC
# ============================================================

def save_dcm_metric(
    season_dcm_file,
    output_file
):
    """
    Read season_dcm.csv, calculate the complete DCM metric,
    and save the final DCM metric dataset.
    """

    season_dcm_file = Path(
        season_dcm_file
    )

    output_file = Path(
        output_file
    )

    df = pd.read_csv(
        season_dcm_file
    )

    # --------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    required_columns = [
        "Player",
        "Defensive Possessions",
    ] + list(EVENTS.keys())

    other_columns = [col if col not in required_columns else None for col in df.columns]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Season DCM is missing required columns: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    dcm_metric = calculate_dcm_metric(
        df
    )

    # --------------------------------------------------------
    # OUTPUT COLUMN ORDER
    # --------------------------------------------------------

    output_columns = [
        # --------------------------------------------------------
        # IDENTIFIERS / DCM
        # --------------------------------------------------------

        "Player",
        "Defensive Possessions",
        "DCM",
        "DCM_Z",

        # --------------------------------------------------------
        # COUNTS / FREQUENCIES
        # --------------------------------------------------------

        "Middle Drives",
        "Middle Drive Frequency",

        "Uncontested 3s",
        "UC3 Frequency",

        "Paint Touches",
        "Paint Touch Per Poss.",

        "Fouls",
        "Foul Frequency",

        "Deflections",
        "Deflection Per Poss.",

        "Charges Taken",
        "Charge Frequency",

        "Loose Balls Recovered",
        "Loose Ball Recovered Frequency",

        "Successful Boxouts",
        "Successful Boxout Frequency",

        "O-Boards Allowed",
        "OBoard Allowed Frequency",

        "On-Ball Opportunities",
        "Boxout Opportunities",
        "Missed Boxouts",

        # --------------------------------------------------------
        # Z-SCORES
        # --------------------------------------------------------

        "Middle Drive Frequency Z-Score",
        "UC3 Frequency Z-Score",
        "Paint Touch Per Poss. Z-Score",
        "Foul Frequency Z-Score",
        "Deflection Per Poss. Z-Score",
        "Charge Frequency Z-Score",
        "Loose Ball Recovered Frequency Z-Score",
        "Successful Boxout Frequency Z-Score",
        "OBoard Allowed Frequency Z-Score",

        # --------------------------------------------------------
        # PERCENTILES
        # --------------------------------------------------------

        "Middle Drive Frequency Percentile",
        "UC3 Frequency Percentile",
        "Paint Touch Per Poss. Percentile",
        "Foul Frequency Percentile",
        "Deflection Per Poss. Percentile",
        "Charge Frequency Percentile",
        "Loose Ball Recovered Frequency Percentile",
        "Successful Boxout Frequency Percentile",
        "OBoard Allowed Frequency Percentile",
    ]
    

    dcm_metric = dcm_metric[
        output_columns
    ].copy()

    # --------------------------------------------------------
    # SORT BY DCM
    # --------------------------------------------------------

    dcm_metric = dcm_metric.sort_values(
        "DCM",
        ascending=False,
        na_position="last",
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dcm_metric.to_csv(
        output_file,
        index=False,
    )

    print(
        f"DCM metric saved to: {output_file}"
    )

    return dcm_metric


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    input_file = (
        "/Users/rrodr102/Desktop/Python/DCM_V3/"
        "data/dcm/master/season_dcm.csv"
    )

    output_file = (
        "/Users/rrodr102/Desktop/Python/DCM_V3/"
        "data/dcm/master/dcm_metric.csv"
    )

    dcm_metric = save_dcm_metric(
        input_file,
        output_file
    )

    print("\nDCM Metric:")

    print(
        dcm_metric
    )