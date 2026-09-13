
import pandas as pd


# ============================================================
# PLAYER INFO
# ============================================================

PLAYER_INFO = {
    "#0 Sarah Deng":        {"name": "Sarah Deng",        "jerseynum": 0,  "initial": "SD",  "height": 66},
    "#02 Mari Somvichian":   {"name": "Mari Somvichian",   "jerseynum": 2,  "initial": "MS",  "height": 64},
    "#03 Danae Powell":      {"name": "Danae Powell",      "jerseynum": 3,  "initial": "DP",  "height": 68},
    "#04 Allison Clarke":    {"name": "Allison Clarke",    "jerseynum": 4,  "initial": "AC",  "height": 70},
    "#06 Shawnee Nordstrom": {"name": "Shawnee Nordstrom", "jerseynum": 6,  "initial": "SN",  "height": 66},
    "#07 Ana Milanovic":     {"name": "Ana Milanovic",     "jerseynum": 7,  "initial": "AM7", "height": 74},
    "#08 Shanayka Ismar":    {"name": "Shanayka Ismar",    "jerseynum": 8,  "initial": "SI",  "height": 69},
    "#10 Lova Lagerlid":     {"name": "Lova Lagerlid",     "jerseynum": 10, "initial": "LL",  "height": 72},
    "#11 Erica Finney":     {"name": "Erica Finney",      "jerseynum": 11, "initial": "EF",  "height": 73},
    "#13 Ivana Krajina":    {"name": "Ivana Krajina",     "jerseynum": 13, "initial": "IK",  "height": 71},
    "#22 Ali'a Matavao":    {"name": "Ali'a Matavao",     "jerseynum": 22, "initial": "A'M", "height": 72},
    "#24 Kayla Jones":      {"name": "Kayla Jones",       "jerseynum": 24, "initial": "KJ",  "height": 75},
    "#30 Janay Brantley":   {"name": "Janay Brantley",    "jerseynum": 30, "initial": "JB",  "height": 73},
    "#55 Maya Hernandez":   {"name": "Maya Hernandez",    "jerseynum": 55, "initial": "MH",  "height": 78},
}


NAME_TO_INFO = {
    info["name"]: {"pid": pid, **info}
    for pid, info in PLAYER_INFO.items()
}


# ============================================================
# LINEUP
# ============================================================

def parse_export_lineup(player_string):
    """
    Convert the Player column into a height-sorted lineup.
    """

    if pd.isna(player_string):
        return ""

    players = []

    for player in str(player_string).split(","):
        player = player.strip()

        if player in PLAYER_INFO:
            info = PLAYER_INFO[player]

            players.append({
                "initial": info["initial"],
                "height": info["height"],
                "name": info["name"],
            })

    players.sort(
        key=lambda x: (x["height"], x["name"])
    )

    return "-".join(
        player["initial"]
        for player in players
    )


# ============================================================
# POSSESSION RESULT PARSER
# ============================================================

def parse_possession(result_str):
    """
    Parse Text Overlay coding.

    @ = missed 2FG
    2 = made 2FG
    # = missed 3FG
    3 = made 3FG
    1 = made FT
    ! = missed FT
    0 = foul
    8 = offensive rebound
    9 = turnover
    ) = incomplete play

    Example:
        @-8-0-!-1

    means:
        missed 2
        offensive rebound
        foul
        missed FT
        made FT
    """

    stats = {
        "2FGA": 0,
        "2FGM": 0,
        "3PA": 0,
        "3PM": 0,
        "FTA": 0,
        "FTM": 0,
        "TOV": 0,
        "ORB": 0,
        "FOUL": 0,
        "PTS": 0,
        "Incomplete": False,
    }

    if pd.isna(result_str):
        return stats

    result_str = str(result_str).strip()

    if result_str == "":
        return stats

    for event in result_str.split("-"):
        event = event.strip()

        if event == "@":
            stats["2FGA"] += 1

        elif event == "2":
            stats["2FGA"] += 1
            stats["2FGM"] += 1
            stats["PTS"] += 2

        elif event == "#":
            stats["3PA"] += 1

        elif event == "3":
            stats["3PA"] += 1
            stats["3PM"] += 1
            stats["PTS"] += 3

        elif event == "1":
            stats["FTA"] += 1
            stats["FTM"] += 1
            stats["PTS"] += 1

        elif event == "!":
            stats["FTA"] += 1

        elif event == "0":
            stats["FOUL"] += 1

        elif event == "8":
            stats["ORB"] += 1

        elif event == "9":
            stats["TOV"] += 1

        elif event == ")":
            stats["Incomplete"] = True

    return stats


