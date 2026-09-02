import json
import os
import re

INPUT_FILE = r"output\medical_scored_dataset_2023_2024.jsonl"
OUTPUT_FILE = r"output\medical_only_dataset_2023_2024.jsonl"


print("=" * 70)
print("CREATING STRICT MEDICAL-ONLY DATASET")
print("=" * 70)


if not os.path.exists(INPUT_FILE):
    print("ERROR: Input file not found!")
    print(INPUT_FILE)
    exit()


# =========================================================
# Strong medical concepts
# =========================================================

STRONG_MEDICAL_TERMS = [

    # Healthcare / clinical
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
    "clinical trial",
    "clinical trials",
    "patient care",
    "patient monitoring",

    # Disease
    "disease",
    "diseases",
    "disorder",
    "disorders",
    "syndrome",
    "pathology",
    "pathological",

    # Cancer
    "cancer",
    "carcinoma",
    "tumor",
    "tumour",
    "oncology",
    "malignant",
    "malignancy",
    "metastasis",
    "leukemia",
    "lymphoma",
    "melanoma",
    "glioma",

    # Diagnosis
    "diagnosis",
    "diagnostic",
    "diagnostics",
    "prognosis",
    "screening",
    "disease detection",
    "cancer detection",
    "tumor detection",

    # Treatment
    "treatment",
    "therapy",
    "therapeutic",
    "surgery",
    "surgical",
    "rehabilitation",
    "drug",
    "drugs",
    "pharmaceutical",
    "immunotherapy",
    "chemotherapy",
    "drug discovery",
    "drug delivery",

    # Biomedical
    "biomedical",
    "biomedicine",
    "bioinformatics",
    "biotechnology",
    "genomics",
    "genome",
    "genomic",
    "proteomics",
    "protein",
    "biomarker",
    "biomarkers",
    "tissue",
    "biopsy",
    "blood",
    "plasma",
    "serum",

    # Medical imaging
    "medical imaging",
    "medical image",
    "medical images",
    "medical image analysis",
    "radiology",
    "radiotherapy",
    "mri",
    "computed tomography",
    "ct scan",
    "ultrasound",
    "x-ray",
    "x ray",
    "histopathology",
    "histopathological",

    # Major medical fields
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
    "psychiatric",
    "mental health",
    "infectious disease",
    "epidemiology",
    "public health",

    # COVID / infection
    "covid-19",
    "covid",
    "coronavirus",
    "sars-cov-2",
    "infection",
    "infectious",
    "vaccine",
    "vaccination",

    # Digital health
    "telemedicine",
    "telehealth",
    "digital health",
    "e-health",
    "ehealth",
    "health informatics",
    "medical informatics",

    # Medical devices
    "medical device",
    "medical devices",
    "prosthesis",
    "prosthetic",
    "implant",
    "implants",
    "biomedical engineering"
]


# =========================================================
# Very strong medical phrases
# =========================================================

VERY_STRONG_PHRASES = [

    "medical diagnosis",
    "clinical diagnosis",
    "disease diagnosis",
    "patient diagnosis",

    "medical imaging",
    "medical image analysis",

    "clinical decision support",
    "clinical decision-making",

    "patient monitoring",
    "patient care",

    "cancer detection",
    "cancer diagnosis",
    "tumor detection",
    "tumor diagnosis",

    "disease detection",
    "disease prediction",
    "disease classification",

    "drug discovery",
    "drug delivery",

    "clinical trial",
    "clinical trials",

    "medical data",
    "clinical data",

    "electronic health record",
    "electronic medical record",

    "biomedical engineering",
    "medical informatics",
    "health informatics",

    "medical image segmentation",
    "medical image classification",

    "histopathological image",
    "histopathology image"
]


# =========================================================
# Obvious non-medical contexts
# =========================================================

EXCLUSION_PHRASES = [

    # Networking
    "cellular network",
    "cellular networks",
    "mobile network",
    "mobile networks",
    "wireless network",
    "wireless networks",
    "network cell",
    "network cells",

    # Engineering fault diagnosis
    "fault diagnosis",
    "fault detection",
    "software fault",
    "machine fault",
    "equipment fault",
    "industrial fault",
    "structural fault",
    "power system fault",
    "circuit fault",
    "network diagnosis",
    "traffic diagnosis",

    # Computer science
    "assembly sequence",
    "assembly language",
    "cell assembly",

    # Environmental engineering
    "wastewater treatment",
    "water treatment",
    "waste water treatment",

    # Agriculture
    "crop disease",
    "plant disease",
    "plant pathology",
    "agricultural disease",

    # Materials
    "material treatment",
    "surface treatment",
    "heat treatment",
    "thermal treatment",

    # Mechanical engineering
    "treatment of materials",
    "material processing"
]


