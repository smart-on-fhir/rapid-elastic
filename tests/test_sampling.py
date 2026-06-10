import unittest
from rapid_elastic import sampling

class TestSampling(unittest.TestCase):

    @unittest.skip('rapid__match_notes_sample_patients.sql')
    def test_union_views_match_notes_sample(self):
        print(sampling.sample_match_notes(num_patients=0))

    @unittest.skip('rapid__match_icd10_sample_patients.sql')
    def test_rapid__match_icd10_sample_patients(self):
        print(sampling.sample_match_icd10(num_patients=0))