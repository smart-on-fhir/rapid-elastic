from typing import List
from pathlib import Path
import re
import csv
from rapid import filetool
from rapid import naming

class DiseaseICD10:
    """
    Content from curated spreadsheet
    "ARPA-H Rare Disease Prioritization via ChatGPT with GIC counts"
    https://docs.google.com/spreadsheets/d/1lNgKOyt1cK_cTA72WbywsjjrvWCM0HUpv1nMFqKEngM/edit?gid=217264283#gid=217264283
    """
    disease_name: str = None
    orpha_list: List[str] = None
    icd10_list: List[str] = None

    def __init__(self,
                 disease_name: str,
                 orpha_list: List[str] | None,
                 icd10_list: List[str] | None):
        self.disease_name = disease_name
        self.orpha_list = orpha_list
        self.icd10_list = icd10_list

    def to_sql(self) -> List[str]:
        out = list()
        disease_alias = naming.name_table_alias(self.disease_name)
        if self.icd10_list:
            for icd10 in self.icd10_list:
                if self.orpha_list:
                    for orpha in self.orpha_list:
                        out.append(f"('{self.disease_name}', '{orpha}', '{icd10}', '{disease_alias}')")
                else:
                    out.append(f"('{self.disease_name}', 'NULL', '{icd10}', '{disease_alias}')")
        else:
            out.append(f"('{self.disease_name}', 'NULL', 'NULL', '{disease_alias}')")
        return out

def list_icd10(snippet: str) -> List:
    """
    :return: List ICD10 codes from human curated spreadsheets
    """
    pattern = r'\b[A-Z][0-9]{2}(?:\.[0-9]{1,3})?\b'
    return re.findall(pattern, snippet)

def list_orpha(snippet: str, as_int=False) -> List:
    """
    :param as_int: Strict integer response (good for testing)
    :return: :return: List ICD10 codes from human curated spreadsheets
    """
    matches = re.findall(r'ORPHA:(\d+)', snippet)
    if as_int:
        return [int(m) for m in matches]
    return matches

def list_entries(disease_csv: Path | str) -> List[DiseaseICD10]:
    """
    :param disease_csv: downloaded spreadsheet.csv file
    :return: List of parsed DiseaseICD10 entries
    """
    with open(filetool.resource(disease_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        out = list()
        for row in reader:
            disease_name = naming.name_unique(row['Disease Name'])
            orpha_code = list_orpha(row['Orphanet'])    # legacy Orpha Code(s)
            icd10_list = list_icd10(row['ICD-10'])      # legacy ICD-10 Code(s)

            out.append(DiseaseICD10(disease_name, orpha_code, icd10_list))
        return out

def list_to_sql(table: str, entry_list: List[DiseaseICD10]) -> str:
    """
    :param table: Table name to create in Athena
    :param entry_list: list of entries to create in Athena
    :return: str SQL of disease_name, orpha_code, icd10_code
    """
    header = f"create or replace view {table} as select * from (values"
    footer = ") AS t (disease_name, orpha_code, icd10_code, disease_alias) ;"
    rows = list()
    for entry in entry_list:
        rows += entry.to_sql()
    out = '\n,'.join(rows)
    return header + '\n' + out + '\n' + footer

def csv_to_sql(filename_csv: str) -> Path:
    """
    :param filename_csv: read disease_csv: downloaded spreadsheet.csv file
    :return: Path to SQL file
    """
    table = 'rapid__codeset'
    entries = list_entries(filename_csv)
    sql = list_to_sql(table, entries)
    return Path(filetool.write_text(sql, filetool.resource(f'{table}.sql')))
