import unittest
from rapid import kql_syntax, filetool


class TestQuerystring(unittest.TestCase):

    def test_generator(self):
        disease_json = filetool.read_disease_json('disease_names_expanded.json')

        for disease, keyword_list in disease_json.items():
            as_string = kql_syntax.match_phrase_any(keyword_list)
            as_json = kql_syntax.query_string(as_string)
            print(as_json)
