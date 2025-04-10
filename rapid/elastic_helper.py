from enum import Enum
from typing import List
from elasticsearch import Elasticsearch
from rapid import filetool
from rapid import config
from rapid import kql_syntax


###############################################################################
# Elasticsearch Field names to uniquely reference
# * Document (required)
# * Patient (required unless your document reference links to the patient)
# * Encounter (optional)
# * group_name (optional)
# * codes (optional, additional document metadata)
#
#  (Optional fields can be disabled by setting the entry to None)
#
# * note is the default field name that elasticsearch is run against.
###############################################################################
_ELASTIC_FIELDS_ = filetool.get_elastic_fields()

class ElasticField(Enum):
    """
    Provides strong type assertions for the supplied ELASTIC_FIELDS.json

    At minimum, these elastic search fields need to be present for this code to work.
    You will either need an ElasticSearch index with these columns or to modify this script.
    """
    note = _ELASTIC_FIELDS_.get('note')
    documentreference_ref = _ELASTIC_FIELDS_.get('documentreference_ref')
    subject_ref = _ELASTIC_FIELDS_.get('subject_ref')
    encounter_ref = _ELASTIC_FIELDS_.get('encounter_ref')
    group_name = _ELASTIC_FIELDS_.get('group_name')
    codes = _ELASTIC_FIELDS_.get('codes')
    document_title = _ELASTIC_FIELDS_.get('document_title')


###############################################################################
# Include/Exclude these columns in Elasticsearch responses
###############################################################################
FIELD_EXCLUDES = [ElasticField.note.value]

FIELD_INCLUDES = [ElasticField.documentreference_ref.value,
                  ElasticField.subject_ref.value,
                  ElasticField.encounter_ref.value,
                  ElasticField.codes.value,
                  ElasticField.group_name.value]

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
    document_title: str = ''

    def __init__(self, source: dict):
        self.anon_ref = source.get(ElasticField.documentreference_ref.value, '')
        self.anon_subject_ref = source.get(ElasticField.subject_ref.value, '')
        self.anon_encounter_ref = source.get(ElasticField.encounter_ref.value, '')
        self.group_name = source.get(ElasticField.group_name.value, '')
        self.document_title = source.get(ElasticField.document_title.value, '')
        self.codes = source.get(ElasticField.codes.value, dict())
        if self.codes:
            self.document_title = self.codes.get('text').replace(',', ';')

    def as_csv(self) -> str:
        out = [self.anon_subject_ref,
               self.anon_encounter_ref,
               self.anon_ref,
               self.group_name,
               self.document_title]
        return ','.join(out)

    def as_json(self):
        return self.__dict__

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
