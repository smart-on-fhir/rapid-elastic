import os
from typing import List
from pathlib import Path
import json
import client_helper

# Class to wrap the response cols
class Entry:
    _timestamp: str = ''
    fhir_ref: str = ''
    anon_ref: str = ''
    anon_subject_ref: str = ''
    anon_encounter_ref: str = ''
    doc_code_text: str = ''
    doc_codes: dict = {}

    def to_csv(self):
        out = [self.anon_subject_ref,
               self.anon_encounter_ref,
               self.anon_ref,
               self.fhir_ref,
               self.doc_code_text]
        return ','.join(out)

def path_csv(disease) -> Path:
    return path_file(f'{disease}.csv')

def path_json(disease) -> Path:
    return path_file(f'{disease}.json')

def path_file(filename) -> Path:
    return Path(os.path.join(os.path.dirname(__file__), 'output', filename))

def list_files(disease) -> List[Path]:
    return [path_csv(disease), path_json(disease)]

def process(disease, querystring) -> List[Path]:
    if path_csv(disease).exists() and path_json(disease).exists():
        print(f'"{disease}" already processed')
        return list_files(disease)
    else:
        print(f'"{disease}" processing')

    all_hits = client_helper.get_hits(querystring)
    print(f'{len(all_hits)} hits to process')

    entry_list = list()

    for hit in all_hits:
        _source = hit['_source']

        e = Entry()
        e.fhir_ref = _source.get('fhir_ref', '')
        e.anon_ref = _source.get('anon_ref', '')
        e.anon_subject_ref = _source.get('anon_subject_ref', '')
        e.anon_encounter_ref = _source.get('anon_encounter_ref', '')
        e._timestamp = _source.get('@timestamp', '')
        e.doc_codes = _source.get('codes', dict())
        if e.doc_codes:
            e.doc_code_text = _source.get('codes').get('text').replace(',', '|')

        entry_list.append(e)

    print(f'{len(entry_list)} entries processed')

    output_csv = '\n'.join([e.to_csv() for e in entry_list])
    output_json = {'request': querystring,
                   'total': len(all_hits),
                   'hits': [e.__dict__ for e in entry_list]}

    with open(path_csv(disease), 'w') as fp:
        print('writing...')
        print(str(fp.name))
        fp.writelines(output_csv)

    with open(path_json(disease), 'w') as fp:
        print('writing...')
        print(str(fp.name))
        json.dump(output_json, fp, indent=4)

    return list_files(disease)
