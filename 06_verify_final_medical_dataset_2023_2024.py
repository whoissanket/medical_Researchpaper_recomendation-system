import json
import os

INPUT_FILE = r"output\medical_only_dataset_2023_2024.jsonl"

print("=" * 70)
print("FINAL MEDICAL DATASET VERIFICATION")
print("=" * 70)

if not os.path.exists(INPUT_FILE):
    print("ERROR: File not found!")
    print(INPUT_FILE)
    exit()

total = 0
invalid = 0
duplicates = 0
missing_fields = 0
non_medical = 0

ids = set()

required_fields = [
    "id",
    "title",
    "abstract",
    "keywords",
    "year",
    "doc_type",
    "venue",
    "medical_score"
]

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as infile:

    for line in infile:

        line = line.strip()

        if not line:
            continue

        try:

            record = json.loads(line)

            total += 1

            # Check ID
            paper_id = record.get("id")

            if paper_id in ids:

                duplicates += 1

            else:

                ids.add(paper_id)


            # Check required fields

            for field in required_fields:

                if field not in record:

                    missing_fields += 1

                    break


            # Final safety check

            if record.get("medical") is not True:

                non_medical += 1


        except Exception:

            invalid += 1


print()
print("=" * 70)
print("VERIFICATION RESULT")
print("=" * 70)

print(f"Total papers       : {total:,}")
print(f"Invalid JSON       : {invalid:,}")
print(f"Duplicate IDs      : {duplicates:,}")
print(f"Missing fields     : {missing_fields:,}")
print(f"Non-medical flags  : {non_medical:,}")

print()

if (
    invalid == 0
    and duplicates == 0
    and missing_fields == 0
    and non_medical == 0
):

    print("STATUS: PASS")
    print("Final dataset is structurally valid.")

else:

    print("STATUS: CHECK REQUIRED")


print()
print("Dataset:")
print(os.path.abspath(INPUT_FILE))

print("=" * 70)