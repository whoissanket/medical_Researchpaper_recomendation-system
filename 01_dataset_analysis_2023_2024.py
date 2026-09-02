import json
import os

INPUT_FILE = os.path.join(
    "data",
    "clean_feature_dataset_2023_2024.jsonl"
)

total_records = 0
valid_records = 0
invalid_records = 0

first_record = None
fields = set()

print("=" * 70)
print("DATASET ANALYSIS")
print("=" * 70)

print(f"Input file: {INPUT_FILE}")
print()

if not os.path.exists(INPUT_FILE):
    print("ERROR: Dataset file not found!")
    print()
    print("Expected location:")
    print(os.path.abspath(INPUT_FILE))
    exit()

print("Dataset found.")
print("Reading dataset...")
print()

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line_number, line in enumerate(f, start=1):

        line = line.strip()

        if not line:
            continue

        try:
            record = json.loads(line)

            total_records += 1

            if first_record is None:
                first_record = record

            if isinstance(record, dict):
                valid_records += 1
                fields.update(record.keys())
            else:
                invalid_records += 1

        except json.JSONDecodeError:
            invalid_records += 1

        if total_records % 100000 == 0:
            print(f"Processed: {total_records:,} records")

print()
print("=" * 70)
print("ANALYSIS RESULT")
print("=" * 70)

print(f"Total records   : {total_records:,}")
print(f"Valid records   : {valid_records:,}")
print(f"Invalid records : {invalid_records:,}")

print()
print("Fields found:")

for field in sorted(fields):
    print(f" - {field}")

print()
print("=" * 70)
print("FIRST RECORD")
print("=" * 70)

if first_record:
    print(json.dumps(
        first_record,
        indent=2,
        ensure_ascii=False
    ))

print()
print("=" * 70)
print("ANALYSIS COMPLETED")
print("=" * 70)