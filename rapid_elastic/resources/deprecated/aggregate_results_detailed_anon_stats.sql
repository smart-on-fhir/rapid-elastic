-- ############################################################################
-- count patients matching any rare disease (ICD10)

select  	count(distinct subject_ref) as cnt_patients,
        	count(distinct (disease_alias, subject_ref)) as cnt
from    rapid__match_icd10;

--    11978 patients
--    17862 cnt

-- ############################################################################
-- count patients matching any rare disease ( NOTES)

select  	count(distinct subject_ref) as cnt_patients,
        	count(distinct (disease_alias, subject_ref)) as cnt
from    rapid__match_notes

--    90836 patients
--    173645 cnt

-- ############################################################################
--count patients matching any rare disease (NOTES vs ICD10)

select  count(distinct subject_ref) as cnt_patients,
        count(distinct document_ref) as cnt_documents,
        count(distinct (subject_ref, disease_alias)) as cnt,
        hit_icd10,
        hit_notes
from    rapid__match_compare
group by hit_icd10, hit_notes
order by hit_icd10 desc, hit_notes desc;

--    cnt_patients	cnt_documents	cnt	    hit_icd10	hit_notes
--    3840	        441312	        3959	true	    true
--    9364	        0	            13903	true	    false
--    88550	        687412	        169686	false	    true

--    PPV of ICD10 (simple estimator)
--    PPV = True Positive cases  matching ICD10 / (patients matching ICD10)

-- = 3959/(13903 + 3959) = 3959/17862 = 22% aggregated for all diseases.


-- ############################################################################
--    create table aggregate_results_detailed_anon_stats as
--    with GPT4 as
--    (
--        select      count(distinct subject_ref) as cnt,
--                    disease_alias,
--                    asserted
--        from        aggregate_results_detailed_anon
--        group by    disease_alias, asserted
--        order by    disease_alias, asserted
--    ),
--    Affirmed        as (select * from GPT4 where asserted='Affirmed'),
--    Denied          as (select * from GPT4 where asserted='Denied'),
--    NoAssertion     as (select * from GPT4 where asserted='NoAssertion'),
--    Vague           as (select * from GPT4 where asserted in ('VaguePositive', 'VagueNegative')),
--    VaguePositive   as (select * from GPT4 where asserted='VaguePositive'),
--    VagueNegative   as (select * from GPT4 where asserted='VagueNegative'),
--    Tabulated as
--    (
--        select      distinct
--                    Affirmed.disease_alias,
--                    coalesce(Affirmed.cnt, 0)       as cnt_affirmed,
--                    coalesce(Denied.cnt,0)          as cnt_denied,
--                    coalesce(NoAssertion.cnt,0)     as cnt_no_assertion,
--                    coalesce(VaguePositive.cnt,0)   as cnt_vague_positive,
--                    coalesce(VagueNegative.cnt,0)   as cnt_vague_negative
--        from        Affirmed
--        left join   Denied          on Affirmed.disease_alias = Denied.disease_alias
--        left join   NoAssertion     on Affirmed.disease_alias = NoAssertion.disease_alias
--        left join   VaguePositive   on Affirmed.disease_alias = VaguePositive.disease_alias
--        left join   VagueNegative   on Affirmed.disease_alias = VagueNegative.disease_alias
--    ),
--    sample_size as
--    (
--        SELECT  cnt_affirmed       +
--                cnt_denied         +
--                cnt_no_assertion   +
--                cnt_vague_positive +
--                cnt_vague_negative as cnt_total,
--                Tabulated.*
--         from Tabulated
--    )
--    select  (cnt_affirmed > 1 and cnt_total >= 10) as threshold,
--            ROUND(CAST
--                    (sample_size.cnt_affirmed AS DOUBLE) /
--                    (sample_size.cnt_total), 3) AS PPV,
--            sample_size.*
--    from sample_size
--    ;

