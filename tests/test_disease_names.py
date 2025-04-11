import unittest
from collections import OrderedDict

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

    def test_unique(self):
        """
        Test that CSV input sheets are mapped in `disease_names_expanded.json`
        """
        spellings = disease_names.map_spellings()
        disease_json = filetool.read_disease_json()
        disease_list = naming.name_unique(list(disease_json.keys()))

        _inter = set(spellings.keys()).intersection(set(disease_list))
        # print(len(_inter), ' .intersect() ')

        _diff1 = set(spellings.keys()).difference(set(disease_list))
        if len(_diff1) > 0:
            print(len(_diff1), '  .difference() ', 'missing?', str(_diff1))

        _diff2 = set(disease_list).difference(set(spellings.keys()))
        if len(_diff2) > 0:
            print(len(_diff2), '  .difference() ', 'deprecated?', str(_diff2))

    def test_synonynms_no_intersection(self):
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
                    if len(_inter) > 0:
                        print(f'warn: search term(s) {_inter} overlap for "{disease1}" and "{disease2}"')

    @unittest.skip('resources/disease_names_spelling.json')
    def test_spelling(self):
        """
        For historical purposes. GPT4o did not consistently name disease names and our outputs sometimes were duplicated.
        Use this file to get a list of disease names that could have been used previously.
        """
        filetool.write_json(
            disease_names.map_spellings(),
            filetool.resource('disease_names_spelling.json'))

    @unittest.skip
    def test_prompt_llm_synonyms(self):
        """
        Enable this test to produce GPT4 suggestions.
        HUMAN curation is complete. For historical purposes.
        """
        print(disease_names.prompt_llm_synonyms('disease_names_expanded.json'))

    @unittest.skip
    def test_find_duplicates(self):
        """
        Enable this test to list which GPT4 suggested rare diseases might be in multiple spreadsheets.
        HUMAN curation is complete. For historical purposes.
        """
        disease_names.find_duplicates_across_sheets()
