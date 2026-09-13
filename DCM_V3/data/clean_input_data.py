import pandas as pd 
def clean_player_names(df):
    """
    Standardize player labels in raw data.

    Jersey convention:
        #0  stays #0
        #2  -> #02
        #3  -> #03
        #4  -> #04
        #6  -> #06
        #7  -> #07
        #8  -> #08
    """

    player_name_map = {
        "#2 Mari Somvichian": "#02 Mari Somvichian",
        "#3 Danae Powell": "#03 Danae Powell",
        "#4 Allison Clarke": "#04 Allison Clarke",
        "#6 Shawnee Nordstrom": "#06 Shawnee Nordstrom",
        "#7 Ana Milanovic": "#07 Ana Milanovic",
        "#8 Shanayka Ismar": "#08 Shanayka Ismar",

        # Typo correction
        "#0 Sarah Dang": "#0 Sarah Deng",
    }

    df = df.copy()

    # Replace wherever these player labels appear
    for old_name, new_name in player_name_map.items():
        df = df.replace(old_name, new_name, regex=False)

    # Also handle player names embedded inside strings
    for old_name, new_name in player_name_map.items():
        df = df.map(
            lambda x: x.replace(old_name, new_name)
            if isinstance(x, str) else x
        )

    return df


import pandas as pd


PLAYER_NAME_MAP = {
    "#2 Mari Somvichian": "#02 Mari Somvichian",
    "#3 Danae Powell": "#03 Danae Powell",
    "#4 Allison Clarke": "#04 Allison Clarke",
    "#6 Shawnee Nordstrom": "#06 Shawnee Nordstrom",
    "#7 Ana Milanovic": "#07 Ana Milanovic",
    "#8 Shanayka Ismar": "#08 Shanayka Ismar",
    # Typo Correction
    "#0 Sarah Dang": "#0 Sarah Deng",
}


def clean_dcm_raw(df):
    """
    Clean the raw DCM matrix while preserving its matrix structure.

    Normalizes duplicate jersey-number formats and combines
    duplicate player rows/columns.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # 1. First column contains the row labels
    # ---------------------------------------------------------

    row_label_col = df.columns[0]

    # Normalize row labels
    df[row_label_col] = df[row_label_col].replace(PLAYER_NAME_MAP)

    # Normalize column labels
    df = df.rename(columns=PLAYER_NAME_MAP)

    # ---------------------------------------------------------
    # 2. Combine duplicate ROWS
    # ---------------------------------------------------------

    df = df.groupby(row_label_col, sort=False).sum(numeric_only=True)

    # ---------------------------------------------------------
    # 3. Combine duplicate COLUMNS
    # ---------------------------------------------------------

    df = df.T.groupby(level=0, sort=False).sum().T

    # ---------------------------------------------------------
    # 4. Restore row labels as first column
    # ---------------------------------------------------------

    df = df.reset_index()

    return df

possession_df = pd.read_csv("data/possession/raw/possession_week02_raw.csv")
possession_df = clean_player_names(possession_df)
possession_df.to_csv("data/possession/raw/possession_week02.csv",index=False)
print("Cleaned possession data saved to data/possession/raw/possession_week02.csv")


dcm_df = pd.read_csv("data/dcm/raw/dcm_week02_raw.csv")
dcm_df = clean_dcm_raw(dcm_df)
dcm_df.to_csv("data/dcm/raw/dcm_week02.csv",index=False)
print("Cleaned DCM data saved to data/dcm/raw/dcm_week02.csv\n\n")