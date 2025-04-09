import unittest
import kql_syntax
import filetool

class TestQuerystring(unittest.TestCase):
    def test_generator(self):
        disease_json = filetool.read_json(filetool.resource('disease_names_expanded.json'))

        for disease, keyword_list in disease_json.items():
            as_string = kql_syntax.match_phrase_any(keyword_list)
            as_json = kql_syntax.query_string(as_string)
            print(as_json)


if __name__ == '__main__':
    unittest.main()
