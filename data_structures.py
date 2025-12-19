from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

# ================================================
# Base data structures
# ================================================

@dataclass
class Person:
    """
    Base class shared by Campers and Counselors. 
    Contains common demographic information.
    """
    name: str
    age_years: int
    age_months: int
    gender: str
    spoken_languages: List[str]

# ================================================
# Counselor data structure
# ================================================

@dataclass
class Counselor(Person):
    """
    Represents a counselor and all scheduling
    and pairing constraints. Inherits basic
    personal info from Person.
    """

    # pairing constraints
    pair_with: List[str]
    avoid_with: List[str]

    # optional pre-assigned groups
    morning_group: Optional[int]
    afternoon_group: Optional[int]

    # weekly schedule availability
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

    # experience and role preferences
    preferred_age_group: str
    years_of_experience: int
    is_speciality: bool
    works_summer_school: bool
    works_summer_camp: bool

# ================================================
# Camper data structure
# ================================================

@dataclass
class Camper(Person):
    """
    Represents a camper with social constraints
    and attendance info.
    """
    grade: str
    pair_with: List[str]     # campers they must be grouped with
    avoid_with: List[str]    # campers they must not be grouped with
    siblings: List[str]
    friends: List[str]
    
    attends_summer_school: bool
    attends_summer_camp: bool

    # optional pre-assigned groups
    morning_group: Optional[int] = None
    afternoon_group: Optional[int] = None

# ================================================
# Dataset wrapper
# ================================================

@dataclass
class CampDataset:
    """
    Container holding all campers and counselors.
    Provides convenience lookup methods.
    """
    counselors: List["Counselor"] = field(default_factory=list)
    campers: List["Camper"] = field(default_factory=list)

    def __len__(self) -> int:
        """Return total number of people in dataset"""
        return len(self.counselors) + len(self.campers)
    
    def counselor_by_name(self) -> dict[str, "Counselor"]:
        """Create a dictionary for quick counselor lookup by name"""
        return {c.name: c for c in self.counselors}

    def camper_by_name(self) -> dict[str, "Camper"]:
         """Create a dictionary for quick camper lookup by name"""
        return {c.name: c for c in self.campers}

# ================================================
# Union-Find (hard pair_with)
# ================================================
class UnionFind:
    """
    Disjoint-set structure used to group people 
    who MUST be together (hard pair_with constraints)
    """
    def __init__(self, items: List[str]):
        # initially, each item is its own parent
        # separate set
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x: str) -> str:
        """
        Find the representative (root) of x with path compression
        """
        while self.parent[x] != x:
            # path compression: point directly to grandparent
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        """
        Merge sets containing a and b.
        Uses union by rank for efficiency.
        """
        ra, rb = self.find(a), self.find(b)

        # if already in same set, nothing to do
        if ra == rb:
            return

        # attach smaller tree under larger one
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1

# ================================================
# RBL Output types
# ================================================
@dataclass
class CamperRBL:
    """
    RBL representation for campers in one session.
    """
    session: str
    num_groups: int
    uf: UnionFind

    # hard-paired components
    components: Dict[str, List[str]]          # root -> camper names
    comp_domain: Dict[str, Set[int]]          # root -> allowed groups
    comp_avoid: Dict[str, Set[str]]           # root -> set of other roots it cannot share a group with

@dataclass
class CounselorRBL:
    """
    RBL representation for counselors in one session
    """
    session: str
    num_groups: int
    counselor_domain: Dict[str, Set[int]]     # counselor -> allowed groups

# ================================================
# RBL summary helpers
# ================================================

def avg_domain_size(domains: dict) -> float:
    """
    Compute the average number of valid groups per entity.
    Useful for debugging constraint tightness.
    """
    if not domains:
        return 0.0
    return sum(len(d) for d in domains.values()) / len(domains)

# ================================================
# Full RBL result container
# ================================================

@dataclass
class RBLResult:
    """
    Stores complete RBL output for both morning 
    and afternoon sessions
    """
    morning_groups: int
    afternoon_groups: int
    
    campers_morning: CamperRBL
    campers_afternoon: CamperRBL
    counselors_morning: CounselorRBL
    counselors_afternoon: CounselorRBL

    def summary(self) -> str:
        """
        Produce a summary of the RBL state.
        """
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
