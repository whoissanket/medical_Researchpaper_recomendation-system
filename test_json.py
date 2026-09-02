import json

file_path = r"data\clean_feature_dataset_2023_2024.jsonl"

print("=" * 70)
print("TESTING DATASET")
print("=" * 70)

with open(file_path, "r", encoding="utf-8") as f:

    for i in range(3):

        line = f.readline()

        print()
        print(f"LINE {i + 1}")
        print("-" * 70)

        print(line[:500])

        try:
            data = json.loads(line)

            print()
            print("JSON PARSED SUCCESSFULLY")
            print("Type:", type(data))

            if isinstance(data, dict):
                print("Fields:", list(data.keys()))

        except Exception as e:
            print()
            print("JSON PARSING ERROR:")
            print(e)

print()
print("=" * 70)
print("TEST COMPLETED")
print("=" * 70)