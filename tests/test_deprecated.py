import unittest
import unittest
from rapid import filetool
from rapid import naming
from rapid import disease_icd10
from rapid import disease_names


class TestDeprecated(unittest.TestCase):
    """
    Will delete these methods, these are temporary for ability to look backwards before
    "New Master 04-13-2025.csv"
    """
    @unittest.skip('disease_names_duplicates.json')
    def test_find_duplicates(self):
        """
        Enable this test to list which GPT4 suggested rare diseases might be in multiple spreadsheets.
        HUMAN curation is complete. For historical purposes.
        """
        print(disease_names.deprecated_find_duplicates_across_sheets())

    @unittest.skip('disease_names_spelling.json')
    def test_spelling(self):
        """
        For historical purposes. GPT4o did not consistently name disease names and our outputs sometimes were duplicated.
        Use this file to get a list of disease names that could have been used previously.
        """
        filetool.write_json(
            disease_names.map_spellings(),
            filetool.resource('disease_names_spelling.json'))

    @unittest.skip('disease_names_legacy.json')
    def test_deprecated_differences(self):
        disease_list = disease_names.list_unique(filetool.DISEASES_CSV)
        disease_json = filetool.read_json(filetool.deprecated('disease_names_expanded.json'))
        legacy = dict()

        for key, synonyms in disease_json.items():
            curated = naming.name_unique(key)
            if curated in disease_list:
                legacy[curated] = synonyms
            else:
                print(f'{curated} (not found!)')
        print(f'{len(legacy.keys())} matches found')
        filetool.write_json(legacy, filetool.resource('disease_names_legacy.json'))
