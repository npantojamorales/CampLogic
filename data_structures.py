from dataclasses import dataclass, field

@dataclass
class Person():
    name: str
    age_years: int
    age_months: int
    gender: str
    spoken_languages: list[str] = field(default_factory=list)
    pair_with: list[str] = field(default_factory=list)
    avoid_with: list[str] = field(default_factory=list)
    morning_group: int | None = None
    afternoon_group: int | None = None

@dataclass
class Counselor(Person):
    availability: dict[str, dict[str, str]] = field(default_factory=dict)
    preferred_age_group: list[str] = field(default_factory=list)
    years_of_experience: int = 0
    is_speciality: bool = False
    is_minor: bool = False
    works_summer_school: bool = False
    works_summer_camp: bool = False
    

@dataclass
class Camper(Person):
    grade: str = ""
    siblings: list[str] = field(default_factory=list)
    friends: list[str] = field(default_factory=list)
    attends_summer_school: bool = False
    attends_summer_camp: bool = False
