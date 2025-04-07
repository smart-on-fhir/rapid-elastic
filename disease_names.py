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

def disease_names_csv(filename_csv=None) -> Path | List[Path]:
    if not filename_csv:
        return [disease_names_csv(i) for i in CSV_LIST]

    print(f'reading .... {filename_csv}')
    out = dict_disease_names(filename_csv)
    print(f"{len(out.keys())} disease names")
    return filetool.write_json(out, filetool.resource(f'{filename_csv}.json'))

def disease_names_json(filename_json: Path | str) -> dict:
    return filetool.read_json(filetool.resource(filename_json))

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
    original = filetool.read_json(filetool.resource('disease_names_csv.json'))
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
        # out.append(f'What are the EHR search terms in clinical note text for exact synonyms of "{disease}"?')
        prompt = f'What are the synonyms of "{disease}"?'
        prompt += f'Respond with JSON where the key is "exact" or "related" and the values are a list.'
        out.append(prompt)
    out = '\n'.join(out)
    return filetool.write_text(out, filetool.resource(f'{disease_json}.prompts.txt'))

def expand(phrase: str, search: str, replace_list: list) -> list:
    if search in phrase:
        return [phrase.replace(search, repl) for repl in replace_list]

def expand_all(disease_json: str | Path) -> Path:
    """
    :param disease_json: filename of curated disease names and synyms
    :return: LVG (lexical variant generated) expressions
    """
    disease_dict = filetool.read_json(filetool.resource(disease_json))
    expanded = dict()
    for disease, synonyms in disease_dict.items():
        expanded[disease] = list()
        lvg = list()

        for syn in synonyms:
            lvg.append(syn)
            if '-' in syn:
                lvg.append(syn.replace('-', ' '))

            syn = syn.lower()

            if 'microdeletion' in syn:
                lvg += expand(syn, 'microdeletion', ['deletion', 'deficiency', 'mutation', 'variant', 'pathogenic'])
            elif 'deletion' in syn:
                lvg += expand(syn, 'deletion', ['deficiency', 'mutation', 'variant', 'pathogenic'])
            if 'mutation' in syn:
                lvg += expand(syn, 'mutation', ['gene mutation', 'pathogenic', 'variant'])
            if 'variant' in syn:
                lvg += expand(syn, 'variant', ['gene mutation', 'pathogenic', 'mutation'])

        expanded[disease] = sorted(list(set(lvg)))
    return filetool.write_json(expanded, filetool.resource('disease_names_expanded.json'))


if __name__ == '__main__':
    llm_prompt_synonyms('disease_names_expanded.json')
    # disease_names_csv()
    # find_duplicates()
    # merge()

    # print(expand("DTNA mutation", "mutation", ["mutation", "variant", "pathogenic"]))
    # print(expand_all('disease_names_merged.json'))
