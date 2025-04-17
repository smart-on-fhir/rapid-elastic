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

def sample_match_icd10(num_patients=None):
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
