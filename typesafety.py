from typing import List
from pathlib import Path
import re
import csv
import filetool

TABLE_PREFIX = "cohorts__rare"

###############################################################################
# ICD10 mappings
###############################################################################
class DiseaseICD10:
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

    @classmethod
    def list_entries(cls, disease_csv: Path | str) -> List:
        with open(filetool.resource(disease_csv), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            next(reader)  # skip header
            out = list()
            for row in reader:
                out.append(DiseaseICD10(disease_name=strip_paren(row['Disease Name']),
                                        orpha_code=row['Orpha Code(s)'],
                                        icd10_list=list_icd10(row['ICD-10 Code(s)'])))
            return out

    def to_sql(self) -> List[str]:
        out = list()
        for icd10 in self.icd10_list:
            out.append(f"('{self.disease_name}', '{self.orpha_code}', '{icd10}')")
        return out

    @classmethod
    def list_to_sql(cls, table: str, entry_list: List) -> str:
        header = f"create or replace view {table} as select * from (values"
        footer = ") AS t (disease_name, orpha, icd10) ;"
        rows = list()
        for entry in entry_list:
            rows += entry.to_sql()
        out = '\n,'.join(rows)
        return header + '\n' + out + '\n' + footer


###############################################################################
# Elasticsearch
###############################################################################
class SearchHit:
    """
    # Class to wrap ElasticSearch responses for only columns we need.
    """
    HEADERS = ['subject_ref', 'encounter_ref', 'document_ref', 'group_name', 'document_title']
    _timestamp: str = ''
    group_name: str = ''
    anon_ref: str = ''
    anon_subject_ref: str = ''
    anon_encounter_ref: str = ''
    doc_code_text: str = ''
    doc_codes: dict = {}

    def __init__(self, from_source: dict):
        self.group_name = from_source.get('group_name', '')
        self.anon_ref = from_source.get('anon_ref', '')
        self.anon_subject_ref = from_source.get('anon_subject_ref', '')
        self.anon_encounter_ref = from_source.get('anon_encounter_ref', '')
        self._timestamp = from_source.get('@timestamp', '')
        self.doc_codes = from_source.get('codes', dict())
        if self.doc_codes:
            self.doc_code_text = from_source.get('codes').get('text').replace(',', '|')

    def to_csv(self) -> str:
        out = [self.anon_subject_ref,
               self.anon_encounter_ref,
               self.anon_ref,
               self.group_name,
               self.doc_code_text]
        return ','.join(out)

    @classmethod
    def list_to_csv(cls, entry_list: List) -> str:
        output_csv = ','.join(SearchHit.HEADERS) + '\n'
        output_csv += '\n'.join([e.to_csv() for e in entry_list])
        return output_csv

###############################################################################
# Disease Names
###############################################################################
def strip_spaces(disease: str, remove_parens=False):
    return disease.replace(' ', '_')

def strip_paren(disease: str) -> str:
    # Replace anything in parentheses (non-greedy match)
    # Autosomal Recessive Polycystic Kidney Disease (ARPKD) -->
    # Autosomal Recessive Polycystic Kidney Disease
    return re.sub(r"\s*\([^)]*\)", "", disease)

###############################################################################
# ICD10
###############################################################################
def name_table(table: list | str) -> list | str:
    if isinstance(table, list):
        return [f'{TABLE_PREFIX}__{table}' for table in list(set(table))]
    else:
        return f'{TABLE_PREFIX}__{table}'

# List ICD10 codes from human curated spreadsheets
def list_icd10(snippet: str) -> List:
    pattern = r'\b[A-Z][0-9]{2}(?:\.[0-9]{1,3})?\b'
    return re.findall(pattern, snippet)
