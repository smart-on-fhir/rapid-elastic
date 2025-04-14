from pathlib import Path
from rapid_elastic import timestamp
from rapid_elastic import naming
from rapid_elastic import filetool
from rapid_elastic import kql_syntax
from rapid_elastic import elastic_helper

###############################################################################
# Pipeline for a single rare-disease disease query
###############################################################################
def pipe_query(disease, query: str | list[str], output_base: str | None = None) -> Path:
    """
    :param disease: example "Sanfilippo syndrome"
    :param query: str prepared KQL query, List[str] synonyms to prepare KQL query for you.
    :param output_base: toplevel output folder
    :return: List of elasticsearch results written to disk, a CSV file and a JSON file
    """
    disease = naming.name_file(disease)
    output_dir = filetool.output_dir(output_base)
    output_csv = output_dir / f'{disease}.csv'
    output_json = output_dir / f'{disease}.json'

    if output_csv.exists() and output_json.exists():
        print(f'"{disease}" already processed')
        return output_csv
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

    result_csv = elastic_helper.ElasticHit.list_to_csv(entry_list)
    # result_json = {'request': query,
    #                'total': len(all_hits),
    #                'hits': [e.as_json() for e in entry_list]}

    return filetool.write_text(result_csv, output_csv)

###############################################################################
# Pipeline using file of saved disease names
###############################################################################

def pipe_file(disease_filename_json: Path | str, output_base: str | None = None) -> list[Path]:
    disease_dict = filetool.read_disease_json(disease_filename_json)

    num_disease = len(disease_dict.keys())

    print(f'{num_disease} diseases, processing now....')
    print(disease_dict)

    file_list = list()

    _pipe_begin = timestamp.datetime.now()
    print("Begin: ", timestamp.datetime_str(_pipe_begin))

    for disease, keyword_list in disease_dict.items():
        file_list.append(pipe_query(disease, keyword_list, output_base=output_base))
        print(f'Progress= {len(file_list)} / {num_disease}')

    _pipe_done = timestamp.datetime.now()
    print("Done: ", timestamp.datetime_str(_pipe_begin), 'seconds')
    print("Took: ", timestamp.diff_seconds(_pipe_begin, _pipe_done), 'seconds')
    return file_list


###############################################################################
#
# MAIN
#
###############################################################################
if __name__ == "__main__":
    pipe_file(filetool.resource('disease_names_expanded.json'))
