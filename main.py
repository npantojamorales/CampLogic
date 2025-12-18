from data_structures import CampDataset
from parsing import load_counselors, load_campers
from functions import *
import math

def main():
    dataset = CampDataset(
        counselors = load_counselors("counselors.csv"),
        campers = load_campers("campers.csv")
    )

   #print(len(dataset))              # 158
   #print(len(dataset.counselors))   # 25
   #print(len(dataset.campers))      # 133

    rbl = rbl_build(dataset)

    campers_m, campers_a, couns_m, couns_a = count_session_attendance(dataset)
    print("Morning campers:", campers_m)
    print("Morning counselors:", couns_m)
    print("Afternoon campers:", campers_a)
    print("Afternoon counselors:", couns_a)

   #n = choose_afternoon_groups(
   #    num_campers_afternoon=campers_a,
   #    num_counselors_afternoon=couns_a,
   #    min_groups=8,
   #    max_groups=10,
   #    min_group_size=12,
   #    max_group_size=18,
   #   camper_per_counselor=10,
   #    min_counselors_per_group=2
   #)
   #print("Chosen afternoon groups:", n)
   #print("Avg campers per afternoon group:", campers_a / n)
   #print("Avg campers per morning group:", campers_m/ 5)

    print(rbl.summary())

    #print_rbl_components(rbl.campers_morning)
    #print_rbl_components(rbl.campers_afternoon)

    #print_locked_components(rbl.campers_morning)
    #print_locked_components(rbl.campers_afternoon)

    #print_draft_groups_from_locked(rbl.campers_morning)
    #print_draft_groups_from_locked(rbl.campers_afternoon)

    #print_avoid_summary(rbl.campers_morning)
    #print_avoid_summary(rbl.campers_afternoon)

    solver = CampCSSolver(
    camper_rbl=rbl.campers_afternoon,
    counselor_rbl=rbl.counselors_afternoon,
    campers=dataset.campers,
    counselors=dataset.counselors,
    min_group_size=12,
    max_group_size=18,
    camper_per_counselor=10,
    min_counselors_per_group=2,
    grade_band_width=2
)

    camper_solution = solver.solve()

    if not camper_solution:
        print("No feasible camper grouping found.")
        exit()

    counselor_solution = solver.assign_counselors()

    if not counselor_solution:
        print("Camper grouping works, but counselor assignment failed.")
        exit()

    print("Solution found!")

    for g in range(rbl.afternoon_groups):
        print(f"\nGroup {g}")
        print(" Campers:", solver.group_state[g]["campers"])
        print(" Counselors:", solver.group_state[g]["counselors"])

    # Build campers per group
    campers_by_group = {g: [] for g in range(rbl.afternoon_groups)}

    for root, group_id in camper_solution.items():
        members = rbl.campers_afternoon.components[root]
        campers_by_group[group_id].extend(members)

    camper_map = {c.name: c for c in dataset.campers}

    print("\n=== CAMPER ASSIGNMENTS (with grades) ===")

    for g in range(rbl.afternoon_groups):
        campers = campers_by_group[g]
        print(f"\nGroup {g} ({len(campers)} campers):")
        for name in sorted(campers):
            grade = camper_map[name].grade
            print(f"  {name} (Grade {grade})")

if __name__ == "__main__":
    main()
