from typing import List
from pathlib import Path
import re
import csv
import filetool
import naming

class DiseaseICD10:
    """
    Content from curated spreadsheet
    "ARPA-H Rare Disease Prioritization via ChatGPT with GIC counts"
    https://docs.google.com/spreadsheets/d/1lNgKOyt1cK_cTA72WbywsjjrvWCM0HUpv1nMFqKEngM/edit?gid=217264283#gid=217264283
    """
    disease_name: str = None
    orpha_code: str = None
    icd10_list: List[str] = None

    def __init__(self,
                 disease_name: str,
                 orpha_code: str | None,
                 icd10_list: List[str] | None):
        self.disease_name = disease_name
        self.orpha_code = orpha_code
        self.icd10_list = icd10_list

    def to_sql(self) -> List[str]:
        out = list()
        for icd10 in self.icd10_list:
            out.append(f"('{self.disease_name}', '{self.orpha_code}', '{icd10}')")
        return out

def list_icd10(snippet: str) -> List:
    """
    :return: List ICD10 codes from human curated spreadsheets
    """
    pattern = r'\b[A-Z][0-9]{2}(?:\.[0-9]{1,3})?\b'
    return re.findall(pattern, snippet)

def list_entries(disease_csv: Path | str) -> List[DiseaseICD10]:
    """
    :param disease_csv: downloaded spreadsheet.csv file
    :return: List of parsed DiseaseICD10 entries
    """
    with open(filetool.resource(disease_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)  # skip header
        out = list()
        for row in reader:
            disease_name = naming.strip_paren(row['Disease Name'])
            orpha_code = row['Orpha Code(s)']
            icd10_list = list_icd10(row['ICD-10 Code(s)'])

            out.append(DiseaseICD10(disease_name, orpha_code, icd10_list))
        return out

def list_to_sql(table: str, entry_list: List[DiseaseICD10]) -> str:
    """
    :param table: Table name to create in Athena
    :param entry_list: list of entries to create in Athena
    :return: str SQL of disease_name, orpha_code, icd10_code
    """
    header = f"create or replace view {table} as select * from (values"
    footer = ") AS t (disease_name, orpha_code, icd10_code) ;"
    rows = list()
    for entry in entry_list:
        rows += entry.to_sql()
    out = '\n,'.join(rows)
    return header + '\n' + out + '\n' + footer

def csv_to_sql(disease_csv: str) -> Path:
    """
    :param disease_csv: read disease_csv: downloaded spreadsheet.csv file
    :return: Path to SQL file
    """
    table = naming.name_table(disease_csv.replace('.csv', ''))
    entries = list_entries(disease_csv)
    sql = list_to_sql(table, entries)
    return Path(filetool.write_text(sql, filetool.output(f'{table}.sql')))
