from pathlib import Path
from datetime import datetime
from rapid_elastic import filetool
from rapid_elastic import kql_syntax
from rapid_elastic import elastic_helper

###############################################################################
# Single query mode
###############################################################################
def pipe_query(
    topic,
    query: str | list[str],
    output_base: str | None = None,
    fields_config: str | None = None,
) -> Path:
    """
    :param topic: example "sanfilippo_syndrome"
    :param query: str prepared KQL query, List[str] synonyms to prepare KQL query for you.
    :param output_base: toplevel output folder
    :param fields_config: file with elasticsearch field overrides
    :return: List of elasticsearch results written to disk, a CSV file and a JSON file
    """
    output_dir = filetool.path_output(output_base)
    output_csv = output_dir / f'{topic}.csv'
    output_csv_gz = output_dir / f'{topic}.csv.gz'

    if output_csv.exists() or output_csv_gz.exists():
        print(f'"{topic}" already processed')
        return output_csv
    else:
        print(f'"{topic}" processing')

    if isinstance(query, list):
        query = kql_syntax.match_phrase_any(query)

    fields = elastic_helper.ElasticFields(config_path=fields_config)

    _time1 = filetool.datetime.now()
    #
    all_hits = elastic_helper.get_hits(query, fields=fields)
    #
    _time2 = datetime.now()

    print("Elastic took: ", diff_seconds(_time1, _time2), ' seconds')
    print(f'{len(all_hits)} hits to process')

    entry_list = [elastic_helper.ElasticHit(hit['_source'], fields=fields) for hit in all_hits]

    print(f'{len(entry_list)} entries processed')

    result_csv = elastic_helper.ElasticHit.list_to_csv(entry_list)
    # result_json = {'request': query,
    #                'total': len(all_hits),
    #                'hits': [e.as_json() for e in entry_list]}

    return filetool.write_text(result_csv, output_csv)

###############################################################################
# Batch mode
###############################################################################
def pipe_batch(
    query_topics_json: Path | dict,
    output_base: str | None = None,
    fields_config: str | None = None,
) -> list[Path]:

    if not isinstance(query_topics_json, dict):
        query_topics_json = filetool.read_query_topics(query_topics_json)

    num_topics = len(query_topics_json.keys())
    print(f'{num_topics} topics, processing now....')

    file_list = list()
    start_time = datetime.now()

    for topic, query in query_topics_json.items():
        file_list.append(pipe_query(topic, query, output_base=output_base, fields_config=fields_config))
        print(f'Progress= {len(file_list)} / {num_topics}')

    stop_time = datetime.now()
    print("Took: ", diff_seconds(start_time, stop_time), 'seconds')
    return file_list

def diff_seconds(start_time: datetime, stop_time: datetime):
    """
    Simple wall-clock Timer
    """
    delta = stop_time - start_time
    return abs(delta.total_seconds())


###############################################################################
#
# MAIN
#
# see `cli.py` for more sophisticated arg parsing
#
###############################################################################
if __name__ == "__main__":
    pipe_batch(filetool.path_query_topics())
