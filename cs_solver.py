from data_structures import *
from typing import Dict
import math

# ----------------------------
# Grade normalization
# ----------------------------
GRADE_MAP = {
    "K": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
}

# ----------------------------
# CS Solver
# ----------------------------
class CampCSSolver:
    def __init__(
        self,
        camper_rbl,
        counselor_rbl,
        campers,
        counselors,
        min_group_size=12,
        max_group_size=18,
        camper_per_counselor=10,
        min_counselors_per_group=2,
        grade_band_width=2,
    ):
        self.camper_rbl = camper_rbl
        self.counselor_rbl = counselor_rbl
        self.num_groups = camper_rbl.num_groups

        self.min_group_size = min_group_size
        self.max_group_size = max_group_size
        self.camper_per_counselor = camper_per_counselor
        self.min_counselors_per_group = min_counselors_per_group
        self.grade_band_width = grade_band_width

        # ---- Camper component metadata ----
        self.component_sizes = {}
        self.component_grades = {}

        camper_map = {c.name: c for c in campers}

        for root, members in camper_rbl.components.items():
            self.component_sizes[root] = len(members)
            self.component_grades[root] = [
                GRADE_MAP[camper_map[m].grade] for m in members
            ]

        # ---- Group state ----
        self.group_state = {
            g: {
                "campers": 0,
                "grades": [],
                "components": [],
                "counselors": []
            }
            for g in range(self.num_groups)
        }

        # ---- Assignment state ----
        self.assignment: Dict[str, int] = {}

    # ----------------------------
    # Variable selection (MRV)
    # ----------------------------
    def _select_next_component(self):
        unassigned = [
            r for r in self.camper_rbl.components
            if r not in self.assignment
        ]

        # MRV: smallest domain first
        return min(
            unassigned,
            key=lambda r: (
                len(self.camper_rbl.comp_domain[r]),
                -self.component_sizes[r]
            )
        )

    # ----------------------------
    # Constraint checks
    # ----------------------------
    def _violates_group_size(self, root, g):
        new_size = self.group_state[g]["campers"] + self.component_sizes[root]
        return new_size > self.max_group_size

    def _violates_grade_band(self, root, g):
        existing = self.group_state[g]["grades"]
        incoming = self.component_grades[root]

        if not existing:
            return False

        min_g = min(existing)
        max_g = max(existing)

        inc_min = min(incoming)
        inc_max = max(incoming)

        new_min = min(min_g, inc_min)
        new_max = max(max_g, inc_max)

        return (new_max - new_min) > self.grade_band_width


    def _violates_avoid_constraints(self, root, g):
        for other_root in self.group_state[g]["components"]:
            if other_root in self.camper_rbl.comp_avoid[root]:
                return True
        return False
    
    def _violates_extreme_imbalance(self, g):
        return self.group_state[g]["campers"] > self.max_group_size

    def _violates_group_counselor_cap(self, g):
        campers = self.group_state[g]["campers"]
        if campers == 0:
            return False

        needed = max(
            math.ceil(campers / self.camper_per_counselor),
            self.min_counselors_per_group
        )

        # Maximum counselors this group could ever get
        possible = sum(
            1 for c, dom in self.counselor_rbl.counselor_domain.items()
            if g in dom
        )

        return needed > possible

    def _violates_future_counselor_feasibility(self):
        """
        Early pruning:
        Checks whether the *minimum* number of counselors that will eventually
        be required already exceeds what is available.
        """
        total_counselors = len(self.counselor_rbl.counselor_domain)

        needed = 0
        for g in range(self.num_groups):
            campers = self.group_state[g]["campers"]
            if campers > 0:
                needed += max(
                    math.ceil(campers / self.camper_per_counselor),
                    self.min_counselors_per_group
                )

        return needed > total_counselors

    # ----------------------------
    # Assignment helpers
    # ----------------------------
    def _assign(self, root, g):
        self.assignment[root] = g
        self.group_state[g]["campers"] += self.component_sizes[root]
        self.group_state[g]["grades"].extend(self.component_grades[root])
        self.group_state[g]["components"].append(root)

    def _unassign(self, root, g):
        del self.assignment[root]
        self.group_state[g]["campers"] -= self.component_sizes[root]
        for _ in self.component_grades[root]:
            self.group_state[g]["grades"].pop()
        self.group_state[g]["components"].remove(root)

    # ----------------------------
    # Backtracking search
    # ----------------------------
    def solve(self):
        return self._backtrack()

    def _backtrack(self):
        # Base case: all components assigned
        if len(self.assignment) == len(self.camper_rbl.components):
            return dict(self.assignment)

        # MRV: choose next component dynamically
        root = self._select_next_component()
        domain = self.camper_rbl.comp_domain[root]

        # Value ordering: least-loaded group first
        for g in sorted(domain, key=lambda g: self.group_state[g]["campers"]):
            if self._violates_group_size(root, g):
                continue
            if self._violates_grade_band(root, g):
                continue
            if self._violates_avoid_constraints(root, g):
                continue

            self._assign(root, g)

            # Early pruning
            if self._violates_future_counselor_feasibility():
                self._unassign(root, g)
                continue

            if self._violates_group_counselor_cap(g):
                self._unassign(root, g)
                continue

            if self._violates_extreme_imbalance(g):
                self._unassign(root, g)
                continue

            result = self._backtrack()
            if result:
                return result

            self._unassign(root, g)

        return None

    def _check_min_group_sizes(self):
        for g in range(self.num_groups):
            if self.group_state[g]["campers"] < self.min_group_size:
                return False
        return True

    # ----------------------------
    # Counselor assignment (second phase)
    # ----------------------------
    def assign_counselors(self):
        counselor_assignments = {}
        available = set(self.counselor_rbl.counselor_domain.keys())

        for g in range(self.num_groups):
            campers = self.group_state[g]["campers"]
            needed = max(
                math.ceil(campers / self.camper_per_counselor),
                self.min_counselors_per_group
            )

            eligible = [
                c for c in available
                if g in self.counselor_rbl.counselor_domain[c]
            ]

            if len(eligible) < needed:
                return None

            chosen = eligible[:needed]
            for c in chosen:
                counselor_assignments[c] = g
                available.remove(c)
                self.group_state[g]["counselors"].append(c)

        return counselor_assignments
