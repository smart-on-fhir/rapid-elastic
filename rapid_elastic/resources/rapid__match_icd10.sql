create table rapid__match_icd10 as
select  distinct
        curated.icd10_code,
        curated.orpha_code,
        curated.disease_name,
        curated.disease_alias,
        DX.*
from    core__condition as DX,
        rapid__codeset as curated
where   DX.system = 'http://hl7.org/fhir/sid/icd-10-cm'
and     curated.icd10_code like concat(DX.code, '%');

--    #################################################
--    Examples to count ICD10 matches
--    #################################################
--    select  icd10_code,
--            count(distinct subject_ref)   as cnt_subjects,
--            count(distinct encounter_ref) as cnt_encounters
--    from    rapid__match_icd10
--    group by icd10_code
--    order by cnt_subjects desc;
--
--    select  disease_alias,
--            count(distinct subject_ref)   as cnt_subjects,
--            count(distinct encounter_ref) as cnt_encounters
--    from    rapid__match_icd10
--    group by disease_alias
--    order by cnt_subjects desc;
--
--    select  icd10_code,
--            disease_alias,
--            count(distinct subject_ref)   as cnt_subjects,
--            count(distinct encounter_ref) as cnt_encounters
--    from    rapid__match_icd10
--    group by icd10_code, disease_alias
--    order by cnt_subjects desc;
