import numpy as np
import pandas as pd


# ============================================================
# SAFE DIVISION
# ============================================================

def safe_divide(numerator, denominator):
    """
    Safely divide numerator by denominator.

    Returns 0 when denominator is 0.
    """
    if denominator == 0 or pd.isna(denominator):
        return 0.0

    return numerator / denominator


# ============================================================
# LOAD POSSESSION MASTER
# ============================================================

def load_possession_master(input_file):
    """
    Load the possession master CSV.

    One row represents one possession.
    """

    df = pd.read_csv(input_file)

    required_columns = [
        "Week",
        "PossessionID",
        "Side",
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
        "PTS",

        "Team_AllowMiddle",
        "Team_AllowPaintTouch",
        "Team_AllowUC3",
        "Team_AllowOBoard",
        "Team_Deflections",
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Possession master is missing required columns: {missing}"
        )

    return df


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(df):
    """
    Prepare possession data for 4A team overview calculations.

    Important distinction:

    - Exposure metrics use ALL possessions.
    - Outcome metrics use COMPLETE possessions only.
    - DCM[4] occurrence metrics can use incomplete possessions
      when the defensive event itself is recorded.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Normalize Side
    # --------------------------------------------------------

    df["Side"] = (
        df["Side"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # --------------------------------------------------------
    # Normalize boolean columns
    # --------------------------------------------------------

    boolean_columns = [
        "IncompleteResult",
        "Team_AllowMiddle",
        "Team_AllowPaintTouch",
        "Team_AllowUC3",
        "Team_AllowOBoard",
        "Team_Deflections",
    ]

    for col in boolean_columns:
        df[col] = df[col].fillna(False).astype(bool)

    # --------------------------------------------------------
    # Fix Duration
    # Convert to seconds
    # --------------------------------------------------------
    def parse_duration(duration):
        if pd.isna(duration):
            return 0.0

        duration = str(duration).strip()

        if duration == "":
            return 0.0

        try:
            minutes, seconds = duration.split(":")
            return (
                int(minutes) * 60
                + float(seconds)
            )
        except (ValueError, TypeError):
            return 0.0


    df["Duration"] = df["Duration"].apply(parse_duration)



    # --------------------------------------------------------
    # Numeric columns
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
        "PTS",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

  

    # --------------------------------------------------------
    # Completed possessions
    #
    # These are the only possessions used for outcome metrics.
    # --------------------------------------------------------

    df["Complete"] = ~df["IncompleteResult"]

    return df


# ============================================================
# EXPOSURE
# ============================================================

def calculate_exposure(df):
    """
    Calculate team possession and minute exposure.

    ALL possessions are included, including incomplete
    possessions.
    """

    offense = df["Side"] == "Offense"
    defense = df["Side"] == "Defense"

    offensive_possessions = offense.sum()
    defensive_possessions = defense.sum()

    offensive_minutes = (
        df.loc[offense, "Duration"].sum() / 60
    )

    defensive_minutes = (
        df.loc[defense, "Duration"].sum() / 60
    )

    total_minutes = (
        offensive_minutes +
        defensive_minutes
    )

    return {
        "Minutes": total_minutes,
        "Off Min": offensive_minutes,
        "Def Min": defensive_minutes,

        "Off Possessions": offensive_possessions,
        "Def Possessions": defensive_possessions,

        "Total Possessions": (
            offensive_possessions +
            defensive_possessions
        ),
    }


# ============================================================
# RAW COUNTS
# ============================================================

def calculate_raw_counts(df):
    """
    Calculate raw/intermediary team counts.

    These counts are retained in the final output.

    Counts are calculated separately for offense and defense
    where the distinction matters.
    """

    offense_complete = (
        (df["Side"] == "Offense") &
        (df["Complete"])
    )

    defense_complete = (
        (df["Side"] == "Defense") &
        (df["Complete"])
    )

    offense_all = df["Side"] == "Offense"
    defense_all = df["Side"] == "Defense"

    return {
        # ----------------------------------------------------
        # Offensive completed-possession counts
        # ----------------------------------------------------

        "FGM": df.loc[offense_complete, ["2FGM", "3PM"]].sum().sum(),

        "FGA": df.loc[
            offense_complete,
            ["2FGA", "3PA"]
        ].sum().sum(),

        "2FGM": df.loc[
            offense_complete,
            "2FGM"
        ].sum(),

        "2FGA": df.loc[
            offense_complete,
            "2FGA"
        ].sum(),

        "3PM": df.loc[
            offense_complete,
            "3PM"
        ].sum(),

        "3PA": df.loc[
            offense_complete,
            "3PA"
        ].sum(),

        "FTM": df.loc[
            offense_complete,
            "FTM"
        ].sum(),

        "FTA": df.loc[
            offense_complete,
            "FTA"
        ].sum(),

        "TOV": df.loc[
            offense_complete,
            "TOV"
        ].sum(),

        "ORB": df.loc[
            offense_complete,
            "ORB"
        ].sum(),

        "PTS": df.loc[
            offense_complete,
            "PTS"
        ].sum(),

        # ----------------------------------------------------
        # Defensive completed-possession counts
        #
        # These are opponent offensive events allowed.
        # ----------------------------------------------------

        "FGM Allowed": df.loc[
            defense_complete,
            ["2FGM", "3PM"]
        ].sum().sum(),

        "FGA Allowed": df.loc[
            defense_complete,
            ["2FGA", "3PA"]
        ].sum().sum(),

        "2FGM Allowed": df.loc[
            defense_complete,
            "2FGM"
        ].sum(),

        "2FGA Allowed": df.loc[
            defense_complete,
            "2FGA"
        ].sum(),

        "3PM Allowed": df.loc[
            defense_complete,
            "3PM"
        ].sum(),

        "3PA Allowed": df.loc[
            defense_complete,
            "3PA"
        ].sum(),

        "FTM Allowed": df.loc[
            defense_complete,
            "FTM"
        ].sum(),

        "FTA Allowed": df.loc[
            defense_complete,
            "FTA"
        ].sum(),

        "TOV Forced": df.loc[
            defense_complete,
            "TOV"
        ].sum(),

        "ORB Allowed": df.loc[
            defense_complete,
            "ORB"
        ].sum(),

        "PTS Allowed": df.loc[
            defense_complete,
            "PTS"
        ].sum(),

        # ----------------------------------------------------
        # Completed possessions
        # ----------------------------------------------------

        "Completed Off Poss": offense_complete.sum(),

        "Completed Def Poss": defense_complete.sum(),

        # ----------------------------------------------------
        # Raw exposure counts
        # ----------------------------------------------------

        "All Off Poss": offense_all.sum(),

        "All Def Poss": defense_all.sum(),
    }


# ============================================================
# PPP / RATINGS
# ============================================================

def calculate_outcomes(df):
    """
    Calculate team-level outcome metrics.

    IMPORTANT:
    Only COMPLETE possessions are used here.

    This includes:

    - PPP
    - ORTG
    - DRTG
    - Plus Minus
    - Plus Minus Per 40
    """

    offense = (
        (df["Side"] == "Offense") &
        (df["Complete"])
    )

    defense = (
        (df["Side"] == "Defense") &
        (df["Complete"])
    )

    o_poss = offense.sum()
    d_poss = defense.sum()

    pts_for = df.loc[offense, "PTS"].sum()
    pts_against = df.loc[defense, "PTS"].sum()

    offensive_ppp = safe_divide(
        pts_for,
        o_poss
    )

    defensive_ppp = safe_divide(
        pts_against,
        d_poss
    )

    ortg = offensive_ppp * 100
    drtg = defensive_ppp * 100
    net_rtg = ortg - drtg

    plus_minus = pts_for - pts_against

    # Minutes remain an exposure metric and therefore include
    # incomplete possessions.
    offensive_minutes = (
        df.loc[df["Side"] == "Offense", "Duration"].sum() / 60
    )

    defensive_minutes = (
        df.loc[df["Side"] == "Defense", "Duration"].sum() / 60
    )

    total_minutes = (
        offensive_minutes +
        defensive_minutes
    )

    pm_per_40 = safe_divide(
        plus_minus * 40,
        total_minutes
    )

    return {
        "Off PPP": offensive_ppp,
        "Def PPP": defensive_ppp,

        "ORTG": ortg,
        "DRTG": drtg,
        "Net_RTG": net_rtg,
        "Plus_Minus": plus_minus,
        "PM_p40": pm_per_40,
    }


# ============================================================
# FOUR FACTORS
# ============================================================

def calculate_four_factors(df):
    """
    Calculate all eight Four Factors.

    Four offensive factors:
        O_eFG%
        O_TOV%
        O_ORB%
        O_FTR

    Four defensive factors:
        D_eFG%
        D_TOV%
        D_ORB%
        D_FTR

    ONLY complete possessions are used.
    """

    offense = (
        (df["Side"] == "Offense") &
        (df["Complete"])
    )

    defense = (
        (df["Side"] == "Defense") &
        (df["Complete"])
    )

    # --------------------------------------------------------
    # OFFENSE
    # --------------------------------------------------------

    o_fgm = df.loc[offense, "2FGM"].sum() + df.loc[offense, "3PM"].sum()

    o_fga = df.loc[offense, "2FGA"].sum() + df.loc[offense, "3PA"].sum()

    o_3pm = df.loc[offense, "3PM"].sum()

    o_tov = df.loc[offense, "TOV"].sum()

    o_orb = df.loc[offense, "ORB"].sum()

    o_fta = df.loc[offense, "FTA"].sum()

    o_poss = offense.sum()

    o_efg = safe_divide(
        o_fgm + (0.5 * o_3pm),
        o_fga
    )

    o_tov_pct = safe_divide(
        o_tov,
        o_poss
    )

    o_orb_pct = safe_divide(
        o_orb,
        o_poss
    )

    o_ftr = safe_divide(
        o_fta,
        o_fga
    )

    # --------------------------------------------------------
    # DEFENSE
    #
    # These describe what the opponent did against us.
    # --------------------------------------------------------

    d_fgm = df.loc[defense, "2FGM"].sum() + df.loc[defense, "3PM"].sum()

    d_fga = df.loc[defense, "2FGA"].sum() + df.loc[defense, "3PA"].sum()

    d_3pm = df.loc[defense, "3PM"].sum()

    d_tov_forced = df.loc[defense, "TOV"].sum()

    d_orb_allowed = df.loc[defense, "ORB"].sum()

    d_fta_allowed = df.loc[defense, "FTA"].sum()

    d_poss = defense.sum()

    d_efg = safe_divide(
        d_fgm + (0.5 * d_3pm),
        d_fga
    )

    d_tov_pct = safe_divide(
        d_tov_forced,
        d_poss
    )

    d_orb_pct = safe_divide(
        d_orb_allowed,
        d_poss
    )

    d_ftr = safe_divide(
        d_fta_allowed,
        d_fga
    )

    return {
        "O_eFG%": o_efg,
        "O_TOV%": o_tov_pct,
        "O_ORB%": o_orb_pct,
        "O_FTR": o_ftr,

        "D_eFG%": d_efg,
        "D_TOV%": d_tov_pct,
        "D_ORB%": d_orb_pct,
        "D_FTR": d_ftr,
    }


# ============================================================
# STOP / SCORE
# ============================================================

def calculate_stop_score(df):
    """
    Calculate defensive Stop Rate and offensive Score Rate.

    STOP:
        Side == Defense
        AND IncompleteResult == False
        AND PTS == 0

    SCORE:
        Side == Offense
        AND IncompleteResult == False
        AND PTS > 0

    Both metrics use COMPLETE possessions only.
    """

    offense = (
        (df["Side"] == "Offense") &
        (df["Complete"])
    )

    defense = (
        (df["Side"] == "Defense") &
        (df["Complete"])
    )

    stop = (
        defense &
        (df["PTS"] == 0)
    )

    score = (
        offense &
        (df["PTS"] > 0)
    )

    defensive_possessions = defense.sum()
    offensive_possessions = offense.sum()

    stops = stop.sum()
    scores = score.sum()

    stop_rate = safe_divide(
        stops,
        defensive_possessions
    )

    score_rate = safe_divide(
        scores,
        offensive_possessions
    )

    return {
        "Stops": stops,
        "Scores": scores,

        "Stop Rate": stop_rate,
        "Score Rate": score_rate,
    }


# ============================================================
# DCM[4] POSSESSION OCCURRENCE
# ============================================================

def calculate_dcm_occurrence(df):
    """
    Calculate defensive DCM[4] possession occurrence.

    DCM[4]:
        Middle
        UC3
        Paint
        Deflection

    Unlike outcome metrics, incomplete defensive possessions
    can contribute here when the event itself is recorded.

    Denominator:
        All defensive possessions.

    This treats the possession as valid defensive exposure even
    when the final possession outcome is incomplete.
    """

    defense = df["Side"] == "Defense"

    defensive_possessions = defense.sum()

    middle = (
        defense &
        df["Team_AllowMiddle"]
    )

    uc3 = (
        defense &
        df["Team_AllowUC3"]
    )

    paint = (
        defense &
        df["Team_AllowPaintTouch"]
    )

    deflection = (
        defense &
        df["Team_Deflections"]
    )

    middle_count = middle.sum()
    uc3_count = uc3.sum()
    paint_count = paint.sum()
    deflection_count = deflection.sum()

    return {
        "Middle": middle_count,
        "Middle Possession Occurrence": safe_divide(
            middle_count,
            defensive_possessions
        ),

        "UC3": uc3_count,
        "UC3 Possession Occurrence": safe_divide(
            uc3_count,
            defensive_possessions
        ),

        "Paint Touch": paint_count,
        "Paint Touch Possession Occurrence": safe_divide(
            paint_count,
            defensive_possessions
        ),

        "Deflection": deflection_count,
        "Deflection Possession Occurrence": safe_divide(
            deflection_count,
            defensive_possessions
        ),
    }


# ============================================================
# TEAM OVERVIEW
# ============================================================

def calculate_team_overview(input_file, output_file):
    """
    Calculate the 4A Team Overview from the possession master.

    The output contains one row representing the team.

    Metric rules:

    EXPOSURE
        All possessions, including incomplete possessions.

    OUTCOME
        Complete possessions only.

    DCM[4] OCCURRENCE
        Defensive possessions, including incomplete possessions
        when the defensive event is recorded.
    """

    df = load_possession_master(input_file)

    df = prepare_data(df)

    exposure = calculate_exposure(df)

    raw_counts = calculate_raw_counts(df)

    outcomes = calculate_outcomes(df)

    four_factors = calculate_four_factors(df)

    stop_score = calculate_stop_score(df)

    dcm_occurrence = calculate_dcm_occurrence(df)

    # --------------------------------------------------------
    # Combine all calculations
    # --------------------------------------------------------

    result = {}

    result.update(exposure)

    result.update(outcomes)

    result.update(four_factors)

    result.update(stop_score)

    result.update(dcm_occurrence)

    result.update(raw_counts)

    output = pd.DataFrame([result])

    # --------------------------------------------------------
    # Final column ordering
    #
    # Headline metrics first.
    # Raw/intermediary counts at the back.
    # --------------------------------------------------------

    headline_columns = [
        # Identification
        "Team",

        # Exposure
        "Minutes",
        "Off Min",
        "Def Min",
        "Total Possessions",
       "Completed Off Poss",
        "Completed Def Poss",

        # Outcomes
        "PM_p40",
        "Net_RTG",
        "Off PPP",
        "Def PPP",
        "ORTG",
        "DRTG",
        "Plus_Minus",
       

        # Four Factors
        "O_eFG%",
        "O_TOV%",
        "O_ORB%",
        "O_FTR",

        "D_eFG%",
        "D_TOV%",
        "D_ORB%",
        "D_FTR",

        # Stop / Score
        "Stop Rate",
        "Score Rate",
        "Stops",
        "Scores",

        # DCM[4]
        "Middle Possession Occurrence",
        "UC3 Possession Occurrence",
        "Paint Touch Possession Occurrence",
        "Deflection Possession Occurrence",
    ]

    raw_columns = [
        # Explicit exposure counts
        "All Off Poss",
        "All Def Poss",

        # Offensive raw counts
        "FGM",
        "FGA",
        "2FGM",
        "2FGA",
        "3PM",
        "3PA",
        "FTM",
        "FTA",
        "TOV",
        "ORB",
        "PTS",

        # Defensive raw counts
        "FGM Allowed",
        "FGA Allowed",
        "2FGM Allowed",
        "2FGA Allowed",
        "3PM Allowed",
        "3PA Allowed",
        "FTM Allowed",
        "FTA Allowed",
        "TOV Forced",
        "ORB Allowed",
        "PTS Allowed",

        # DCM[4] raw event counts
        "Middle",
        "UC3",
        "Paint Touch",
        "Deflection",

       
    ]

    output["Team"] = "TEAM"

    output = output[
        headline_columns + raw_columns
    ]

    # --------------------------------------------------------
    # Round numeric columns
    # --------------------------------------------------------

    numeric_columns = output.select_dtypes(
        include=["float64", "int64"]
    ).columns

    output[numeric_columns] = (
        output[numeric_columns]
        .round(3)
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output.to_csv(
        output_file,
        index=False
    )

    print(
        "4A Team Overview calculated successfully."
    )

    print(
        f"Team overview saved to: {output_file}"
    )

    return output


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
        "team_overview_4a.csv"
    )

    team_overview = calculate_team_overview(
        input_file,
        output_file
    )

    print("\n4A Team Overview:")
    print(
        team_overview
    )