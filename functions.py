from data_structures import Counselor

def is_available_monday(counselor: Counselor) -> bool:
    return counselor.monday_start != "" and counselor.monday_end != ""

def can_pair(c1: Counselor, c2: Counselor) -> bool:
    return (
        c2.name not in c1.avoid_with and
        c1.name not in c2.avoid_with
    )
