create table rapid__match_compare AS WITH
patient_list as
(
    select distinct disease_alias, subject_ref from rapid__match_icd10
    UNION
    select distinct disease_alias, subject_ref from rapid__match_notes
),
match_icd10 as
(
    select  distinct
            disease_alias,
            subject_ref,
            icd10_code
    from    rapid__match_icd10
),
match_notes as
(
    select  distinct
            disease_alias,
            subject_ref,
            document_ref
    from    rapid__match_notes
),
sample_patients as
(
    select  distinct
            disease_alias,
            subject_ref
    from    rapid__match_notes_sample_patients
),
sample_notes as
(
    select  distinct
            disease_alias,
            subject_ref,
            document_ref
    from    rapid__match_notes_sample_notes
),
tabulate as
(
    select  distinct
            patient_list.disease_alias,
            patient_list.subject_ref,
            match_icd10.subject_ref is not null as hit_icd10,
            match_icd10.icd10_code,
            match_notes.subject_ref is not null as hit_notes,
            match_notes.document_ref,
            sample_patients.subject_ref is not null as hit_sample_patients,
            sample_notes.subject_ref is not null as hit_sample_notes
    from    patient_list
    left join   match_icd10
                on  patient_list.subject_ref=match_icd10.subject_ref
                and patient_list.disease_alias=match_icd10.disease_alias
    left join   match_notes
                on  patient_list.subject_ref=match_notes.subject_ref
                and patient_list.disease_alias=match_notes.disease_alias
    left join   sample_patients
                on  patient_list.subject_ref=sample_patients.subject_ref
                and patient_list.disease_alias=sample_patients.disease_alias
    left join   sample_notes
                on  patient_list.subject_ref=sample_notes.subject_ref
                and patient_list.disease_alias=sample_notes.disease_alias
)
select * from tabulate;

--    #################################################
--    Examples to compare matches
--    #################################################

--    select count(distinct subject_ref) as cnt_patients,
--            hit_notes,
--            hit_icd10
--    from    rapid__match_compare
--    group by
--            hit_notes,
--            hit_icd10
--    order by hit_notes, hit_icd10;
--
--    select count(distinct subject_ref) as cnt_patients,
--            hit_notes,
--            hit_icd10,
--            hit_sample_patients
--    from    rapid__match_compare
--    group by
--            hit_notes,
--            hit_icd10,
--            hit_sample_patients,
--            hit_sample_notes
--    order by hit_notes, hit_icd10;
--
--    select      count(distinct subject_ref) as cnt_patients,
--                disease_alias,
--                hit_notes,
--                hit_icd10
--    from        rapid__match_compare
--    group by    disease_alias,
--                hit_notes,
--                hit_icd10
--    order by    disease_alias,
--                hit_notes, hit_icd10;
--
--
--    select      count(distinct subject_ref) as cnt_patients,
--                disease_alias,
--                hit_notes,
--                hit_icd10,
--                hit_sample_patients
--    from        rapid__match_compare
--    group by    disease_alias,
--                hit_notes,
--                hit_icd10,
--                hit_sample_patients,
--                hit_sample_notes
--    order by    disease_alias,
--                hit_notes, hit_icd10;
