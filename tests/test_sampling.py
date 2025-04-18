import unittest

from rapid_elastic import filetool
from rapid_elastic import sampling
from rapid_elastic import elastic_helper

class TestSampling(unittest.TestCase):

    @unittest.skip('rapid__match_notes_sample_patients.sql')
    def test_union_views_match_notes_sample(self):
        print(sampling.sample_match_notes(num_patients=0))

    @unittest.skip('rapid__match_icd10_sample_patients.sql')
    def test_rapid__match_icd10_sample_patients(self):
        print(sampling.sample_match_icd10(num_patients=0))

    @unittest.skip
    def test_sample_csv_to_json_file(self):
        print(sampling.sample_csv_to_json_file())

    @unittest.skip
    def test_list_notes(self):
        lookup = filetool.read_json(
            filetool.resource('rapid__match_both_sample_notes.json'))

        client = elastic_helper.connect()

        for disease_alias in lookup.keys():
            subject_list = lookup[disease_alias]['subject_ref']
            note_list = lookup[disease_alias]['document_ref']
            print(f'{disease_alias}:\t{len(subject_list)} subjects; {len(note_list)} notes')

            counter = 1
            counter_step = 100
            for document_ref in note_list:
                file_txt = filetool.output_note(f'{document_ref}.txt')
                file_gz = filetool.output_note(f'{document_ref}.txt.gz')

                if counter % counter_step == 0:
                    print(f'{disease_alias}: {counter} of {len(note_list)}')

                counter += 1
                if not file_txt.exists() or file_gz.exists():
                    text = elastic_helper.get_note(document_ref, client)
                    filetool.write_text(text, filetool.output_note(f'{document_ref}.txt'))
                else:
                    print(f'OK cached request for {document_ref}')
