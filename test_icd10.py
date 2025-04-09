import unittest
from typing import List
from pathlib import Path
import csv
import filetool
import typesafety

class TestICD10(unittest.TestCase):
    def test(self):
        # define_icd10('UNIQUE_LT10_PER_100K.csv')
        filename = 'UNIQUE_LT10_PER_100K.csv'
        entries = typesafety.DiseaseICD10.list_entries(filename)
        table = typesafety.name_table('UNIQUE_LT10_PER_100K')
        out = typesafety.DiseaseICD10.list_to_sql(table, entries)
        print(out)
