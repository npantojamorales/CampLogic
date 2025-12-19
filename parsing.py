from data_structures import Counselor, Camper      # custom data classes
import pandas as pd                                # used to read and work with CSV files
import re                                          # used for splitting strings with regex

# -------------------------------------------------------------------
# Helper parsing functions
# -------------------------------------------------------------------

def parse_list(value):
    """Convert a comma/semicolon separated strings into a clean list."""
    if pd.isna(value) or str(value).strip() == "":
        return []
    parts = re.split(r"[;,]", str(value))
    return [p.strip() for p in parts if p.strip()]

def parse_bool(value):
    """Convert common string/number representations into a boolean"""
    
    # if the value is already a boolean, return it directly
    if isinstance(value, bool):
        return value

    # normalize the value and check against "true" values
    return str(value).strip().upper() in {"TRUE", "1", "YES"}

def nan_to_none(value):
    """Convert pandas NaN to Python None."""
    return None if pd.isna(value) else value

# -------------------------------------------------------------------
# Load counselors from CSV
# -------------------------------------------------------------------

def load_counselors(csv_path: str) -> list[Counselor]:
    """Read a counselor CSV file and return a list of Counselor objects"""

    # read the CSV into a pandas dataframe
    df = pd.read_csv(csv_path)

    # normalize column names (lowercase and remove extra spaces)
    df.columns = df.columns.str.strip().str.lower()

    counselors = []

    # loop through each row of the CSV
    for _, row in df.iterrows():
        
        # clean optional numeric fields by converting NaN to None
        morning_group = nan_to_none(row.get("morning_group"))
        afternoon_group = nan_to_none(row.get("afternoon_group"))

        # if group exists, convert them into integers
        if morning_group is not None:
            morning_group = int(morning_group)
        if afternoon_group is not None:
            afternoon_group = int(afternoon_group)

        # --- clean optional lunch fields ---
        wednesday_lunch = nan_to_none(row["wednesday_lunch"])
        friday_lunch = nan_to_none(row["friday_lunch"])

        # create a Counselor object using cleaned data
        counselors.append(
            Counselor(
                name=row["name"],
                age_years=int(row["age_years"]),
                age_months=int(row["age_months"]),
                gender=row["gender"],
                spoken_languages=parse_list(row["spoken_languages"]),

                pair_with=parse_list(row["pair_with"]),
                avoid_with=parse_list(row["avoid_with"]),
                morning_group=morning_group,
                afternoon_group=afternoon_group,

                # weekly schedule
                monday_start=row["monday_start"],
                monday_end=row["monday_end"],
                monday_lunch=row["monday_lunch"],

                tuesday_start=row["tuesday_start"],
                tuesday_end=row["tuesday_end"],
                tuesday_lunch=row["tuesday_lunch"],

                wednesday_start=row["wednesday_start"],
                wednesday_end=row["wednesday_end"],
                wednesday_lunch=wednesday_lunch,

                thursday_start=row["thursday_start"],
                thursday_end=row["thursday_end"],
                thursday_lunch=row["thursday_lunch"],

                friday_start=row["friday_start"],
                friday_end=row["friday_end"],
                friday_lunch=friday_lunch,

                preferred_age_group=row["preferred_age_group"],
                years_of_experience=int(row["years_of_experience"]),
                is_speciality=parse_bool(row["is_speciality"]),
                works_summer_school=parse_bool(row["works_summer_school"]),
                works_summer_camp=parse_bool(row["works_summer_camp"]),
            )
        )

    return counselors

# -------------------------------------------------------------------
# Load campers from CSV
# -------------------------------------------------------------------

def load_campers(csv_path: str) -> list[Camper]:
    """Read a camper CSV file and return a list of Camper objects"""

    # read the CSV into a dataframe
    df = pd.read_csv(csv_path)

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    campers: list[Camper] = []

    # loop through each camper row
    for _, row in df.iterrows():

        # clean optional group assignments
        morning_group = nan_to_none(row.get("morning_group"))
        afternoon_group = nan_to_none(row.get("afternoon_group"))

        if morning_group is not None:
            morning_group = int(morning_group)
        if afternoon_group is not None:
            afternoon_group = int(afternoon_group)

        # create a Camper object
        campers.append(
            Camper(
                name=row["name"],
                age_years=int(row["age_years"]),
                age_months=int(row["age_months"]),
                gender=row["gender"],
                spoken_languages=parse_list(row["spoken_languages"]),

                grade=str(row["grade"]).strip(),
                pair_with=parse_list(row.get("pair_with")),
                avoid_with=parse_list(row.get("avoid_with")),
                siblings=parse_list(row.get("siblings")),
                friends=parse_list(row.get("friends")),

                attends_summer_school=parse_bool(row["attends_summer_school"]),
                attends_summer_camp=parse_bool(row["attends_summer_camp"]),

                morning_group=morning_group,
                afternoon_group=afternoon_group,
            )
        )

    return campers
