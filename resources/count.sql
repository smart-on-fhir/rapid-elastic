create table cohorts__rare__DX as
select  distinct
        curated.icd10_code,
        curated.orpha_code,
        curated.disease_name,
        DX.*
from    core__condition as DX,
        cohorts__rare__CODES as curated
where   DX.system = 'http://hl7.org/fhir/sid/icd-10-cm'
and     curated.icd10_code like concat(DX.code, '%');

select  icd10_code,
        count(distinct subject_ref)   as cnt_subjects,
        count(distinct encounter_ref) as cnt_encounters
from    cohorts__rare__DX
group by icd10_code
order by cnt_subjects desc;

select  lower(disease_name) as disease_name,
        count(distinct subject_ref)   as cnt_subjects,
        count(distinct encounter_ref) as cnt_encounters
from    cohorts__rare__DX
group by lower(disease_name)
order by cnt_subjects desc;

select  icd10_code,
        lower(disease_name) as disease_name,
        count(distinct subject_ref)   as cnt_subjects,
        count(distinct encounter_ref) as cnt_encounters
from    cohorts__rare__DX
group by icd10_code, lower(disease_name)
order by cnt_subjects desc;

--    select  orpha_code,
--            lower(disease_name) as disease_name,
--            count(distinct subject_ref)   as cnt_subjects,
--            count(distinct encounter_ref) as cnt_encounters
--    from    cohorts__rare__DX
--    group by orpha_code, lower(disease_name)
--    order by cnt_subjects desc;


