from data_structures import *
from dataclasses import dataclass
from typing import Dict, Set, Tuple, List, Optional
import math
import pandas as pd

def build_name_maps(dataset) -> Tuple[Dict[str, object], Dict[str, object]]:
    camper_map = {c.name: c for c in dataset.campers}
    counselor_map = {c.name: c for c in dataset.counselors}
    return camper_map, counselor_map

def counselor_works_session(counselor, session: str) -> bool:
    # session: "morning" means summer school, "afternoon" means summer camp
    if session == "morning":
        return bool(counselor.works_summer_school)
    if session == "afternoon":
        return bool(counselor.works_summer_camp)
    raise ValueError("session must be 'morning' or 'afternoon'")

def _has_time(value) -> bool:
    return value is not None and str(value).strip() != ""

def counselor_has_any_availability(counselor) -> bool:
    # If they have at least one day with both start+end, consider them usable.
    days = [
        ("monday_start", "monday_end"),
        ("tuesday_start", "tuesday_end"),
        ("wednesday_start", "wednesday_end"),
        ("thursday_start", "thursday_end"),
        ("friday_start", "friday_end"),
    ]
    for start_attr, end_attr in days:
        if _has_time(getattr(counselor, start_attr)) and _has_time(getattr(counselor, end_attr)):
            return True
    return False

# ----------------------------
# Helper: attendance counts
# ----------------------------
def count_session_attendance(dataset):
    campers_morning = sum(
        c.attends_summer_camp and (not c.attends_summer_school)
        for c in dataset.campers
    )
    campers_afternoon = sum(c.attends_summer_camp for c in dataset.campers)

    counselors_morning = sum(
        counselor_works_session(cn, "morning") and counselor_has_any_availability(cn)
        for cn in dataset.counselors
    )
    counselors_afternoon = sum(
        counselor_works_session(cn, "afternoon") and counselor_has_any_availability(cn)
        for cn in dataset.counselors
    )

    return campers_morning, campers_afternoon, counselors_morning, counselors_afternoon

# ----------------------------
# Group count choice (afternoon)
# ----------------------------
def choose_afternoon_groups(
    num_campers_afternoon: int,
    num_counselors_afternoon: int,
    min_groups: int = 8,
    max_groups: int = 10,
    min_group_size: int = 12,
    max_group_size: int = 18,
    camper_per_counselor: int = 10,
    min_counselors_per_group: int = 2
) -> int:
    feasible = []

    for g in range(min_groups, max_groups + 1):
        # group size feasibility
        if num_campers_afternoon < g * min_group_size:
            continue
        if num_campers_afternoon > g * max_group_size:
            continue

        # staffing feasibility
        ratio_needed = math.ceil(num_campers_afternoon / camper_per_counselor)
        per_group_needed = g * min_counselors_per_group
        counselors_needed = max(ratio_needed, per_group_needed)

        if num_counselors_afternoon >= counselors_needed:
            feasible.append(g)

    return max(feasible) if feasible else min_groups

# ----------------------------
# RBL: camper eligibility for a session
# ----------------------------
def camper_domain_for_session(camper, session: str, num_groups: int) -> set[int]:
    """
    session: "morning" = MORNING CAMP GROUPS
             "afternoon" = AFTERNOON CAMP GROUPS
    Hard rule: summer school campers are NOT placed in morning camp groups.
    """
    if session == "morning":
        # morning camp groups only for camp-only kids
        if not camper.attends_summer_camp:
            return set()
        if camper.attends_summer_school:
            return set()

    if session == "afternoon":
        # afternoon camp groups include all camp kids
        if not camper.attends_summer_camp:
            return set()

    pref = camper.morning_group if session == "morning" else camper.afternoon_group
    if pref is not None and not pd.isna(pref):
        return {int(pref)}

    return set(range(num_groups))


# ----------------------------
# RBL: counselor eligibility for a session (soft pair/avoid NOT enforced)
# ----------------------------
def counselor_domain_for_session(counselor, session: str, num_groups: int) -> set[int]:
    # Hard filter: must work this session AND have availability
    if not counselor_works_session(counselor, session):
        return set()
    if not counselor_has_any_availability(counselor):
        return set()

    # Hard filter: locked group if provided
    pref = counselor.morning_group if session == "morning" else counselor.afternoon_group
    if pref is not None and not pd.isna(pref):
        return {int(pref)}

    return set(range(num_groups))


