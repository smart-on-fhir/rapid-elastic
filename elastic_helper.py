from enum import Enum
from typing import List
from elasticsearch import Elasticsearch
import config
import kql_syntax

class ElasticField(Enum):
    """
    At minimum, these elastic search fields need to be present for this code to work.
    You will either need an ElasticSearch index with these columns or to modify this script.
     Note that doc_codes are optional metadata to determine "doc_code_text" which is the document title.
     Example:
        "codes": {
            "text": "Neurosurgery Visit",
            "coding": [
                {"display": "Neurosurgery Visit",
                "code": "3817546",
                "system": "https://fhir.cerner.com/96976f07-eccb-424c-9825-e0d0b887148b/codeSet/72"
                }]},
    """
    note = 'raw clinical note text from FHIR DocumentReference'
    fhir_ref = 'FHIR DocumentReference.id (original).'
    anon_ref = 'FHIR DocumentReference.id (anon)'
    anon_subject_ref = 'FHIR Patient.id (anon)'
    anon_encounter_ref = 'FHIR Encounter.id (anon)'
    group_name = 'optional, BCH uses this to batch up ETL jobs.'
    codes = dict()


###############################################################################
# Include/Exclude these columns in Elasticsearch responses
###############################################################################
FIELD_EXCLUDES = [ElasticField.note]

FIELD_INCLUDES = [ElasticField.fhir_ref,
                  ElasticField.anon_ref,
                  ElasticField.anon_subject_ref,
                  ElasticField.anon_encounter_ref,
                  ElasticField.codes,
                  ElasticField.group_name]

###############################################################################
# Elasticsearch "hits"
###############################################################################
class ElasticHit:
    """
    Class to wrap Elasticsearch responses for only columns we need.
    """
    HEADERS_OUT = ['subject_ref',       # Patient id
                   'encounter_ref',     # Encounter id
                   'document_ref',      # Document id
                   'group_name',        # Group name (optional)
                   'document_title']    # Document Title (optional)
    group_name: str = ''
    anon_ref: str = ''
    anon_subject_ref: str = ''
    anon_encounter_ref: str = ''
    codes: dict = {}
    doc_title: str = ''

    def __init__(self, source: dict):
        self.anon_ref = source.get(ElasticField.anon_ref.name, '')
        self.anon_subject_ref = source.get(ElasticField.anon_subject_ref.name, '')
        self.anon_encounter_ref = source.get(ElasticField.anon_encounter_ref.name, '')
        self.group_name = source.get(ElasticField.group_name.name, '')
        self.codes = source.get(ElasticField.codes.name, dict())
        if self.codes:
            self.doc_title = self.codes.get('text').replace(',', ';')

    def as_csv(self) -> str:
        out = [self.anon_subject_ref,
               self.anon_encounter_ref,
               self.anon_ref,
               self.group_name,
               self.doc_title]
        return ','.join(out)

    def as_json(self):
        out = self.__dict__
        del out['HEADERS_OUT']
        return out

    @classmethod
    def list_to_csv(cls, entry_list: List) -> str:
        output_csv = ','.join(ElasticHit.HEADERS_OUT) + '\n'
        output_csv += '\n'.join([e.as_csv() for e in entry_list])
        return output_csv

###############################################################################
#
# Helper Methods
#
###############################################################################
def connect() -> Elasticsearch:
    return Elasticsearch(hosts=config.ELASTIC_HOST,
                         basic_auth=(config.ELASTIC_USER, config.ELASTIC_PASS))

def get_hits(disease_query_string: str, scroll_size=1000) -> dict:
    print(f'connecting user "{config.ELASTIC_USER}"')
    client = connect()
    query = kql_syntax.query_string(disease_query_string)
    query = query | kql_syntax.response_fields(FIELD_INCLUDES, FIELD_EXCLUDES)
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
