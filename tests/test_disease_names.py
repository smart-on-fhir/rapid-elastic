import unittest

from rapid_elastic import filetool
from rapid_elastic import naming
from rapid_elastic import disease_names


class TestDiseaseNames(unittest.TestCase):

    def test_table_alias(self):
        """
        Testing LLM initial selection
        """
        expected = sorted([
            'noonan_syndrome',
            'carbamoyl_phosphate_synthetase_i_deficiency',
            'beckwith_wiedemann_syndrome',
            'pompe_disease',
            'angelman_syndrome'])

        actual = naming.name_table_alias([
            'Noonan syndrome',
            'Carbamoyl phosphate synthetase I deficiency(CPS1)',
            'Beckwith-Wiedemann syndrome',
            'Pompe disease(infantile)',
            'Angelman syndrome'])

        self.assertEqual(sorted(expected), sorted(actual))

    def test_unique(self):
        """
        Test that CSV input sheets are mapped in `disease_names_expanded.json`
        """
        spellings = disease_names.list_unique()
        disease_json = filetool.read_disease_json()
        disease_list = naming.name_unique(list(disease_json.keys()))

        _inter = set(spellings).intersection(set(disease_list))
        _diff1 = set(spellings).difference(set(disease_list))
        _diff2 = set(disease_list).difference(set(spellings))

        if len(_diff1) > 0:
            print(len(_diff1), '  .difference() ', 'missing?', str(_diff1))

        if len(_diff2) > 0:
            print(len(_diff2), '  .difference() ', 'deprecated?', str(_diff2))

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

    @unittest.skip('prompts.txt')
    def test_prompt_llm_synonyms(self, diseases_csv=filetool.DISEASES_CSV):
        """
        Enable this test to produce GPT4 suggestions.
        HUMAN curation is complete. For historical purposes.
        """
        print(disease_names.prompt_llm_synonyms(diseases_csv))
