import json
import os

INPUT_FILE = r"data\clean_feature_dataset_2023_2024.jsonl"
OUTPUT_FILE = r"data\converted_dataset_2023_2024.jsonl"

print("=" * 70)
print("CONVERTING DATASET TO PROPER JSONL")
print("=" * 70)

print()
print("Input :", INPUT_FILE)
print("Output:", OUTPUT_FILE)
print()

if not os.path.exists(INPUT_FILE):
    print("ERROR: Input dataset not found!")
    exit()

record_count = 0
error_count = 0

decoder = json.JSONDecoder()

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    buffer = ""

    for line in infile:
        buffer += line

        while buffer.strip():

            try:
                record, index = decoder.raw_decode(buffer.lstrip())

                buffer = buffer.lstrip()[index:]

                if isinstance(record, dict):
                    outfile.write(
                        json.dumps(
                            record,
                            ensure_ascii=False
                        ) + "\n"
                    )

                    record_count += 1

                    if record_count % 10000 == 0:
                        print(
                            f"Converted: {record_count:,} records"
                        )

                else:
                    error_count += 1

            except json.JSONDecodeError:
                break

print()
print("=" * 70)
print("CONVERSION COMPLETED")
print("=" * 70)

print(f"Valid records : {record_count:,}")
print(f"Invalid data  : {error_count:,}")
print()
print("Output file:")
print(os.path.abspath(OUTPUT_FILE))
print("=" * 70)