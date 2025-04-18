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
with GPT4 as
(
    select      count(distinct subject_ref) as cnt,
                disease_alias,
                asserted
    from        aggregate_results_detailed_anon
    group by    disease_alias, asserted
    order by    disease_alias, asserted
),
Affirmed        as (select * from GPT4 where asserted='Affirmed'),
Denied          as (select * from GPT4 where asserted='Denied'),
NoAssertion     as (select * from GPT4 where asserted='NoAssertion'),
Vague           as (select * from GPT4 where asserted in ('VaguePositive', 'VagueNegative')),
VaguePositive   as (select * from GPT4 where asserted='VaguePositive'),
VagueNegative   as (select * from GPT4 where asserted='VagueNegative'),
Tabulated as
(
    select      distinct
                Affirmed.disease_alias,
                coalesce(Affirmed.cnt, 0)       as cnt_affirmed,
                coalesce(Denied.cnt,0)          as cnt_denied,
                coalesce(NoAssertion.cnt,0)     as cnt_no_assertion,
                coalesce(VaguePositive.cnt,0)   as cnt_vague_positive,
                coalesce(VagueNegative.cnt,0)   as cnt_vague_negative
    from        Affirmed
    left join   Denied          on Affirmed.disease_alias = Denied.disease_alias
    left join   NoAssertion     on Affirmed.disease_alias = NoAssertion.disease_alias
    left join   VaguePositive   on Affirmed.disease_alias = VaguePositive.disease_alias
    left join   VagueNegative   on Affirmed.disease_alias = VagueNegative.disease_alias
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
)
select  (cnt_affirmed > 1 and cnt_total >= 10) as threshold,
        ROUND(CAST
                (sample_size.cnt_affirmed AS DOUBLE) /
                (sample_size.cnt_total), 3) AS PPV,
        sample_size.*
from sample_size
;


