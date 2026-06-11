import unittest
from rapid_elastic import filetool

class TestDiseaseNames(unittest.TestCase):

    def test_synonynms_no_query_intersection(self):
        """
        Test that there are no overlapping search terms between diseases.
        This test should be considered optional depending on your use case.
        You may want to have superset queries like "genetic mutation" and "TCF4 genetic mutation"
        """
        disease_json = filetool.read_query_topics()

        for disease, syn_list in disease_json.items():
            syn_list_lower = [s.lower() for s in syn_list]
            disease_json[disease] = syn_list_lower

        for disease1, syn_list1 in disease_json.items():
            for disease2, syn_list2 in disease_json.items():
                if disease1 != disease2:
                    overlap = set(syn_list1).intersection(set(syn_list2))

                    # Urea Cycle Disorders is a known "catch all" category with overlaps
                    if 'dx_urea_cycle_disorders' not in [disease1, disease2]:
                        self.assertTrue(
                            len(overlap) == 0,
                            f'search term(s) {overlap} overlap for "{disease1}" and "{disease2}"')
