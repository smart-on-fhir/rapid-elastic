import unittest
from rapid import filetool
from rapid import naming
from rapid import disease_icd10
from rapid import disease_names
from rapid import sql_compare


class TestDeprecated(unittest.TestCase):
    """
    Will delete these methods, these are temporary for ability to look backwards before
    "New Master 04-13-2025.csv"
    """
    def test_curated_csv_exists(self):
        for curated_csv in filetool.DEPRECATED_CSV_LIST:
            self.assertTrue(filetool.deprecated(curated_csv).exists())

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

    @unittest.skip('rapid__codeset.sql')
    def test_union_views_codeset_icd10(self):
        tables_list = [t.replace('.csv', '') for t in filetool.DEPRECATED_CSV_LIST]
        tables_list = [naming.name_cohort(f'codeset_{t}') for t in tables_list]
        print(sql_compare.union_views_file(
            create='rapid__codeset',
            table_list=tables_list,
            create_table=True,
            alias_col='source_csv'))

