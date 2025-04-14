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
        out = list()
        for row in reader:
            disease_name = naming.name_unique(row['Disease Name'])
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

def csv_to_sql(filename_csv: str) -> Path:
    """
    :param filename_csv: read disease_csv: downloaded spreadsheet.csv file
    :return: Path to SQL file
    """
    table = naming.name_table(filename_csv.replace('.csv', ''))
    entries = list_entries(filename_csv)
    sql = list_to_sql(table, entries)
    return Path(filetool.write_text(sql, filetool.resource(f'{filename_csv}.sql')))

def union_views() -> str:
    table_list = list()
    sheet_list = [f.replace('.csv', '') for f in filetool.CSV_LIST]

    for sheet in sheet_list:
        table_name = naming.name_table(sheet)
        table_list.append(table_name)

    create = f"create or replace view {naming.name_table('CODES')} AS \n"
    select = [f"select '{t}' as sheet, * from {t}" for t in table_list]
    out = create + '\n UNION \n'.join(select)
    return out
