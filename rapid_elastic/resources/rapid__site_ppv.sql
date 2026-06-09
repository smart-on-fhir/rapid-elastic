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
    select  rapid__site_count.disease_alias,
            coalesce(rapid__site_count.cnt_icd10, 0)        as cnt_icd10,
            coalesce(rapid__site_count.cnt_icd10_notes, 0)  as cnt_icd10_notes,
            coalesce(rapid__site_count.cnt_notes_only, 0)   as cnt_notes_only,
            coalesce(ppv_hit_notes_only.ppv, 0)             as  const_hit_notes_only_ppv,
            coalesce(ppv_hit_icd10_notes.ppv, 0)            as  const_icd10_notes_ppv
    from    rapid__site_count
    left    join ppv_hit_icd10_notes on rapid__site_count.disease_alias = ppv_hit_icd10_notes.disease_alias
    left    join ppv_hit_notes_only  on rapid__site_count.disease_alias = ppv_hit_notes_only.disease_alias
),
graceful as
(
    select  distinct
            disease_alias,
            cnt_icd10,
            cnt_icd10_notes,
            cnt_notes_only,
            const_hit_notes_only_ppv,
            case    when const_icd10_notes_ppv > 0
                    then const_icd10_notes_ppv
                    else const_hit_notes_only_ppv end as const_icd10_notes_ppv
    from tabulated
),
calculated as
(
    select  round((graceful.cnt_icd10_notes * const_icd10_notes_ppv),2)      as  cnt_icd10_notes_ppv,
            round((graceful.cnt_notes_only  * const_hit_notes_only_ppv), 2)  as  cnt_notes_only_ppv,
            cnt_icd10,
            cnt_icd10_notes,
            cnt_notes_only,
            const_icd10_notes_ppv,
            const_hit_notes_only_ppv,
            disease_alias
    from graceful
),
site_total as
(
    select  round((cnt_icd10_notes_ppv + cnt_notes_only_ppv), 2) as cnt_total_ppv,
            calculated.*
    from calculated
)
select * from site_total
order by site_total.disease_alias
;
