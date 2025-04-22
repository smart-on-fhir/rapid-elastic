import csv
from typing import List
from pathlib import Path
from rapid_elastic import filetool

def union_views(create: str, table_list: List[str], create_table=False, alias_col='alias', num_patients=0) -> str:
    if create_table:
        create = f"create TABLE {create} AS \n"
    else:
        create = f"create or replace VIEW {create} AS \n"

    select = list()
    for table in table_list:
        alias = table.replace('cohorts__rare_', '')
        if num_patients > 0:
            select.append(f"(select distinct '{alias}' as {alias_col}, subject_ref from {table} limit {num_patients})")
        else:
            select.append(f"select distinct '{alias}' as {alias_col}, subject_ref from {table}")
    out = create + '\n UNION '.join(select)
    return out

def union_views_file(create: str, table_list: List[str], create_table=False, alias_col='alias', num_patients=0) -> Path:
    return filetool.write_text(
        contents=union_views(create, table_list, create_table, alias_col, num_patients),
        file_path=filetool.resource(f'{create}.sql'))

def reviewer_csv_to_sql_file(aggregate_results_csv='aggregate-results-review-anon.csv') -> Path:
    with open(filetool.resource(aggregate_results_csv), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        entries = list()
        for row in reader:
            _subject_ref = row.get('subject_ref')
            _document_ref = row.get('document_ref')
            _disease_alias = row.get('disease_alias')
            _assertion = row.get('assertion')
            _span = row.get('span')
            _human = row.get('human')
            _agree = row.get('agree')

            if _human:
                entries.append(f"('{_subject_ref}', '{_document_ref}', '{_disease_alias}', '{_assertion}', {_span}, '{_human}', {_agree})")
        ##
        create = f' CREATE or replace view rapid__aggregate_results_review as select * from ( VALUES \n'
        entries = '\n,'.join(entries)
        cols = ') AS t (subject_ref, document_ref, disease_alias, assertion, span, human, agree)'
        sql = create + entries + cols

        return filetool.write_text(sql, filetool.resource(f'{aggregate_results_csv}.sql'))
