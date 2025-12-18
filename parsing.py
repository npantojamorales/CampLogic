import pandas as pd
import re
from data_structures import Counselor

def parse_list(value):
    """Split comma/semicolon separated strings into a list."""
    if pd.isna(value) or str(value).strip() == "":
        return []
    parts = re.split(r"[;,]", str(value))
    return [p.strip() for p in parts if p.strip()]

def parse_bool(value):
    return str(value).strip().upper() == "TRUE"

def nan_to_none(value):
    """Convert pandas NaN to Python None."""
    return None if pd.isna(value) else value

def load_counselors(csv_path: str) -> list[Counselor]:
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower()

    counselors = []

    for _, row in df.iterrows():
        # --- clean optional numeric fields ---
        morning_group = nan_to_none(row.get("morning_group"))
        afternoon_group = nan_to_none(row.get("afternoon_group"))

        if morning_group is not None:
            morning_group = int(morning_group)
        if afternoon_group is not None:
            afternoon_group = int(afternoon_group)

        # --- clean optional lunch fields ---
        wednesday_lunch = nan_to_none(row["wednesday_lunch"])
        friday_lunch = nan_to_none(row["friday_lunch"])

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
