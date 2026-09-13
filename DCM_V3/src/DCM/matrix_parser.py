import pandas as pd


# ============================================================
# RAW MATRIX COLUMN MAPPING
# ============================================================
#
# Maps the raw DCM matrix columns to the standardized
# DCM V3 parser schema.
#
# The parser stops at:
#     - defensive events
#     - defensive opportunities
#
# It does NOT calculate:
#     - frequencies
#     - per-possession values
#     - z-scores
#     - percentiles
#     - DCM scores
#


RAW_COLUMNS = {
    "Defensive Possessions": "Defense",

    "On-Ball Opportunities": "On-Ball Opp",

    "Middle Drives": "Allow Middle",

    "Paint Touches": "Allow Paint Touch",

    "Uncontested 3s": "Allow UC 3",
    "Uncontested 3s Alt": "Allow Uncontested Three",

    "O-Boards Allowed": "Allow OBoard",

    "Loose Balls Recovered": "Loose Ball Recovered",

    "Fouls": "Foul",

    "Deflections": "Deflection",

    "Charges Taken": "Charge",

    "Successful Boxouts": "Successful Boxout",

    "Missed Boxouts": "Missed Box Out",
}


# ============================================================
# PARSER
# ============================================================

def parse_dcm_matrix(
    input_file,output_file
):
    """
    Convert a raw weekly DCM matrix into a clean weekly
    DCM player dataset.

    The parser produces:
        - defensive possessions
        - on-ball opportunities
        - boxout opportunities
        - nine DCM event counts

    The parser does NOT calculate:
        - frequencies
        - per-possession values
        - z-scores
        - percentiles
        - DCM ratings

    Those calculations belong to later layers of the DCM
    pipeline.
    """

    # --------------------------------------------------------
    # READ RAW MATRIX
    # --------------------------------------------------------

    df = pd.read_csv(input_file)

    # The first column of the raw matrix contains player names.
    player_column = df.columns[0]

    df = df.rename(columns={player_column: "Player"})

    # --------------------------------------------------------
    # TEAM DEFENSIVE POSSESSIONS
    # --------------------------------------------------------
    #
    # The first row of the raw matrix contains the team-level
    # Live value. This is used as the true defensive possession
    # count for the weekly matrix.
    #
    # It is NOT summed across players.
    #
    # Individual player defensive possessions are retained
    # below.
    # --------------------------------------------------------

    team_def_poss = pd.to_numeric(
        df.iloc[0][RAW_COLUMNS["Defensive Possessions"]],
        errors="coerce",
    )

    print("Team defensive possessions:", team_def_poss)

    # --------------------------------------------------------
    # PLAYER DATA
    # --------------------------------------------------------
    #
    # The first row is the team summary row and should not be
    # treated as an individual player.
    # --------------------------------------------------------

    players = df.iloc[1:].copy()

    output = pd.DataFrame()

    output["Player"] = players["Player"]

    # --------------------------------------------------------
    # OPPORTUNITIES
    # --------------------------------------------------------

    output["Defensive Possessions"] = pd.to_numeric(
        players[RAW_COLUMNS["Defensive Possessions"]],
        errors="coerce",
    ).fillna(0)

    output["On-Ball Opportunities"] = pd.to_numeric(
        players[RAW_COLUMNS["On-Ball Opportunities"]],
        errors="coerce",
    ).fillna(0)

    # --------------------------------------------------------
    # DCM EVENT COUNTS
    # --------------------------------------------------------

    output["Middle Drives"] = pd.to_numeric(
        players[RAW_COLUMNS["Middle Drives"]],
        errors="coerce",
    ).fillna(0)

    output["Paint Touches"] = pd.to_numeric(
        players[RAW_COLUMNS["Paint Touches"]],
        errors="coerce",
    ).fillna(0)

    # Sarah's UC3 is represented by two raw matrix columns.
    output["Uncontested 3s"] = (
        pd.to_numeric(
            players[RAW_COLUMNS["Uncontested 3s"]],
            errors="coerce",
        ).fillna(0)
        +
        pd.to_numeric(
            players[RAW_COLUMNS["Uncontested 3s Alt"]],
            errors="coerce",
        ).fillna(0)
    )

    output["O-Boards Allowed"] = pd.to_numeric(
        players[RAW_COLUMNS["O-Boards Allowed"]],
        errors="coerce",
    ).fillna(0)

    output["Loose Balls Recovered"] = pd.to_numeric(
        players[RAW_COLUMNS["Loose Balls Recovered"]],
        errors="coerce",
    ).fillna(0)

    output["Fouls"] = pd.to_numeric(
        players[RAW_COLUMNS["Fouls"]],
        errors="coerce",
    ).fillna(0)

    output["Deflections"] = pd.to_numeric(
        players[RAW_COLUMNS["Deflections"]],
        errors="coerce",
    ).fillna(0)

    output["Charges Taken"] = pd.to_numeric(
        players[RAW_COLUMNS["Charges Taken"]],
        errors="coerce",
    ).fillna(0)

    output["Successful Boxouts"] = pd.to_numeric(
        players[RAW_COLUMNS["Successful Boxouts"]],
        errors="coerce",
    ).fillna(0)

    output["Missed Boxouts"] = pd.to_numeric(
        players[RAW_COLUMNS["Missed Boxouts"]],
        errors="coerce",
    ).fillna(0)
    # --------------------------------------------------------
    # BOXOUT OPPORTUNITIES
    # --------------------------------------------------------
    #
    # Boxout Opportunities are defined as:
    #
    #     Successful Boxouts + Missed Boxouts
    #
    # This is an opportunity count, not a frequency.
    # --------------------------------------------------------

    missed_boxouts = pd.to_numeric(
        players[RAW_COLUMNS["Missed Boxouts"]],
        errors="coerce",
    ).fillna(0)

    output["Boxout Opportunities"] = (
        output["Successful Boxouts"] + missed_boxouts
    )

    # --------------------------------------------------------
    # FINAL COLUMN ORDER
    # --------------------------------------------------------

    columns = [
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

    output = output[columns]

    # --------------------------------------------------------
    # CLEAN NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [
        column
        for column in output.columns
        if column != "Player"
    ]

    output[numeric_columns] = output[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    # Counts/opportunities should be integers.
    output[numeric_columns] = output[numeric_columns].fillna(0).astype(int)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output.to_csv(output_file, index=False)

    print(
        f"DCM boxscore saved to {output_file}"
    )

    return output


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    #change the week num in the function definition 
    dcm_boxscore = parse_dcm_matrix(
        input_file="/Users/rrodr102/Desktop/Python/DCM_V3/Data/dcm/raw/DCM_week02.csv",
        output_file="/Users/rrodr102/Desktop/Python/DCM_V3/Data/dcm/parsed/DCM_boxscore_week02.csv",
    )

    print(dcm_boxscore)