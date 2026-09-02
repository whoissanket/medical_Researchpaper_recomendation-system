import json
import os
import re

INPUT_FILE = r"output\processed_dataset_2023_2024.jsonl"
OUTPUT_FILE = r"output\medical_scored_dataset_2023_2024.jsonl"

print("=" * 70)
print("MEDICAL RELEVANCE SCORING - 2023-2024 DATASET")
print("=" * 70)

if not os.path.exists(INPUT_FILE):
    print("ERROR: Input file not found!")
    print(INPUT_FILE)
    exit()

# ---------------------------------------------------------
# Strong medical terms
# ---------------------------------------------------------

STRONG_TERMS = [
    "cancer",
    "carcinoma",
    "tumor",
    "tumour",
    "oncology",
    "malignant",
    "metastasis",
    "leukemia",
    "lymphoma",
    "melanoma",
    "glioma",

    "patient",
    "patients",
    "clinical",
    "clinically",
    "hospital",
    "healthcare",
    "health care",
    "medical",
    "medicine",
    "physician",
    "doctor",

    "disease",
    "diseases",
    "syndrome",
    "disorder",
    "pathology",
    "pathological",

    "diagnosis",
    "diagnostic",
    "diagnostics",
    "prognosis",
    "screening",

    "surgery",
    "surgical",
    "therapy",
    "therapeutic",
    "treatment",
    "drug",
    "drugs",
    "pharmaceutical",

    "clinical trial",
    "clinical trials",
    "randomized trial",

    "covid",
    "coronavirus",
    "sars-cov-2",
    "influenza",
    "infection",
    "infectious",

    "vaccine",
    "vaccination",
    "immunotherapy",
    "immunology",

    "biomedical",
    "biomedicine",
    "bioinformatics",
    "medical imaging",
    "radiology",
    "radiotherapy",

    "cardiology",
    "cardiovascular",
    "neurology",
    "neuroscience",
    "neurodegenerative",

    "diabetes",
    "hypertension",
    "stroke",
    "alzheimer",
    "parkinson",

    "genomics",
    "genome",
    "genomic",
    "proteomics",

    "tissue",
    "organ",
    "blood",
    "plasma",
    "serum",
    "biopsy",

    "anatomy",
    "physiology",
    "epidemiology",
    "public health",

    "telemedicine",
    "telehealth"
]

# ---------------------------------------------------------
# Medical phrases that are especially strong
# ---------------------------------------------------------

STRONG_PHRASES = [
    "medical diagnosis",
    "disease diagnosis",
    "clinical diagnosis",
    "medical imaging",
    "clinical decision",
    "clinical decision support",
    "patient diagnosis",
    "patient monitoring",
    "healthcare system",
    "healthcare application",
    "disease detection",
    "cancer detection",
    "tumor detection",
    "tumour detection",
    "disease prediction",
    "medical image",
    "medical images",
    "medical data",
    "clinical data",
    "electronic health record",
    "electronic medical record",
    "drug discovery",
    "drug delivery",
    "disease prediction",
    "disease classification",
    "medical classification"
]

# ---------------------------------------------------------
# Terms that can cause false positives
# ---------------------------------------------------------

GENERIC_TERMS = [
    "cell",
    "cells",
    "network",
    "networks",
    "treatment",
    "diagnosis",
    "diagnostic",
    "genetic",
    "gene",
    "genes",
    "model",
    "classification"
]

# ---------------------------------------------------------
# Obvious non-medical contexts
# ---------------------------------------------------------

NON_MEDICAL_PHRASES = [
    "cellular network",
    "cellular networks",
    "mobile network",
    "wireless network",
    "network cell",
    "assembly sequence",
    "software fault diagnosis",
    "fault diagnosis",
    "fault detection",
    "network diagnosis",
    "traffic diagnosis",
    "machine diagnosis",
    "equipment diagnosis",
    "industrial diagnosis",
    "building diagnosis",
    "structural diagnosis",
    "power system diagnosis",
    "circuit diagnosis",
    "communication network"
]


def normalize(text):
    text = str(text).lower()
    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def count_term_matches(text, terms):
    count = 0

    for term in terms:
        term = normalize(term)

        # Word/phrase boundary matching
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text):
            count += 1

    return count


