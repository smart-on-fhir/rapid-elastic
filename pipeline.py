from typing import List
from pathlib import Path
import filetool
import elastic_helper
import kql_syntax

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


def process(disease, querystring) -> List[Path]:

    if filetool.output(f'{disease}.csv').exists() and filetool.output(f'{disease}.json').exists():
        print(f'"{disease}" already processed')
        return filetool.list_output(disease)
    else:
        print(f'"{disease}" processing')

    all_hits = elastic_helper.get_hits(querystring)
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

    filetool.write_text(output_csv, filetool.output(f'{disease}.csv'))
    filetool.write_json(output_json, filetool.output(f'{disease}.json'))


###############################################################################
#
# MAIN query elastic and write results
#
###############################################################################


if __name__ == "__main__":
    disease_json = filetool.read_json(filetool.resource('disease_names.json'))

    for disease, keyword_list in disease_json.items():
        disease = disease.replace(' ', '_')
        querystring = kql_syntax.match_phrase_any(keyword_list)

        process(disease, querystring)
