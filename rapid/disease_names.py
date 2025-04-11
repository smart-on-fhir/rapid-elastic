import csv
from typing import List
from pathlib import Path
from rapid import filetool
from rapid import naming

def map_spellings() -> dict:
    """
    :param deduplicate: deduplicate potential alternate spellings
    :return:
    """
    mapping = dict()
    for file_csv in filetool.CSV_LIST:
        for original in csv_to_list(file_csv):
            _unique = naming.name_unique(original)
            _file = naming.name_file(original)
            _file_lower = naming.name_file(original).lower()
            _spaces = naming.strip_spaces(original)
            _spaces_paren = naming.strip_spaces(naming.strip_paren(original))
            _spaces_paren_lower = naming.strip_spaces(naming.strip_paren(original)).lower()

            if _unique not in mapping.keys():
                mapping[_unique] = list()

            mapping[_unique] += [
                naming.name_file(original),
                naming.name_file(original).lower(),
                naming.strip_spaces(original),
                naming.strip_spaces(naming.strip_paren(original)),
                naming.strip_spaces(naming.strip_paren(original)).lower()]
    return mapping


###############################################################################
# Synonyms
###############################################################################
def prompt_llm_synonyms(disease_json: str) -> Path:
    """
    LLM prompts tried thus far include
        "What are the EHR search terms in clinical note text for exact synonyms of "$disease"
        "What are the EHR search terms in clinical note text for exact synonyms of "$disease""
        "What are the EHR search terms of "$disease"? Respond with JSON where the key is "synonym" or "related" and the values are a list.'

    HUMAN curation by Andy was performed for all diseases, considerable HOURS of careful consideration.
    DO not change the synonyms list unless you are very sure you are fixing a known false positive or false negative hit!
    """
    disease_dict = filetool.read_disease_json(disease_json)
    out = list()
    for disease in disease_dict.keys():
        # out.append(f'What are the EHR search terms in clinical note text for exact synonyms of "{disease}"?')
        prompt = f'What are the EHR search terms of "{disease}"? '
        prompt += f'Respond with JSON where the key is "synonym" or "related" and the values are a list.'
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

###############################################################################
# Convert CSV to JSON
###############################################################################
def csv_to_json_file(disease_csv=None) -> Path | List[Path]:
    if not disease_csv:
        return [csv_to_json_file(i) for i in filetool.CSV_LIST]

    print(f'reading .... {disease_csv}')
    out = csv_to_json(disease_csv)
    print(f"{len(out.keys())} disease names")
    return filetool.write_json(out, filetool.resource(f'{disease_csv}.json'))

def csv_to_list(disease_csv: Path | str) -> List[str]:
    """
    :return: dict with simple identity pair of {disease:disease}
    """
    with open(filetool.resource(disease_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        out = list()
        for row in reader:
            out.append(row['Disease Name'])
        return out

def csv_to_json(disease_csv: Path | str) -> dict:
    """
    :return: dict with simple identity pair of {disease:disease}
    """
    with open(filetool.resource(disease_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        out = {}
        for row in reader:
            disease_name = row['Disease Name']
            disease_name = naming.name_unique(disease_name)
            out[disease_name] = [disease_name]
        return out

###############################################################################
#
# Duplicates and Merging curation lists
#
###############################################################################
def find_duplicates_across_sheets() -> Path:
    """
    Deprecated status: this has been done and reviewed manually by Andy
    :return: path to duplicates found
    """
    merged = dict()
    duplicates = dict()

    for filename_csv in filetool.CSV_LIST:
        from_json = filetool.read_disease_json(f'{filename_csv}.json')
        for disease, _ in from_json.items():
            disease = naming.name_unique(disease)
            disease = disease.lower()
            disease = disease.replace('-', ' ')

            if disease in merged.keys():
                print(f'duplicate: {disease}')
                merged[disease].append(filename_csv)

                if disease not in duplicates.keys():
                    duplicates[disease] = merged[disease]
            else:
                merged[disease] = [filename_csv]
    print(f'{len(duplicates.keys())}  "duplicates found"')
    return filetool.write_json(duplicates, filetool.resource('disease_names_duplicates.json'))

def merge(filename_json: str) -> Path:
    """
    Deprecated status: this has been done and reviewed manually by Andy
    :param filename_json: JSON to merge with the CSV names.
    :return: Path to merged file
    """
    original = filetool.read_disease_json(filename_json)
    original_keys = [key.lower() for key in original.keys()]
    merged = original

    for filename_csv in filetool.CSV_LIST:
        from_json = filetool.read_json(filetool.resource(f'{filename_csv}.json'))
        for disease, synonyms in from_json.items():
            disease.lower()
            if disease.lower() not in original_keys:
                print(f'merge: {disease}')
                merged[disease] = synonyms

    return filetool.write_json(merged, filetool.resource('disease_names_merged.json'))