def calculate_medical_score(record):

    title = normalize(record.get("title", ""))
    abstract = normalize(record.get("abstract", ""))

    keywords = record.get("keywords", [])

    if isinstance(keywords, list):
        keyword_text = " ".join(str(k) for k in keywords)
    else:
        keyword_text = str(keywords)

    keyword_text = normalize(keyword_text)

    # -----------------------------------------------------
    # Score each field separately
    # -----------------------------------------------------

    title_strong = count_term_matches(title, STRONG_TERMS)
    keyword_strong = count_term_matches(keyword_text, STRONG_TERMS)
    abstract_strong = count_term_matches(abstract, STRONG_TERMS)

    title_phrases = count_term_matches(title, STRONG_PHRASES)
    keyword_phrases = count_term_matches(keyword_text, STRONG_PHRASES)
    abstract_phrases = count_term_matches(abstract, STRONG_PHRASES)

    # -----------------------------------------------------
    # Weighted scoring
    # -----------------------------------------------------

    score = 0

    score += title_strong * 5
    score += keyword_strong * 4
    score += abstract_strong * 1

    score += title_phrases * 8
    score += keyword_phrases * 6
    score += abstract_phrases * 3

    # -----------------------------------------------------
    # Context evidence
    # -----------------------------------------------------

    medical_context_terms = [
        "patient",
        "clinical",
        "hospital",
        "healthcare",
        "disease",
        "medical",
        "medicine",
        "physician",
        "cancer",
        "tumor",
        "diagnosis",
        "treatment",
        "therapy",
        "drug",
        "biomedical",
        "radiology",
        "surgery",
        "vaccine",
        "infection"
    ]

    full_text = title + " " + keyword_text + " " + abstract

    context_count = count_term_matches(
        full_text,
        medical_context_terms
    )

    if context_count >= 3:
        score += 5

    if context_count >= 5:
        score += 5

    # -----------------------------------------------------
    # Penalize obvious non-medical contexts
    # -----------------------------------------------------

    penalty = 0

    for phrase in NON_MEDICAL_PHRASES:
        if normalize(phrase) in full_text:
            penalty += 5

    score -= penalty

    if score < 0:
        score = 0

    # -----------------------------------------------------
    # Determine medical classification
    # -----------------------------------------------------

    if score >= 10:
        medical = True
    else:
        medical = False

    return score, medical


# ---------------------------------------------------------
# Process dataset
# ---------------------------------------------------------

total_records = 0
medical_records = 0
non_medical_records = 0

score_distribution = {
    "0-4": 0,
    "5-9": 0,
    "10-19": 0,
    "20-39": 0,
    "40+": 0
}

print()
print("Starting medical scoring...")
print()

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    for line in infile:

        line = line.strip()

        if not line:
            continue

        try:
            record = json.loads(line)

            score, medical = calculate_medical_score(record)

            record["medical_score"] = score
            record["medical"] = medical

            outfile.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

            total_records += 1

            if medical:
                medical_records += 1
            else:
                non_medical_records += 1

            if score <= 4:
                score_distribution["0-4"] += 1
            elif score <= 9:
                score_distribution["5-9"] += 1
            elif score <= 19:
                score_distribution["10-19"] += 1
            elif score <= 39:
                score_distribution["20-39"] += 1
            else:
                score_distribution["40+"] += 1

            if total_records % 100000 == 0:
                print(f"Processed: {total_records:,} records")

        except Exception as e:
            print("Error:", e)


# ---------------------------------------------------------
# Final report
# ---------------------------------------------------------

print()
print("=" * 70)
print("MEDICAL SCORING COMPLETED")
print("=" * 70)

print(f"Total records       : {total_records:,}")
print(f"Medical papers      : {medical_records:,}")
print(f"Non-medical papers  : {non_medical_records:,}")

print()
print("Score distribution:")
print(f"0-4                 : {score_distribution['0-4']:,}")
print(f"5-9                 : {score_distribution['5-9']:,}")
print(f"10-19               : {score_distribution['10-19']:,}")
print(f"20-39               : {score_distribution['20-39']:,}")
print(f"40+                 : {score_distribution['40+']:,}")

print()
print("Output file:")
print(os.path.abspath(OUTPUT_FILE))

print("=" * 70)