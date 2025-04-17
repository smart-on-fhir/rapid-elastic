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
