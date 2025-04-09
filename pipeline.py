from typing import List
from pathlib import Path
from datetime import datetime
import filetool
import elastic_helper
import kql_syntax
import naming

def get_timestamp() -> str:
    """
    Timestamp to measure see long Elasticsearch takes
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def process(disease, query: str | List[str]) -> List[Path]:
    """
    :param disease: 
    :param query: str prepared KQL query, List[str] will prepare KQL query for you.   
    :return: 
    """
    if filetool.output(f'{disease}.csv').exists() or filetool.output(f'{disease}.csv.gz').exists():
        print(f'"{disease}" already processed')
        return filetool.list_output(disease)
    else:
        print(f'"{disease}" processing')

    if isinstance(query, list):
        query = kql_syntax.match_phrase_any(keyword_list)

    all_hits = elastic_helper.get_hits(query)
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

    filetool.write_json(output_json, filetool.output(f'{disease}.json'))
    filetool.write_text(output_csv, filetool.output(f'{disease}.csv'))


###############################################################################
#
# MAIN query elastic and write results
#
###############################################################################
if __name__ == "__main__":
    disease_json = filetool.read_disease_json('disease_names_expanded.json')

    print(f'{len(disease_json.keys())} rare-diseases, processing now....')
    print(disease_json)

    print("Started @:", get_timestamp())

    for disease, keyword_list in disease_json.items():
        disease = naming.strip_spaces(disease)

        process(disease, keyword_list)

    print("Finished @:", get_timestamp())
