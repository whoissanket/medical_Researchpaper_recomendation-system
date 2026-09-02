import json
import os

INPUT_FILE = r"output\medical_scored_dataset_2023_2024.jsonl"

print("=" * 70)
print("MEDICAL DATASET VALIDATION")
print("=" * 70)

if not os.path.exists(INPUT_FILE):
    print("ERROR: Input file not found!")
    print(INPUT_FILE)
    exit()

total = 0
medical = 0
non_medical = 0
invalid = 0

# Store examples for manual inspection
high_score = []
medium_score = []
borderline = []

with open(INPUT_FILE, "r", encoding="utf-8") as infile:

    for line in infile:

        line = line.strip()

        if not line:
            continue

        try:

            record = json.loads(line)

            total += 1

            score = record.get("medical_score", 0)
            is_medical = record.get("medical", False)

            if is_medical:
                medical += 1
            else:
                non_medical += 1

            # Keep a few examples from each range
            if score >= 40 and len(high_score) < 15:
                high_score.append(record)

            elif 20 <= score < 40 and len(medium_score) < 15:
                medium_score.append(record)

            elif 10 <= score < 20 and len(borderline) < 15:
                borderline.append(record)

        except Exception:
            invalid += 1


print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"Total records       : {total:,}")
print(f"Medical papers      : {medical:,}")
print(f"Non-medical papers  : {non_medical:,}")
print(f"Invalid JSON        : {invalid:,}")

print()

if total == medical + non_medical:
    print("PASS: Record counts are consistent.")
else:
    print("WARNING: Record counts do not match!")


def display_examples(title, records):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    if not records:
        print("No examples found.")
        return

    for i, record in enumerate(records, 1):

        print()
        print(f"Example {i}")
        print("-" * 70)

        print("Medical Score :", record.get("medical_score"))
        print("Medical       :", record.get("medical"))
        print("Title         :", record.get("title"))
        print("Keywords      :", record.get("keywords"))
        print("Year          :", record.get("year"))
        print("Venue         :", record.get("venue"))

        abstract = record.get("abstract", "")

        # Don't print entire abstract
        if len(abstract) > 500:
            abstract = abstract[:500] + "..."

        print("Abstract      :", abstract)


display_examples(
    "HIGH SCORE PAPERS (40+)",
    high_score
)

display_examples(
    "MEDIUM SCORE PAPERS (20-39)",
    medium_score
)

display_examples(
    "BORDERLINE PAPERS (10-19)",
    borderline
)

print()
print("=" * 70)
print("VALIDATION COMPLETED")
print("=" * 70)