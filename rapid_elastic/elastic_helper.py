import dataclasses
from typing import List
from elasticsearch import Elasticsearch
from rapid_elastic import filetool
from rapid_elastic import config
from rapid_elastic import kql_syntax

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
@dataclasses.dataclass
class ElasticFields:
    """
    Provides strong type assertions for the supplied elastic fields config

    At minimum, these elastic search fields need to be present for this code to work.
    You will either need an ElasticSearch index with these columns or to pass a config with
    the names you use in your index.
    """
    config_path: dataclasses.InitVar[str | None] = None

    note: str = "note"
    note_ref: str = "anon_ref"
    subject_ref: str = "anon_subject_ref"
    encounter_ref: str = "anon_encounter_ref"
    group_name: str = "group_name"
    codes: str = "codes"
    document_title: str = ""

    def __post_init__(self, config_path: str | None):
        if config_path:
            mappings = filetool.read_json(config_path)
            for field in dataclasses.fields(self):
                if field.name in mappings:
                    setattr(self, field.name, mappings[field.name])

    # Exclude these columns from Elasticsearch responses
    @property
    def excludes(self) -> list[str]:
        return [self.note]

    # Include these columns in Elasticsearch responses
    @property
    def includes(self) -> list[str]:
        return [
            self.note_ref,
            self.subject_ref,
            self.encounter_ref,
            self.codes,
            self.group_name,
        ]


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

    def __init__(self, source: dict, *, fields: ElasticFields):
        self.anon_ref = source.get(fields.note_ref, '')
        self.anon_subject_ref = source.get(fields.subject_ref, '')
        self.anon_encounter_ref = source.get(fields.encounter_ref, '')
        self.group_name = source.get(fields.group_name, '')
        self.document_title = source.get(fields.document_title, '')
        self.codes = source.get(fields.codes, {})
        if self.codes and not self.document_title:
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

def get_hits(disease_query_string: str, scroll_size=1000, *, fields: ElasticFields) -> dict:
    print(f'connecting user "{config.ELASTIC_USER}"')
    client = connect()
    query = kql_syntax.query_string(disease_query_string)
    query = query | kql_syntax.response_fields(fields.includes, fields.excludes)
    print(query)
    response = client.search(body=query, scroll='10m', size=scroll_size)

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

    client.clear_scroll(scroll_id=scroll_id)
    print(f"Total documents retrieved: {len(all_hits)}")

    return all_hits


