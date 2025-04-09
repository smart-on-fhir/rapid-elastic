import unittest
import disease_names

class TestDiseaseNames(unittest.TestCase):

    def test_expand(self):
        expected = ['ABCD1 mutation', 'ABCD1 variant', 'ABCD1 pathogenic']
        actual = disease_names.expand("ABCD1 mutation", "mutation", ["mutation", "variant", "pathogenic"])
        self.assertEqual(expected, actual)

    @unittest.skip
    def test_find_duplicates(self):
        disease_names.deprecated_find_duplicates()

    @unittest.skip('Merge curated JSON with names from the CSV spreadsheets')
    def test_deprecated_merge(self):
        disease_names.deprecated_merge('disease_names.json')