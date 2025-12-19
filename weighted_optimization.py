from collections import Counter

GRADE_TO_AGE_GROUP = {
    "K": "K-1",
    "1": "K-1",
    "2": "2-3",
    "3": "2-3",
    "4": "4-6",
    "5": "4-6",
    "6": "4-6",
}

WEIGHTS = {
    "preferred_age_match": 10,
    "language_match": 2,
    "pair_with": 8,
    "avoid_with": -15,
}

CAMPER_WEIGHTS = {
    "friend_together": 5,
    "language_match_counselor": 3,
    "gender_balance": 10,   # per group, not per camper
}

def gender_balance_score(campers, camper_map):
    counts = {"M": 0, "F": 0}

    for name in campers:
        gender = camper_map[name].gender
        if gender in counts:
            counts[gender] += 1

    total = counts["M"] + counts["F"]
    if total == 0:
        return 0

    imbalance = abs(counts["M"] - counts["F"]) / total
    return max(0, 1 - imbalance)


def score_solution(
    campers_by_group,
    counselor_solution,
    dataset
):
    camper_map = {c.name: c for c in dataset.campers}
    counselor_map = {c.name: c for c in dataset.counselors}

    total_score = 0
    breakdown = []

    # Precompute camper info per group
    group_ages = {}
    group_languages = {}

    for g, campers in campers_by_group.items():
        ages = []
        languages = Counter()
        for name in campers:
            camper = camper_map[name]
            ages.append(GRADE_TO_AGE_GROUP[camper.grade])
            for lang in camper.spoken_languages:
                languages[lang] += 1
        group_ages[g] = Counter(ages)
        group_languages[g] = languages

    # Score each counselor
    for counselor_name, g in counselor_solution.items():
        counselor = counselor_map[counselor_name]
        score = 0
        reasons = []

        campers = campers_by_group[g]

        # ----------------------------
        # Preferred age group
        # ----------------------------
        if counselor.preferred_age_group:
            if group_ages[g][counselor.preferred_age_group] > 0:
                score += WEIGHTS["preferred_age_match"]
                reasons.append("preferred age group match")

        # ----------------------------
        # Language match (bidirectional)
        # ----------------------------
        if counselor.spoken_languages:
            for lang in counselor.spoken_languages:
                matches = group_languages[g].get(lang, 0)
                if matches > 0:
                    score += matches * WEIGHTS["language_match"]
                    reasons.append(f"{matches} language match(es): {lang}")

        # ----------------------------
        # Pair-with bonus
        # ----------------------------
        for p in counselor.pair_with:
            if p in counselor_solution and counselor_solution[p] == g:
                score += WEIGHTS["pair_with"]
                reasons.append(f"paired with {p}")

        # ----------------------------
        # Avoid-with penalty
        # ----------------------------
        for a in counselor.avoid_with:
            if a in counselor_solution and counselor_solution[a] == g:
                score += WEIGHTS["avoid_with"]
                reasons.append(f"avoid-with violation: {a}")

        total_score += score
        breakdown.append((counselor_name, score, reasons))

    return total_score, breakdown

def score_campers(
    campers_by_group,
    counselor_solution,
    dataset
):
    camper_map = {c.name: c for c in dataset.campers}
    counselor_map = {c.name: c for c in dataset.counselors}

    score = 0
    breakdown = []

    # ----------------------------
    # Group-level gender balance
    # ----------------------------
    for g, campers in campers_by_group.items():
        balance = gender_balance_score(campers, camper_map)
        group_score = balance * CAMPER_WEIGHTS["gender_balance"]
        score += group_score
        breakdown.append(
            (f"Group {g + 1}", group_score, f"gender balance = {balance:.2f}")
        )

    # ----------------------------
    # Individual camper scoring
    # ----------------------------
    for g, campers in campers_by_group.items():
        counselors_in_group = [
            c for c, cg in counselor_solution.items() if cg == g
        ]

        for name in campers:
            camper = camper_map[name]
            camper_score = 0
            reasons = []

            # Friends together
            for f in camper.friends:
                if f in campers:
                    camper_score += CAMPER_WEIGHTS["friend_together"]
                    reasons.append(f"friend with {f}")

            # Language match with counselor
            for counselor_name in counselors_in_group:
                counselor = counselor_map[counselor_name]
                shared = set(camper.spoken_languages) & set(counselor.spoken_languages)
                if shared:
                    camper_score += CAMPER_WEIGHTS["language_match_counselor"]
                    reasons.append(
                        f"language match with {counselor_name}: {list(shared)}"
                    )

            if camper_score > 0:
                score += camper_score
                breakdown.append((name, camper_score, reasons))

    return score, breakdown

def score_full_solution(
    campers_by_group,
    counselor_solution,
    dataset
):
    counselor_score, counselor_breakdown = score_solution(
        campers_by_group,
        counselor_solution,
        dataset
    )

    camper_score, camper_breakdown = score_campers(
        campers_by_group,
        counselor_solution,
        dataset
    )

    total = counselor_score + camper_score

    return total, counselor_breakdown, camper_breakdown
