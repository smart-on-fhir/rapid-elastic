import unittest
from rapid import filetool
from rapid import elastic_helper
from rapid.elastic_helper import ElasticField

class TestElasticFields(unittest.TestCase):
    def test_json_exists(self):
        filetool.resource('ELASTIC_FIELDS.json')

    def test_required(self):
        self.assertIsNotNone(elastic_helper.ElasticField.note)
        self.assertIsNotNone(elastic_helper.ElasticField.documentreference_ref)

    def test_desired(self):
        for field in [ElasticField.subject_ref, ElasticField.encounter_ref]:
            if not field.value:
                print(f'{field.name} field is empty, this is OK if you can link documents to patients and/or encounters.')

    def test_optional(self):
        for field in [ElasticField.group_name, ElasticField.codes, ElasticField.document_title]:
            if not field.value:
                print(f'{ElasticField.encounter_ref.name} OPTIONAL field is not mapped (OK)')