-- ############################################################################
create table rapid__aggregate_results_detailed_anon_stats as
WITH
match_icd10 as ( select  distinct disease_alias, subject_ref from rapid__match_icd10),
match_notes as ( select  distinct disease_alias, subject_ref from rapid__match_notes),
match_gpt4  as
(
    select      AGG.disease_alias,
                AGG.asserted,
                concat('Patient/', AGG.subject_ref) as subject_ref,
                match_icd10.subject_ref is not null as hit_icd10,
                match_notes.subject_ref is not null as hit_notes
    from        aggregate_results_detailed_anon as AGG
    left join   match_icd10
                on AGG.disease_alias=match_icd10.disease_alias
                and concat('Patient/', AGG.subject_ref)=match_icd10.subject_ref
    left join   match_notes
                on AGG.disease_alias=match_notes.disease_alias
                and concat('Patient/', AGG.subject_ref)=match_notes.subject_ref
),
GPT4 as
(
    select      count(distinct match_gpt4.subject_ref) as cnt,
                match_gpt4.disease_alias,
                match_gpt4.asserted,
                match_gpt4.hit_icd10,
                match_gpt4.hit_notes
    from        match_gpt4
    group by    match_gpt4.disease_alias, match_gpt4.asserted, match_gpt4.hit_icd10, match_gpt4.hit_notes
    order by    match_gpt4.disease_alias, match_gpt4.asserted, match_gpt4.hit_icd10, match_gpt4.hit_notes
),
Affirmed        as (select * from GPT4 where asserted='Affirmed'),
Denied          as (select * from GPT4 where asserted='Denied'),
NoAssertion     as (select * from GPT4 where asserted='NoAssertion'),
VaguePositive   as (select * from GPT4 where asserted='VaguePositive'),
VagueNegative   as (select * from GPT4 where asserted='VagueNegative'),
Tabulated as
(
    select      distinct
                Affirmed.disease_alias,
                Affirmed.hit_icd10,
                Affirmed.hit_notes,
                coalesce(Affirmed.cnt, 0)       as cnt_affirmed,
                coalesce(Denied.cnt,0)          as cnt_denied,
                coalesce(NoAssertion.cnt,0)     as cnt_no_assertion,
                coalesce(VaguePositive.cnt,0)   as cnt_vague_positive,
                coalesce(VagueNegative.cnt,0)   as cnt_vague_negative
    from        Affirmed
    left join   Denied          ON  Affirmed.disease_alias  = Denied.disease_alias
                                and Affirmed.hit_icd10      = Denied.hit_icd10
                                and Affirmed.hit_notes      = Denied.hit_notes
    left join   NoAssertion     ON  Affirmed.disease_alias  = NoAssertion.disease_alias
                                and Affirmed.hit_icd10      = NoAssertion.hit_icd10
                                and Affirmed.hit_notes      = NoAssertion.hit_notes
    left join   VaguePositive   ON  Affirmed.disease_alias  = VaguePositive.disease_alias
                                and Affirmed.hit_icd10      = VaguePositive.hit_icd10
                                and Affirmed.hit_notes      = VaguePositive.hit_notes
    left join   VagueNegative   ON  Affirmed.disease_alias  = VagueNegative.disease_alias
                                and Affirmed.hit_icd10      = VagueNegative.hit_icd10
                                and Affirmed.hit_notes      = VagueNegative.hit_notes
),
sample_size as
(
    SELECT  cnt_affirmed       +
            cnt_denied         +
            cnt_no_assertion   +
            cnt_vague_positive +
            cnt_vague_negative as cnt_total,
            Tabulated.*
     from Tabulated
),
statifier as
(
    select      (cnt_affirmed > 1 and cnt_total >= 5) as threshold,
                hit_icd10 and hit_notes         as hit_icd10_notes,
                hit_notes and not hit_icd10     as hit_notes_only,
                sample_size.*
    from        sample_size
    order by    disease_alias, hit_icd10 desc, hit_notes desc
),
PPV_calc as
(
    select      ROUND(CAST
                    (statifier.cnt_affirmed AS DOUBLE) /
                    (statifier.cnt_total), 3) AS PPV,
                statifier.*
    from        statifier
    order by    disease_alias, hit_icd10 desc, hit_notes desc
)
select * from PPV_calc;

