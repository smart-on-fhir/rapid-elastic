from typing import List
from pathlib import Path
import timestamp
import filetool
import elastic_helper
import kql_syntax
import naming

###############################################################################
# Pipeline for a single rare-disease disease query
###############################################################################
def pipe_query(disease, query: str | List[str]) -> List[Path]:
    """
    :param disease: example "Sanfilippo syndrome"
    :param query: str prepared KQL query, List[str] synonyms to prepare KQL query for you.
    :return: List of elasticsearch results written to disk, a CSV file and a JSON file
    """
    disease = naming.strip_spaces(disease)

    if filetool.output(f'{disease}.csv').exists() or filetool.output(f'{disease}.csv.gz').exists():
        print(f'"{disease}" already processed')
        return filetool.list_output(disease)
    else:
        print(f'"{disease}" processing')

    if isinstance(query, list):
        query = kql_syntax.match_phrase_any(query)

    _time1 = timestamp.datetime.now()
    #
    all_hits = elastic_helper.get_hits(query)
    #
    _time2 = timestamp.datetime.now()

    print("Elastic took: ", timestamp.diff_seconds(_time1, _time2), ' seconds')
    print(f'{len(all_hits)} hits to process')

    entry_list = list()

    for hit in all_hits:
        entry_list.append(
            elastic_helper.ElasticHit(hit['_source']))

    print(f'{len(entry_list)} entries processed')

    output_csv = elastic_helper.ElasticHit.list_to_csv(entry_list)
    output_json = {'request': query,
                   'total': len(all_hits),
                   'hits': [e.as_json() for e in entry_list]}

    return [filetool.write_json(output_json, filetool.output(f'{disease}.json')),
            filetool.write_text(output_csv, filetool.output(f'{disease}.csv'))]

###############################################################################
# Pipeline using file of saved disease names
###############################################################################

def pipe_file(disease_filename_json='disease_names_expanded.json') -> List[Path]:
    disease_dict = filetool.read_disease_json(disease_filename_json)

    print(f'{len(disease_dict.keys())} rare-diseases, processing now....')
    print(disease_dict)

    file_list = list()

    _pipe_begin = timestamp.datetime.now()
    print("Begin: ", timestamp.to_string(_pipe_begin))

    for disease, keyword_list in disease_dict.items():
        file_list += pipe_query(disease, keyword_list)

    _pipe_done = timestamp.datetime.now()
    print("Done: ", timestamp.to_string(_pipe_begin))
    print("Took: ", timestamp.diff_seconds(_pipe_begin, _pipe_done))
    return file_list


###############################################################################
#
# MAIN
#
###############################################################################
if __name__ == "__main__":
    pipe_file('disease_names_expanded.json')
