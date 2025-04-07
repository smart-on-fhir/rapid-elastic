import re
import csv
from typing import List
from pathlib import Path
import filetool

CSV_LIST = ["UNIQUE_LT10_PER_100K.csv",
            "UNIQUE_LT50_PER_100K.csv",
            "BROAD_LT10_PER_100K.csv",
            "BROAD_LT50_PER_100K.csv"]

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease)

def clean_name(disease: str) -> str:
    return strip_paren(disease).replace('-', ' ')

def dict_disease_names(disease_csv: Path | str) -> dict:
    with open(filetool.resource(disease_csv), newline='') as csvfile:
        reader = csv.reader(csvfile)
        out = {}

        # Optional: skip header if presentf
        headers = next(reader)
        # print(headers)

        # Loop through rows
        for row in reader:
            # Each row is a list of column values
            # print(row)          # Full row as list
            disease_name = row[0]
            disease_name = strip_paren(disease_name)

            # initialize search keywords only with self
            out[disease_name] = [disease_name]
        return out

def disease_names(filename_csv=None) -> Path | List[Path]:
    if not filename_csv:
        return [disease_names(i) for i in CSV_LIST]

    print(f'reading .... {filename_csv}')
    out = dict_disease_names(filename_csv)
    print(f"{len(out.keys())} disease names")
    return filetool.write_json(out, filetool.resource(f'{filename_csv}.json'))

def find_duplicates():
    merged = dict()
    duplicates = dict()

    for filename_csv in CSV_LIST:
        from_json = filetool.read_json(filetool.resource(f'{filename_csv}.json'))
        for disease, _ in from_json.items():
            disease = strip_paren(disease)
            disease = disease.lower()
            disease = disease.replace('-', ' ')

            if disease in merged.keys():
                print(f'duplicate: {disease}')
                merged[disease].append(filename_csv)

                if disease not in duplicates.keys():
                    duplicates[disease] = merged[disease]
            else:
                merged[disease] = [filename_csv]

    # duplicates = sorted(duplicates)
    print(f'{len(duplicates.keys())}  "duplicates found"')
    return filetool.write_json(duplicates, filetool.resource('disease_names_duplicates.json'))

def merge():
    original = filetool.read_json(filetool.resource('disease_names.json'))
    original_keys = [key.lower() for key in original.keys()]
    merged = original

    for filename_csv in CSV_LIST:
        from_json = filetool.read_json(filetool.resource(f'{filename_csv}.json'))
        for disease, synonyms in from_json.items():
            disease.lower()
            if disease.lower() not in original_keys:
                print(f'merge: {disease}')
                merged[disease] = synonyms

    return filetool.write_json(merged, filetool.resource('disease_names_merged.json'))

def llm_prompt_synonyms(disease_json: str | Path) -> str:
    disease_dict = filetool.read_json(filetool.resource(disease_json))
    out = list()
    for disease in disease_dict.keys():
        out.append(f'What are the EHR search terms in clinical note text for exact synonyms of "{disease}"?')
    out = '\n'.join(out)
    return filetool.write_text(out, filetool.resource(f'{disease_json}.prompts.txt'))


if __name__ == '__main__':
    # disease_names()
    # find_duplicates()
    # merge()
    llm_prompt_synonyms('disease_names_merged.json')
