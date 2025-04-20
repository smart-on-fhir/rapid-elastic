create table rapid__site_count as
WITH
disease_list as
(
    select distinct disease_alias, subject_ref from rapid__match_compare
),
icd10_total as
(
    select  count(distinct subject_ref) as cnt, disease_alias
    from    rapid__match_compare
    where   hit_icd10
    group by disease_alias
),
icd10_notes as
(
    select  count(distinct subject_ref) as cnt, disease_alias
    from    rapid__match_compare
    where   hit_icd10 and hit_notes
    group by disease_alias
),
notes_only as
(
    select  count(distinct subject_ref) as cnt, disease_alias
    from    rapid__match_compare
    where   hit_notes and not hit_icd10
    group by disease_alias
)
select      distinct
            icd10_total.cnt as cnt_icd10,
            icd10_notes.cnt as cnt_icd10_notes,
            notes_only.cnt as cnt_notes_only,
            disease_list.disease_alias
from        disease_list
left join   icd10_total on disease_list.disease_alias = icd10_total.disease_alias
left join   icd10_notes on disease_list.disease_alias = icd10_notes.disease_alias
left join   notes_only  on disease_list.disease_alias = notes_only.disease_alias
order by disease_alias
;


