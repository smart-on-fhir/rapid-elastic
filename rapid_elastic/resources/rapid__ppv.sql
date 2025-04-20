create table rapid__ppv as
WITH
disease_list as (select distinct disease_alias from rapid__match_compare),
match_icd10 as (select  distinct disease_alias, subject_ref from rapid__match_icd10),
match_notes as (select  distinct disease_alias, subject_ref from rapid__match_notes),
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
                disease_list.disease_alias,
                Affirmed.hit_icd10,
                Affirmed.hit_notes,
                coalesce(Affirmed.cnt, 0)       as cnt_affirmed,
                coalesce(Denied.cnt,0)          as cnt_denied,
                coalesce(NoAssertion.cnt,0)     as cnt_no_assertion,
                coalesce(VaguePositive.cnt,0)   as cnt_vague_positive,
                coalesce(VagueNegative.cnt,0)   as cnt_vague_negative
    from        disease_list
    left join   Affirmed        ON  disease_list.disease_alias  = Affirmed.disease_alias
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
    select      (cnt_affirmed >= 1)              as threshold,
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

