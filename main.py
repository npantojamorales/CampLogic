from data_structures import CampDataset
from parsing import load_counselors, load_campers
from rbl import rbl_build, count_session_attendance
from cs_solver import CampCSSolver
from weighted_optimization import score_full_solution

def main():
    """
    1) load CSV data
    2) build RBL constraints
    3) solver camper grouping (CS Solver)
    4) assign counselors
    5) score and display the solution
    """

    # =====================================
    # Load dataset from CSVs
    # =====================================
    dataset = CampDataset(
        counselors = load_counselors("counselors.csv"),
        campers = load_campers("campers.csv")
    )

    # sanity checks
    """
    print(len(dataset))              # 158
    print(len(dataset.counselors))   # 25
    print(len(dataset.campers))      # 133
    """

    # =====================================
    # Build RBL constraints
    # =====================================    
    rbl = rbl_build(dataset)

    # debug RBL inspection
    """
    print("Morning campers (RBL):",
        sum(len(v) for v in rbl.campers_morning.components.values()))
    
    print("Morning campers (RBL):",
        sum(len(v) for v in rbl.campers_afternoon.components.values()))

    print(rbl.summary())
    """

    # =====================================
    # Afternoon Group Solving
    # =====================================

    # initialize the constraint-satisfaction solver
    solver = CampCSSolver(
    camper_rbl=rbl.campers_afternoon,
    counselor_rbl=rbl.counselors_afternoon,
    campers=dataset.campers,
    counselors=dataset.counselors,
    min_group_size=10,
    max_group_size=20,
    camper_per_counselor=10,
    min_counselors_per_group=2,
    grade_band_width=2
)

    # =====================================
    # Solve camper grouping
    # =====================================
    camper_solution = solver.solve()

    if not camper_solution:
        print("No feasible camper grouping found.")
        exit()

    # =====================================
    # Assign counselors
    # =====================================
    counselor_solution = solver.assign_counselors()

    if not counselor_solution:
        print("Camper grouping works, but counselor assignment failed.")
        exit()

    print("\nSolution found!")

    # =====================================
    # Print high-level group summary
    # =====================================
    for g in range(rbl.afternoon_groups):
        print(f"\nGroup {g+1}")
        print(" Campers:", solver.group_state[g]["campers"])
        print(" Counselors:", solver.group_state[g]["counselors"])

    # =====================================
    # Build camper lists per group
    # =====================================
    campers_by_group = {g: [] for g in range(rbl.afternoon_groups)}

    for root, group_id in camper_solution.items():
        members = rbl.campers_afternoon.components[root]
        campers_by_group[group_id].extend(members)

    camper_map = {c.name: c for c in dataset.campers}

    # =====================================
    # Print detailed group assignments
    # =====================================
    print("\n=== AFTERNOON GROUP ASSIGNMENTS (with grades) ===")

    for g in range(rbl.afternoon_groups):
        campers = campers_by_group[g]
        print(f"\nGroup {g+1} ({len(campers)} campers):")
        for name in sorted(campers):
            grade = camper_map[name].grade
            print(f"  {name} (Grade {grade})")

    # =====================================
    # Score the final solution
    # =====================================
    total, counselor_details, camper_details = score_full_solution(
        campers_by_group,
        counselor_solution,
        dataset
    )

    print("\n=== FINAL WEIGHTED SCORE FOR AFTERNOON GROUPS ===")
    print("Total score:", total)

    # optional detailed score breakdown
    """
    print("\n--- Counselor Contributions ---")
    for name, s, reasons in counselor_details:
        print(f"{name}: {s}")
        for r in reasons:
            print("  -", r)

    print("\n--- Camper Contributions ---")
    for name, s, reasons in camper_details:
        print(f"{name}: {s}")
        if isinstance(reasons, list):
            for r in reasons:
                print("  -", r)
        else:
            print(" ", reasons)
    """

if __name__ == "__main__":
    main()
