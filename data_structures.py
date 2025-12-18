from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

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
    grade: str
    pair_with: List[str]
    avoid_with: List[str]
    siblings: List[str]
    friends: List[str]
    attends_summer_school: bool
    attends_summer_camp: bool
    morning_group: Optional[int] = None
    afternoon_group: Optional[int] = None

@dataclass
class CampDataset:
    counselors: List["Counselor"] = field(default_factory=list)
    campers: List["Camper"] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.counselors) + len(self.campers)
    
    def counselor_by_name(self) -> dict[str, "Counselor"]:
        return {c.name: c for c in self.counselors}

    def camper_by_name(self) -> dict[str, "Camper"]:
        return {c.name: c for c in self.campers}


# ----------------------------
# Union-Find (hard pair_with)
# ----------------------------
class UnionFind:
    def __init__(self, items: List[str]):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1

# ----------------------------
# RBL Output types
# ----------------------------
@dataclass
class CamperRBL:
    session: str
    num_groups: int
    uf: UnionFind
    components: Dict[str, List[str]]          # root -> camper names (hard paired clusters)
    comp_domain: Dict[str, Set[int]]          # root -> valid groups
    comp_avoid: Dict[str, Set[str]]           # root -> set of other roots it cannot share a group with

@dataclass
class CounselorRBL:
    session: str
    num_groups: int
    counselor_domain: Dict[str, Set[int]]     # counselor name -> valid groups (hard only)

# ----------------------------
# RBL: build full RBL for both sessions with your group counts
# ----------------------------

def avg_domain_size(domains: dict) -> float:
    if not domains:
        return 0.0
    return sum(len(d) for d in domains.values()) / len(domains)

@dataclass
class RBLResult:
    morning_groups: int
    afternoon_groups: int
    campers_morning: CamperRBL
    campers_afternoon: CamperRBL
    counselors_morning: CounselorRBL
    counselors_afternoon: CounselorRBL

    def summary(self) -> str:
        lines = []
        lines.append("\n===RBL SUMMARY===")
        lines.append(f"Morning groups: {self.morning_groups}")
        lines.append(f"Afternoon groups: {self.afternoon_groups}")

        lines.append("")
        lines.append("Campers (Morning):")
        lines.append(f"  Components: {len(self.campers_morning.components)}")
        lines.append(f"  Avg domain size: {avg_domain_size(self.campers_morning.comp_domain):.2f}")

        lines.append("")
        lines.append("Campers (Afternoon):")
        lines.append(f"  Components: {len(self.campers_afternoon.components)}")
        lines.append(f"  Avg domain size: {avg_domain_size(self.campers_afternoon.comp_domain):.2f}")

        lines.append("")
        lines.append("Counselors (Morning):")
        lines.append(f"  Counselors: {len(self.counselors_morning.counselor_domain)}")

        lines.append("")
        lines.append("Counselors (Afternoon):")
        lines.append(f"  Counselors: {len(self.counselors_afternoon.counselor_domain)}")

        return "\n".join(lines)
