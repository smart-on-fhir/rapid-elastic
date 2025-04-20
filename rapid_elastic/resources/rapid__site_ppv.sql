--    rapid__site_count
--    * cnt_icd10
--    * cnt_icd10_notes
--    * cnt_notes_only
--    * disease_alias
--
--    rapid__ppv
--    * ppv
--    * threshold
--    * disease_alias
--    * hit_icd10_notes
--    * hit_notes_only


create table rapid__site_ppv as
WITH
ppv_hit_icd10_notes as
(
    select ppv, cnt_affirmed, disease_alias from rapid__ppv where hit_icd10_notes
),
ppv_hit_notes_only as
(
    select ppv, cnt_affirmed, disease_alias from rapid__ppv where hit_notes_only
),
tabulated as
(
    select  rapid__site_count.cnt_icd10,
            rapid__site_count.cnt_icd10_notes,
            rapid__site_count.cnt_notes_only,
            coalesce(ppv_hit_icd10_notes.ppv, 0) as  const_icd10_notes_ppv,
            coalesce(ppv_hit_notes_only.ppv, 0)  as  const_hit_notes_only_ppv,
            ppv_hit_icd10_notes.cnt_affirmed as cnt_affirmed_icd10_notes,
            ppv_hit_notes_only.cnt_affirmed as cnt_affimed_notes_only,
            rapid__site_count.disease_alias
    from    rapid__site_count
    left    join ppv_hit_icd10_notes on rapid__site_count.disease_alias = ppv_hit_icd10_notes.disease_alias
    left    join ppv_hit_notes_only  on rapid__site_count.disease_alias = ppv_hit_notes_only.disease_alias
),
calculated as
(
    select  round((tabulated.cnt_icd10_notes * const_icd10_notes_ppv),2)      as  cnt_icd10_notes_ppv,
            round((tabulated.cnt_notes_only  * const_hit_notes_only_ppv), 2)  as  cnt_notes_only_ppv,
            cnt_icd10,
            cnt_icd10_notes,
            cnt_notes_only,
            const_icd10_notes_ppv,
            const_hit_notes_only_ppv,
            disease_alias
    from calculated
)
select * from calculated
order by calculated.disease_alias
;



