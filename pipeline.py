from typing import List
from pathlib import Path
from datetime import datetime
import filetool
import elastic_helper
import kql_syntax
import typesafety

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def process(disease, querystring) -> List[Path]:

    if filetool.output(f'{disease}.csv').exists() or filetool.output(f'{disease}.csv.gz').exists():
        print(f'"{disease}" already processed')
        return filetool.list_output(disease)
    else:
        print(f'"{disease}" processing')

    all_hits = elastic_helper.get_hits(querystring)
    print(f'{len(all_hits)} hits to process')

    entry_list = list()

    for hit in all_hits:
        entry_list.append(
            typesafety.SearchHit(hit['_source']))

    print(f'{len(entry_list)} entries processed')

    output_csv = typesafety.SearchHit.list_to_csv(entry_list)
    output_json = {'request': querystring,
                   'total': len(all_hits),
                   'hits': [e.__dict__ for e in entry_list]}

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
        disease = typesafety.strip_spaces(disease)
        querystring = kql_syntax.match_phrase_any(keyword_list)
        process(disease, querystring)

    print("Finished @:", get_timestamp())
