import json
import os

INPUT_FILE = r"data\converted_dataset_2023_2024.jsonl"
OUTPUT_FILE = r"output\processed_dataset_2023_2024.jsonl"

print("=" * 70)
print("DATA CLEANING - 2023-2024 DATASET")
print("=" * 70)

print()
print("Input :", INPUT_FILE)
print("Output:", OUTPUT_FILE)
print()

if not os.path.exists(INPUT_FILE):
    print("ERROR: Input file not found!")
    exit()

os.makedirs("output", exist_ok=True)

total_records = 0
valid_records = 0
invalid_records = 0

missing_id = 0
missing_title = 0
missing_abstract = 0
duplicate_ids = 0

seen_ids = set()

print("Starting cleaning...")
print()

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    for line in infile:

        line = line.strip()

        if not line:
            continue

        total_records += 1

        try:
            record = json.loads(line)

            if not isinstance(record, dict):
                invalid_records += 1
                continue

            # Get fields
            paper_id = record.get("id")
            title = record.get("title")
            abstract = record.get("abstract")
            keywords = record.get("keywords")
            year = record.get("year")
            doc_type = record.get("doc_type")
            venue = record.get("venue")

            # Check ID
            if paper_id is None or str(paper_id).strip() == "":
                missing_id += 1
                continue

            paper_id = str(paper_id).strip()

            # Check duplicate ID
            if paper_id in seen_ids:
                duplicate_ids += 1
                continue

            seen_ids.add(paper_id)

            # Check title
            if title is None or str(title).strip() == "":
                missing_title += 1
                continue

            title = str(title).strip()

            # Check abstract
            if abstract is None or str(abstract).strip() == "":
                missing_abstract += 1
                continue

            abstract = str(abstract).strip()

            # Clean keywords
            if keywords is None:
                keywords = []

            if not isinstance(keywords, list):
                keywords = [str(keywords)]

            cleaned_keywords = []

            for keyword in keywords:
                if keyword is not None:
                    keyword = str(keyword).strip()

                    if keyword:
                        cleaned_keywords.append(keyword)

            keywords = cleaned_keywords

            # Clean year
            try:
                year = int(year)
            except:
                year = None

            # Clean doc_type
            if doc_type is not None:
                doc_type = str(doc_type).strip()

            # Clean venue
            if venue is not None:
                venue = str(venue).strip()

            # Create cleaned record
            cleaned_record = {
                "id": paper_id,
                "title": title,
                "abstract": abstract,
                "keywords": keywords,
                "year": year,
                "doc_type": doc_type,
                "venue": venue
            }

            # Write cleaned record
            outfile.write(
                json.dumps(
                    cleaned_record,
                    ensure_ascii=False
                ) + "\n"
            )

            valid_records += 1

        except Exception:
            invalid_records += 1

        if total_records % 100000 == 0:
            print(f"Processed: {total_records:,} records")


print()
print("=" * 70)
print("CLEANING COMPLETED")
print("=" * 70)

print(f"Total records       : {total_records:,}")
print(f"Valid records       : {valid_records:,}")
print(f"Invalid records     : {invalid_records:,}")
print(f"Missing IDs         : {missing_id:,}")
print(f"Missing titles      : {missing_title:,}")
print(f"Missing abstracts   : {missing_abstract:,}")
print(f"Duplicate IDs       : {duplicate_ids:,}")

print()
print("Cleaned dataset:")
print(os.path.abspath(OUTPUT_FILE))

print("=" * 70)