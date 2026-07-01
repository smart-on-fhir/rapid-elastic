import unittest
from rapid_elastic import kql_syntax, filetool

def generate(filename_json='disease_names_expanded.json'):
    disease_json = filetool.read_query_topics_json(filetool.path_resource(filename_json))
    query_json = dict()
    query_list = list()

    for disease, keyword_list in disease_json.items():
        as_string = kql_syntax.match_phrase_any(keyword_list)
        as_json = kql_syntax.query_string(as_string)
        query_json[disease] = as_json
        query_list.append(str(as_json))

    filetool.write_text('\n'.join(query_list), filetool.path_resource(f'{filename_json}.query.txt'))
    filetool.write_json(query_json, filetool.path_resource(f'{filename_json}.query.json'))

##########################################
# Test (optional)
##########################################
class TestQuerystring(unittest.TestCase):
    # @unittest.skip('query.json, query.txt')
    def test_generator(self, filename_json='query_synonyms.json'):
        generate(filename_json)