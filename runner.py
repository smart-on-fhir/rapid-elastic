import os
import json
from elasticsearch import Elasticsearch

# HTTP Basic Auth
ELASTIC_USER = os.environ.get("ELASTIC_USER")
ELASTIC_PASS = os.environ.get("ELASTIC_PASS")

# Response includes/excludes
INCLUDE_COLS = ['fhir_ref', 'anon_ref', 'anon_subject_ref', 'anon_encounter_ref', 'codes', '@timestamp']
EXCLUDE_COLS = []
#EXCLUDE_COLS = ['note']

# Class to wrap the response cols
class Entry:
    _timestamp: str = None
    fhir_ref: str = None
    anon_ref: str = None
    anon_subject_ref: str = None
    anon_encounter_ref: str = None
    doc_code_text: str = None
    doc_codes: dict = None

def connect() -> Elasticsearch:
    return Elasticsearch("http://localhost:9200", basic_auth=(ELASTIC_USER, ELASTIC_PASS))

def query_string(expression) -> dict:
    return {"query": {"query_string": {"query": expression}}}

def sort_by(sortable='@timestamp') -> dict:
    return {"sort": [{sortable: {"order": "desc"}}]}

def return_these() -> dict:
    return {'_source': {'includes': INCLUDE_COLS, 'excludes': EXCLUDE_COLS}}


CF = """
note: "cystic fibrosis" and not (note: "non-cystic fibrosis")
""".strip()

PKU = """
note : ("phenylketonuria" or "phenylalanine hydroxylase deficiency" or "hyperphenylalaninemia")
""".strip()


if __name__ == '__main__':
    print(f'connecting user "{ELASTIC_USER}"')
    client = connect()
    query = query_string(PKU)
    query = query | return_these()

    print(query)

    result = client.search(body=query, size=10*1000)
    entry_list = list()

    for hit in result['hits']['hits']:
        _source = hit['_source']

        e = Entry()
        e.fhir_ref = _source['fhir_ref']
        e.anon_ref = _source['anon_ref']
        e.anon_subject_ref = _source.get('anon_subject_ref')
        e.anon_encounter_ref = _source.get('anon_encounter_ref')
        e._timestamp = _source.get('@timestamp')
        e.doc_codes = _source.get('codes')
        if e.doc_codes:
            e.doc_code_text = _source.get('codes').get('text')

        entry_list.append(e.__dict__)

    output = {'request': query,
              'total': result['hits']['total'],
              'hits': entry_list}

    print(f'{len(entry_list)} hits matched')

    with open('result.json', 'w') as fp:
        json.dump(result['hits'], fp, indent=4)

    with open('result_entry_list.json', 'w') as fp:
        json.dump(output, fp, indent=4)
