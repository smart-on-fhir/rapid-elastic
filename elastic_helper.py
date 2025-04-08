import os
import json
from elasticsearch import Elasticsearch
import config
import filetool


# Response includes/excludes
INCLUDE_COLS = ['fhir_ref', 'anon_ref', 'anon_subject_ref', 'anon_encounter_ref', 'codes', 'group_name', '@timestamp']
# EXCLUDE_COLS = []
EXCLUDE_COLS = ['note']

def connect() -> Elasticsearch:
    return Elasticsearch("http://localhost:9200", basic_auth=(config.ELASTIC_USER, config.ELASTIC_PASS))

def query_string(expression) -> dict:
    return {"query": {"query_string": {"query": expression}}}

def sort_by(sortable='@timestamp') -> dict:
    return {"sort": [{sortable: {"order": "desc"}}]}

def return_these() -> dict:
    return {'_source': {'includes': INCLUDE_COLS, 'excludes': EXCLUDE_COLS}}

def get_hits(disease_query_string: str, scroll_size=1000) -> dict:
    print(f'connecting user "{config.ELASTIC_USER}"')
    client = connect()
    query = query_string(disease_query_string)
    query = query | return_these()
    print(query)
    response = client.search(body=query, scroll='5m', size=scroll_size)

    total = response['hits']['total']
    print(f'{total} response hits')

    # Extract the first scroll ID and hits
    scroll_id = response['_scroll_id']
    all_hits = response['hits']['hits']

    # Keep scrolling until no more results
    while True:
        scroll_response = client.scroll(scroll_id=scroll_id, scroll='2m')
        hits = scroll_response['hits']['hits']
        if not hits:
            break
        all_hits.extend(hits)
        scroll_id = scroll_response['_scroll_id']  # Update scroll ID for next round

        print(f"count hits: {len(all_hits)}")

    print(f"Total documents retrieved: {len(all_hits)}")

    return all_hits
