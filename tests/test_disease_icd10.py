import unittest
from rapid_elastic import disease_icd10, filetool


class TestDiseaseICD10(unittest.TestCase):
    def test_list_icd10(self):
        text = "H35.5 + H90.5 (RP + hearing loss)"
        expected = ['H35.5', 'H90.5']

        self.assertEqual(expected, disease_icd10.list_icd10(text))

    def test_list_orpha(self):
        text = "ORPHA:558;ORPHA:284963; ORPHA:284973; ORPHA:284993"
        expected_int = [558, 284963, 284973, 284993]
        expected_str = ['558', '284963', '284973', '284993']

        self.assertEqual(expected_int, disease_icd10.list_orpha(text, as_int=True))
        self.assertEqual(expected_str, disease_icd10.list_orpha(text, as_int=False))

    @unittest.skip('rapid__codeset.sql')
    def test_csv_to_sql(self, csv_file=filetool.DISEASES_CSV):
        print(disease_icd10.csv_to_sql(csv_file))
