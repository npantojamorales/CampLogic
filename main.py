from parsing import load_counselors
from functions import can_pair

def main():
    counselors = load_counselors("counselors.csv")

    print(f"Loaded {len(counselors)} counselors")
    print(counselors[0])

    print(
        can_pair(counselors[0], counselors[1])
    )

if __name__ == "__main__":
    main()
