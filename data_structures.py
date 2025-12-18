from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Person:
    name: str
    age_years: int
    age_months: int
    gender: str
    spoken_languages: List[str]

@dataclass
class Counselor(Person):
    pair_with: List[str]
    avoid_with: List[str]
    morning_group: Optional[int]
    afternoon_group: Optional[int]

    monday_start: str
    monday_end: str
    monday_lunch: str

    tuesday_start: str
    tuesday_end: str
    tuesday_lunch: str

    wednesday_start: str
    wednesday_end: str
    wednesday_lunch: str

    thursday_start: str
    thursday_end: str
    thursday_lunch: str

    friday_start: str
    friday_end: str
    friday_lunch: str

    preferred_age_group: str
    years_of_experience: int
    is_speciality: bool
    works_summer_school: bool
    works_summer_camp: bool
    
@dataclass
class Camper(Person):
    grade: str = ""
    siblings: list[str] = field(default_factory=list)
    friends: list[str] = field(default_factory=list)
    attends_summer_school: bool = False
    attends_summer_camp: bool = False