def normalize(text):

    text = str(text).lower()

    text = text.replace("-", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_term(text, term):

    term = normalize(term)

    pattern = r"\b" + re.escape(term) + r"\b"

    return bool(re.search(pattern, text))


def count_matches(text, terms):

    count = 0

    for term in terms:

        if contains_term(text, term):

            count += 1

    return count


def is_strictly_medical(record):

    title = normalize(record.get("title", ""))

    abstract = normalize(record.get("abstract", ""))

    keywords = record.get("keywords", [])

    if isinstance(keywords, list):

        keyword_text = " ".join(
            str(k) for k in keywords
        )

    else:

        keyword_text = str(keywords)

    keyword_text = normalize(keyword_text)

    full_text = (
        title
        + " "
        + keyword_text
        + " "
        + abstract
    )


    # -----------------------------------------------------
    # Check exclusions
    # -----------------------------------------------------

    exclusion_count = 0

    for phrase in EXCLUSION_PHRASES:

        if normalize(phrase) in full_text:

            exclusion_count += 1


    # -----------------------------------------------------
    # Count strong medical evidence
    # -----------------------------------------------------

    title_matches = count_matches(
        title,
        STRONG_MEDICAL_TERMS
    )

    keyword_matches = count_matches(
        keyword_text,
        STRONG_MEDICAL_TERMS
    )

    abstract_matches = count_matches(
        abstract,
        STRONG_MEDICAL_TERMS
    )


    phrase_matches = count_matches(
        full_text,
        VERY_STRONG_PHRASES
    )


    # -----------------------------------------------------
    # Medical score from previous stage
    # -----------------------------------------------------

    previous_score = record.get(
        "medical_score",
        0
    )


    # -----------------------------------------------------
    # Decision rules
    # -----------------------------------------------------

    # Rule 1:
    # Strong medical evidence in title
    if title_matches >= 2:

        return True


    # Rule 2:
    # Very strong medical phrase in title
    if count_matches(
        title,
        VERY_STRONG_PHRASES
    ) >= 1:

        return True


    # Rule 3:
    # Medical keywords + abstract evidence
    if keyword_matches >= 2 and abstract_matches >= 2:

        return True


    # Rule 4:
    # Multiple medical concepts across the paper
    if abstract_matches >= 4 and keyword_matches >= 1:

        return True


    # Rule 5:
    # Very strong phrase + supporting evidence
    if phrase_matches >= 1 and abstract_matches >= 2:

        return True


    # Rule 6:
    # High previous score plus medical evidence
    if previous_score >= 30:

        if title_matches >= 1 or keyword_matches >= 1:

            return True


    # -----------------------------------------------------
    # Reject papers dominated by non-medical contexts
    # -----------------------------------------------------

    if exclusion_count >= 2:

        return False


    return False


# =========================================================
# Process dataset
# =========================================================

total = 0

medical_only = 0

removed = 0

invalid = 0


os.makedirs(
    "output",
    exist_ok=True
)


print()
print("Reading scored dataset...")
print()


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as infile:

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as outfile:

        for line in infile:

            line = line.strip()

            if not line:

                continue


            try:

                record = json.loads(line)

                total += 1


                # Only evaluate papers
                # previously classified as medical

                if record.get(
                    "medical",
                    False
                ):

                    if is_strictly_medical(record):

                        outfile.write(
                            json.dumps(
                                record,
                                ensure_ascii=False
                            ) + "\n"
                        )

                        medical_only += 1

                    else:

                        removed += 1


            except Exception:

                invalid += 1


            if total % 100000 == 0:

                print(
                    f"Processed: {total:,}"
                )


# =========================================================
# Final report
# =========================================================

print()
print("=" * 70)
print("STRICT MEDICAL DATASET CREATED")
print("=" * 70)

print(
    f"Scored records checked : {total:,}"
)

print(
    f"Medical candidates     : {total - removed - invalid:,}"
)

print(
    f"Final medical papers   : {medical_only:,}"
)

print(
    f"Removed by strict filter: {removed:,}"
)

print(
    f"Invalid records        : {invalid:,}"
)

print()
print("Output file:")

print(
    os.path.abspath(
        OUTPUT_FILE
    )
)

print("=" * 70)