# ============================================================
# SIDE PARSER
# ============================================================

def parse_side(user_tags):
    """
    Determine whether the possession is an offensive or
    defensive possession for our team.

    User Tags should contain either:
        - Offense
        - Defense

    Returns:
        "Offense"
        "Defense"
        pd.NA if neither is present
    """

    user_tags = str(user_tags)

    if "Offense" in user_tags:
        return "Offense"

    if "Defense" in user_tags:
        return "Defense"

    return pd.NA


# ============================================================
# EXPORT.CSV -> POSSESSION DATA
# ============================================================

def parse_export(
    input_file,
    output_file
):
    """
    Read Export.csv and create one clean row per possession.

    The output contains:

    - Side (Offense / Defense)
    - Notes
    - Height-sorted lineup
    - Parsed box-score result
    - Result completeness
    - Duration
    - Team defensive possession indicator
    - Team DCM defensive tags

    The parser preserves both offensive and defensive
    possessions.

    Team DCM tags are only interpreted independently of Side.
    A defensive possession does not need to contain a DCM tag.
    """

    df = pd.read_csv(input_file)

    rows = []

    for _, row in df.iterrows():

        # ----------------------------------------------------
        # PARSE RESULT
        # ----------------------------------------------------

        result = parse_possession(
            row.get("Title", "")
        )

        # ----------------------------------------------------
        # USER TAGS
        # ----------------------------------------------------

        user_tags = str(
            row.get("User Tags", "")
        )

        # ----------------------------------------------------
        # SIDE
        # ----------------------------------------------------

        side = parse_side(user_tags)

        # ----------------------------------------------------
        # BUILD POSSESSION ROW
        # ----------------------------------------------------

        rows.append({

            "PossessionID": row.get("#"),
             # ------------------------------------------------
            # ORIGINAL POSSESSION INFORMATION
            # ------------------------------------------------

            "Notes": row.get("Notes"),

            # ------------------------------------------------
            # POSSESSION DIRECTION
            # ------------------------------------------------

            "Side": side,

           

            # ------------------------------------------------
            # LINEUP
            # ------------------------------------------------

            "HeightSortedLineup": parse_export_lineup(
                row.get("Player")
            ),

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            "IncompleteResult": result["Incomplete"],
            "Duration": row.get("Duration"),

            "2FGA": result["2FGA"],
            "2FGM": result["2FGM"],

            "3PA": result["3PA"],
            "3PM": result["3PM"],

            "FTA": result["FTA"],
            "FTM": result["FTM"],

            "TOV": result["TOV"],
            "ORB": result["ORB"],
            "FOUL": result["FOUL"],
            "PTS": result["PTS"],

            # ------------------------------------------------
            # TEAM POSSESSION TYPE
            # ------------------------------------------------

            "Team_DefPoss": side == "Defense",

            # ------------------------------------------------
            # TEAM DCM TAGS
            # ------------------------------------------------

            "Team_AllowMiddle": (
                "Allow Middle" in user_tags
            ),

            "Team_AllowPaintTouch": (
                "Allow Paint Touch" in user_tags
            ),

            "Team_AllowUC3": (
                "Allow UC 3" in user_tags
            ),

            "Team_AllowOBoard": (
                "Allow O-Board" in user_tags
            ),

            "Team_Deflections": (
                "Deflection" in user_tags
            ),
        })

    # ========================================================
    # OUTPUT DATAFRAME
    # ========================================================

    output = pd.DataFrame(rows)

    # ========================================================
    # SAVE
    # ========================================================

    output.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Parsed {len(output)} possessions "
        f"to {output_file}\n"
    )

    return output


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    input_file="/Users/rrodr102/Desktop/Python/DCM_V3/data/possession/raw/possession_week02.csv"
    output_file="/Users/rrodr102/Desktop/Python/DCM_V3/data/possession/parsed/parsed_possessions_week02.csv"
    parse_export(input_file, output_file)