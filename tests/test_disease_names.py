import unittest
from rapid import filetool
from rapid import naming
from rapid import disease_names


class TestDiseaseNames(unittest.TestCase):

    def test_expand(self):
        """
        Test that "mutation" LVG lexical variant generation for search phrase construction
        """
        expected = ['ABCD1 mutation', 'ABCD1 variant', 'ABCD1 pathogenic']
        actual = disease_names.expand("ABCD1 mutation", "mutation", ["mutation", "variant", "pathogenic"])
        self.assertEqual(expected, actual)

    @unittest.skip
    def test_expand_all(self):
        print(disease_names.expand_all('disease_names.json'))

    def test_unique(self):
        """
        Test that CSV input sheets are mapped in `disease_names_expanded.json`
        """
        spellings = disease_names.list_unique()
        disease_json = filetool.read_disease_json()
        disease_list = naming.name_unique(list(disease_json.keys()))

        _inter = set(spellings).intersection(set(disease_list))
        # print(len(_inter), ' .intersect() ')

        _diff1 = set(spellings).difference(set(disease_list))
        if len(_diff1) > 0:
            print(len(_diff1), '  .difference() ', 'missing?', str(_diff1))

        _diff2 = set(disease_list).difference(set(spellings))
        if len(_diff2) > 0:
            print(len(_diff2), '  .difference() ', 'deprecated?', str(_diff2))

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

    @unittest.skip('disease_names.json')
    def test_update(self):
        disease_list = disease_names.list_unique(filetool.DISEASES_CSV)
        legacy_json = filetool.read_json(filetool.deprecated('disease_names_expanded.json'))
        merged = dict()

        for disease in disease_list:
            if disease in legacy_json.keys():
                merged[disease] = legacy_json[disease]
                print(f'{disease} (matched)')
            else:
                merged[disease] = [disease]
                print(f'{disease} (?missing?)')

        filetool.write_json(merged, filetool.resource('disease_names.json'))

    def test_synonynms_no_query_intersection(self):
        """
        Test that there are no overlapping search terms between diseases.
        """
        _unexpected = set()
        disease_json = filetool.read_disease_json()

        for disease, syn_list in disease_json.items():
            syn_list_lower = [s.lower() for s in syn_list]
            disease_json[disease] = syn_list_lower

        for disease1, syn_list1 in disease_json.items():
            for disease2, syn_list2 in disease_json.items():
                if disease1 != disease2:
                    _inter = set(syn_list1).intersection(set(syn_list2))
                    self.assertTrue(
                        len(_inter) == 0,
                        f'search term(s) {_inter} overlap for "{disease1}" and "{disease2}"')

    @unittest.skip('disease_names_spelling.json')
    def test_spelling(self):
        """
        For historical purposes. GPT4o did not consistently name disease names and our outputs sometimes were duplicated.
        Use this file to get a list of disease names that could have been used previously.
        """
        filetool.write_json(
            disease_names.map_spellings(),
            filetool.resource('disease_names_spelling.json'))

    @unittest.skip('prompts.txt')
    def test_prompt_llm_synonyms(self, diseases_csv=filetool.DISEASES_CSV):
        """
        Enable this test to produce GPT4 suggestions.
        HUMAN curation is complete. For historical purposes.
        """
        print(disease_names.prompt_llm_synonyms(diseases_csv))

    @unittest.skip('disease_names_duplicates.json')
    def test_find_duplicates(self):
        """
        Enable this test to list which GPT4 suggested rare diseases might be in multiple spreadsheets.
        HUMAN curation is complete. For historical purposes.
        """
        print(disease_names.deprecated_find_duplicates_across_sheets())
