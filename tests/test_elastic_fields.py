import unittest
from rapid_elastic.elastic_helper import ElasticFields

class TestElasticFields(unittest.TestCase):
    def test_required(self):
        fields = ElasticFields()
        self.assertIsNotNone(fields.note)
        self.assertIsNotNone(fields.note_ref)

    def test_desired(self):
        fields = ElasticFields()
        for field in [fields.subject_ref, fields.encounter_ref]:
            if not field:
                print(f'A field is empty, this is OK if you can link documents to patients and/or encounters.')

    def test_optional(self):
        fields = ElasticFields()
        for field in [fields.group_name, fields.codes, fields.document_title]:
            if not field:
                print(f'An OPTIONAL field is not mapped (OK)')
