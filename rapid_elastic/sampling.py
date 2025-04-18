import csv
from pathlib import Path
from rapid_elastic import filetool
from rapid_elastic import disease_names
from rapid_elastic import sql_compare

def list_where(sample_table: str, disease_alias: list | str, num_patients=None) -> list | str:
    """
    :param sample_table: table to sample from
    :param disease_alias: where clause
    :param num_patients: 0 default no limit
    :return:
    """
    if isinstance(disease_alias, list):
        return [list_where(sample_table, table) for table in list(set(disease_alias))]
    else:
        _select = f"SELECT distinct disease_alias, subject_ref FROM {sample_table} WHERE disease_alias='{disease_alias}'"
        if num_patients:
            return _select + f' LIMIT {num_patients}'
        return _select

def sample_match_icd10(num_patients=None) -> Path:
    """
    Match Patients to ICD10 codesets
    :param num_patients: 0 default no limit
    :return: Path to SQL file
    """
    _create_table = 'rapid__match_icd10_sample_patients'
    _sample_list = list_where(sample_table='rapid__match_icd10',
                              disease_alias=disease_names.list_disease_alias(),
                              num_patients=num_patients)
    _union = " \tUNION \n".join(f'({sample})' for sample in _sample_list)
    _sql = f"CREATE TABLE {_create_table} as {_union}"

    return filetool.write_text(_sql, filetool.resource(f'{_create_table}.sql'))

def sample_match_notes(num_patients=None) -> Path:
    """
    Match Patients to Elasticsearch clinical note results
    :param num_patients:
    :return: Path to SQL file
    """
    return sql_compare.union_views_file(
        create='rapid__match_notes_sample_patients',
        table_list=disease_names.list_cohorts(),
        create_table=True, alias_col='disease_alias', num_patients=num_patients)

def sample_csv_to_json(sample_csv='rapid__match_both_sample_notes.csv', num_patients=100) -> dict:
    """
    Get lookups of notes to fetch

    select distinct disease_alias, subject_ref, document_ref
    from rapid__match_both_sample_notes
    order by disease_alias, subject_ref, document_ref

    :param sample_csv: saved SQL query result
    :param num_patients: max number of patients per disease_alias
    :return: dict where keys=disease_alias, document_ref, subject_ref
    """
    with open(filetool.resource(sample_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        out = dict()
        for row in reader:
            _disease_alias = row['disease_alias']
            _subject_ref = row['subject_ref']
            _document_ref = row['document_ref']

            if _disease_alias not in out.keys():
                print(f'INIT {num_patients} for {_disease_alias}')
                out[_disease_alias] = {'subject_ref': list(),
                                       'document_ref': list()}

            if num_patients >= len(out[_disease_alias]['subject_ref']):
                if _subject_ref not in out[_disease_alias]['subject_ref']:
                    out[_disease_alias]['subject_ref'].append(_subject_ref)

                if _subject_ref not in out[_disease_alias]['document_ref']:
                    out[_disease_alias]['document_ref'].append(_document_ref)
    return out

def sample_csv_to_json_file(sample_csv='rapid__match_both_sample_notes.csv', num_patients=100) -> Path:
    as_json = sample_csv_to_json(sample_csv, num_patients)
    file_json = sample_csv.replace('.csv', '.json')
    return filetool.write_json(as_json, filetool.resource(file_json))
