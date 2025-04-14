import unittest
from rapid import naming, disease_icd10, filetool


class TestDiseaseICD10(unittest.TestCase):
    def test_list_icd10(self):
        text = "H35.5 + H90.5 (RP + hearing loss)"
        expected = ['H35.5', 'H90.5']

        self.assertEqual(expected, disease_icd10.list_icd10(text))

    def test_entries(self):
        for csv_file in filetool.DEPRECATED_CSV_LIST:
            entries = disease_icd10.list_entries(csv_file)
            table = naming.name_table(csv_file.replace('.csv', ''))
            out = disease_icd10.list_to_sql(table, entries)
            print(out)

    # @unittest.skip("write output SQL files for each disease.csv file")
    def test_csv_to_sql(self):
        for csv_file in filetool.DEPRECATED_CSV_LIST:
            file_sql = disease_icd10.csv_to_sql(csv_file)
            print(file_sql)