# ----------------------------
# RBL: build camper constraints for ONE session
# ----------------------------
def rbl_build_campers_for_session(dataset, session: str, num_groups: int) -> CamperRBL:
    camper_map, _ = build_name_maps(dataset)
    names = list(camper_map.keys())

    # 1) hard must-link via pair_with
    uf = UnionFind(names)
    for camper in dataset.campers:
        for p in camper.pair_with:
            if p in camper_map:
                uf.union(camper.name, p)

    # 2) build components (clusters)
    components: Dict[str, List[str]] = {}
    for name in names:
        root = uf.find(name)
        components.setdefault(root, []).append(name)

    # 3) compute component domains as intersection of member domains
    comp_domain: Dict[str, Set[int]] = {}
    attending_components: Dict[str, List[str]] = {}

    for root, members in components.items():
        member_domains = [camper_domain_for_session(camper_map[m], session, num_groups) for m in members]
        anyone_attends = any(len(d) > 0 for d in member_domains)

        if anyone_attends:
            attending_components[root] = members

            dom = None
            for d in member_domains:
                # ignore non-attending members (empty domain) in intersection
                if not d:
                    continue
                dom = set(d) if dom is None else (dom & d)

            comp_domain[root] = dom if dom is not None else set()

    # If attends but domain empty -> impossible
    for root, members in attending_components.items():
        if not comp_domain[root]:
            raise ValueError(
                f"RBL conflict ({session}): paired component {members} has no valid groups "
                f"(check attendance + locked morning/afternoon_group fields)."
            )

    # 4) hard cannot-link via avoid_with at component level
    comp_avoid: Dict[str, Set[str]] = {root: set() for root in attending_components.keys()}

    for camper in dataset.campers:
        c_root = uf.find(camper.name)
        if c_root not in attending_components:
            continue

        for a in camper.avoid_with:
            if a not in camper_map:
                continue
            a_root = uf.find(a)
            if a_root not in attending_components:
                continue

            # contradiction: same component both paired and avoided
            if c_root == a_root:
                raise ValueError(
                    f"RBL conflict ({session}): {camper.name} avoids {a} but they are in the same "
                    f"pair_with component (hard constraints)."
                )

            comp_avoid[c_root].add(a_root)
            comp_avoid[a_root].add(c_root)

    return CamperRBL(
        session=session,
        num_groups=num_groups,
        uf=uf,
        components=attending_components,
        comp_domain=comp_domain,
        comp_avoid=comp_avoid,
    )

# ----------------------------
# RBL: build counselor domains for ONE session (soft pair/avoid not applied)
# ----------------------------
def rbl_build_counselors_for_session(dataset, session: str, num_groups: int) -> CounselorRBL:
    _, counselor_map = build_name_maps(dataset)

    counselor_domain: Dict[str, Set[int]] = {}
    for name, counselor in counselor_map.items():
        counselor_domain[name] = counselor_domain_for_session(counselor, session, num_groups)

    return CounselorRBL(session=session, num_groups=num_groups, counselor_domain=counselor_domain)

def rbl_build(dataset) -> RBLResult:
    MORNING_GROUPS = 5

    campers_m, campers_a, couns_m, couns_a = count_session_attendance(dataset)

    AFTERNOON_GROUPS = choose_afternoon_groups(
        num_campers_afternoon=campers_a,
        num_counselors_afternoon=couns_a,
        min_groups=8,
        max_groups=10,
        min_group_size=12,
        max_group_size=20,
        camper_per_counselor=10,
        min_counselors_per_group=2
    )

    campers_morning = rbl_build_campers_for_session(dataset, "morning", MORNING_GROUPS)
    campers_afternoon = rbl_build_campers_for_session(dataset, "afternoon", AFTERNOON_GROUPS)

    counselors_morning = rbl_build_counselors_for_session(dataset, "morning", MORNING_GROUPS)
    counselors_afternoon = rbl_build_counselors_for_session(dataset, "afternoon", AFTERNOON_GROUPS)

    return RBLResult(
        morning_groups=MORNING_GROUPS,
        afternoon_groups=AFTERNOON_GROUPS,
        campers_morning=campers_morning,
        campers_afternoon=campers_afternoon,
        counselors_morning=counselors_morning,
        counselors_afternoon=counselors_afternoon,
    )

def print_rbl_components(camper_rbl, max_show=80):
    print(f"\n=== RBL Components ({camper_rbl.session}) ===")
    print("Num groups:", camper_rbl.num_groups)
    print("Num components:", len(camper_rbl.components))

    shown = 0
    for root, members in camper_rbl.components.items():
        print(f"- component size {len(members)}: {members}")
        shown += 1
        if shown >= max_show:
            break

def print_locked_components(camper_rbl):
    locked = []
    for root, dom in camper_rbl.comp_domain.items():
        if len(dom) == 1:
            g = next(iter(dom))
            locked.append((g, root))

    locked.sort(key=lambda x: x[0])

    print(f"\n=== Locked components ({camper_rbl.session}) ===")
    if not locked:
        print("None locked (no pre-assigned group numbers).")
        return

    for g, root in locked:
        members = camper_rbl.components[root]
        print(f"Group {g}: component size {len(members)} -> {members}")

def print_draft_groups_from_locked(camper_rbl):
    groups = {g: [] for g in range(camper_rbl.num_groups)}

    for root, dom in camper_rbl.comp_domain.items():
        if len(dom) == 1:
            g = next(iter(dom))
            groups[g].extend(camper_rbl.components[root])

    print(f"\n=== Draft groups from locked assignments ({camper_rbl.session}) ===")
    for g in range(camper_rbl.num_groups):
        members = groups[g]
        print(f"Group {g}: {len(members)} campers")
        if members:
            print("  ", members)

def print_avoid_summary(camper_rbl, max_show=130):
    print(f"\n=== Avoid edges summary ({camper_rbl.session}) ===")
    items = list(camper_rbl.comp_avoid.items())
    items.sort(key=lambda x: len(x[1]), reverse=True)

    for root, avoids in items[:max_show]:
        members = camper_rbl.components[root]
        print(f"Component {members} avoids {len(avoids)} other components")


