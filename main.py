from data_structures import CampDataset
from parsing import load_counselors, load_campers
from functions import *
import math

def main():
    dataset = CampDataset(
        counselors = load_counselors("counselors.csv"),
        campers = load_campers("campers.csv")
    )

    print(len(dataset))              # total people
    print(len(dataset.counselors))   # 25
    print(len(dataset.campers))      # 133

    rbl = rbl_build(dataset)

    campers_m, campers_a, couns_m, couns_a = count_session_attendance(dataset)
    print("Morning campers:", campers_m)
    print("Morning counselors:", couns_m)
    print("Afternoon campers:", campers_a)
    print("Afternoon counselors:", couns_a)

    n = choose_afternoon_groups(
        num_campers_afternoon=campers_a,
        num_counselors_afternoon=couns_a,
        min_groups=8,
        max_groups=10,
        min_group_size=12,
        max_group_size=18,
        camper_per_counselor=10,
        min_counselors_per_group=2
    )
    print("Chosen afternoon groups:", n)
    print("Avg campers per afternoon group:", campers_a / n)
    print("Avg campers per morning group:", campers_m/ 5)

    print(rbl.summary())

    #print_rbl_components(rbl.campers_morning)
    #print_rbl_components(rbl.campers_afternoon)

    #print_locked_components(rbl.campers_morning)
    #print_locked_components(rbl.campers_afternoon)

    #print_draft_groups_from_locked(rbl.campers_morning)
    #print_draft_groups_from_locked(rbl.campers_afternoon)

    #print_avoid_summary(rbl.campers_morning)
    #print_avoid_summary(rbl.campers_afternoon)

if __name__ == "__main__":
    main()
