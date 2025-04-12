-- NOTES
select  disease_alias,
        count(distinct subject_ref)   as cnt_subjects,
        count(distinct encounter_ref) as cnt_encounters
from    cohorts__rare_match_notes
group by disease_alias
order by cnt_subjects desc;

-- ICD10
select  disease_alias,
        count(distinct subject_ref)   as cnt_subjects,
        count(distinct encounter_ref) as cnt_encounters
from    cohorts__rare_match_icd10
group by disease_alias
order by cnt_subjects desc;

-- ICD10 + NOTES
select  match_icd10.disease_alias,
        count(distinct match_icd10.subject_ref)  as cnt_subjects
from    cohorts__rare_match_icd10 as match_icd10,
        cohorts__rare_match_notes as match_notes
where   match_icd10.subject_ref = match_notes.subject_ref
group by match_icd10.disease_alias
order by cnt_subjects desc;


with match_notes as
(
    select  disease_alias,
            count(distinct subject_ref)   as cnt_subjects,
            count(distinct encounter_ref) as cnt_encounters
    from    cohorts__rare_match_notes
    group by disease_alias
),
match_icd10 as
(
    select  disease_alias,
            count(distinct subject_ref)   as cnt_subjects,
            count(distinct encounter_ref) as cnt_encounters
    from    cohorts__rare_match_icd10
    group by disease_alias
)
select
    match_notes.cnt_subjects as notes_subjects,
    match_notes.cnt_encounters as notes_encounters,




