import unittest
import typesafety

class TestICD10(unittest.TestCase):

    def test_extract(self):
        text = "H35.5 + H90.5 (RP + hearing loss)"
        expected = ['H35.5', 'H90.5']

        self.assertEqual(expected, typesafety.list_icd10(text))
