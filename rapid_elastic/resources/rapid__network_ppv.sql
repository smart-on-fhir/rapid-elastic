create table rapid__network_ppv as
WITH
disease_list  as ( select distinct disease_alias from rapid__ppv ),
        BCH   as ( select * from rapid__site_ppv_bch ),
        CCHMC as ( select * from rapid__site_ppv_cchmc ),
        CHOP  as ( select * from rapid__site_ppv_chop ),
        PITT  as ( select * from rapid__site_ppv_pitt),
        REGI  as ( select * from rapid__site_ppv_regi),
        UTHSC as ( select * from rapid__site_ppv_uthsc),
        WASHU as ( select * from rapid__site_ppv_washu)
SELECT      distinct
            disease_list.disease_alias,
            coalesce(BCH.cnt_total_ppv,     0)  as cnt_total_ppv_bch,
            coalesce(CCHMC.cnt_total_ppv,   0)  as cnt_total_ppv_cchmc,
            coalesce(CHOP.cnt_total_ppv,    0)  as cnt_total_ppv_chop,
            coalesce(REGI.cnt_total_ppv,    0)  as cnt_total_ppv_iu,
            coalesce(PITT.cnt_total_ppv,    0)  as cnt_total_ppv_pitt,
            coalesce(UTHSC.cnt_total_ppv,   0)  as cnt_total_ppv_uthsc,
            coalesce(WASHU.cnt_total_ppv,   0)  as cnt_total_ppv_washu,

            coalesce(BCH.cnt_icd10_notes_ppv,   0)  as cnt_icd10_notes_ppv_bch,
            coalesce(CCHMC.cnt_icd10_notes_ppv, 0)  as cnt_icd10_notes_ppv_cchmc,
            coalesce(CHOP.cnt_icd10_notes_ppv,  0)  as cnt_icd10_notes_ppv_chop,
            coalesce(REGI.cnt_icd10_notes_ppv,  0)  as cnt_icd10_notes_ppv_iu,
            coalesce(PITT.cnt_icd10_notes_ppv,  0)  as cnt_icd10_notes_ppv_pitt,
            coalesce(UTHSC.cnt_icd10_notes_ppv, 0)  as cnt_icd10_notes_ppv_uthsc,
            coalesce(WASHU.cnt_icd10_notes_ppv, 0)  as cnt_icd10_notes_ppv_washu,

            coalesce(BCH.cnt_notes_only_ppv,    0)  as cnt_notes_only_ppv_bch,
            coalesce(CCHMC.cnt_notes_only_ppv,  0)  as cnt_notes_only_ppv_cchmc,
            coalesce(CHOP.cnt_notes_only_ppv,   0)  as cnt_notes_only_ppv_chop,
            coalesce(REGI.cnt_notes_only_ppv,   0)  as cnt_notes_only_ppv_iu,
            coalesce(PITT.cnt_notes_only_ppv,   0)  as cnt_notes_only_ppv_pitt,
            coalesce(UTHSC.cnt_notes_only_ppv,  0)  as cnt_notes_only_ppv_uthsc,
            coalesce(WASHU.cnt_notes_only_ppv,  0)  as cnt_notes_only_ppv_washu,

            coalesce(BCH.cnt_icd10,     0)  as cnt_icd10_bch,
            coalesce(CCHMC.cnt_icd10,   0)  as cnt_icd10_cchmc,
            coalesce(CHOP.cnt_icd10,    0)  as cnt_icd10_chop,
            coalesce(REGI.cnt_icd10,    0)  as cnt_icd10_iu,
            coalesce(PITT.cnt_icd10,    0)  as cnt_icd10_pitt,
            coalesce(UTHSC.cnt_icd10,   0)  as cnt_icd10_uthsc,
            coalesce(WASHU.cnt_icd10,   0)  as cnt_icd10_washu,

            coalesce(BCH.cnt_icd10_notes,   0)  as cnt_icd10_notes_bch,
            coalesce(CCHMC.cnt_icd10_notes, 0)  as cnt_icd10_notes_cchmc,
            coalesce(CHOP.cnt_icd10_notes,  0)  as cnt_icd10_notes_chop,
            coalesce(REGI.cnt_icd10_notes,  0)  as cnt_icd10_notes_iu,
            coalesce(PITT.cnt_icd10_notes,  0)  as cnt_icd10_notes_pitt,
            coalesce(UTHSC.cnt_icd10_notes, 0)  as cnt_icd10_notes_uthsc,
            coalesce(WASHU.cnt_icd10_notes, 0)  as cnt_icd10_notes_washu,

            coalesce(BCH.cnt_notes_only,    0)  as cnt_notes_only_bch,
            coalesce(CCHMC.cnt_notes_only,  0)  as cnt_notes_only_cchmc,
            coalesce(CHOP.cnt_notes_only,   0)  as cnt_notes_only_chop,
            coalesce(REGI.cnt_notes_only,   0)  as cnt_notes_only_iu,
            coalesce(PITT.cnt_notes_only,   0)  as cnt_notes_only_pitt,
            coalesce(UTHSC.cnt_notes_only,  0)  as cnt_notes_only_uthsc,
            coalesce(WASHU.cnt_notes_only,  0)  as cnt_notes_only_washu
from        disease_list
left join   BCH on disease_list.disease_alias   = BCH.disease_alias
left join   CCHMC on disease_list.disease_alias = CCHMC.disease_alias
left join   CHOP on disease_list.disease_alias  = CHOP.disease_alias
left join   PITT on disease_list.disease_alias  = PITT.disease_alias
left join   REGI on disease_list.disease_alias  = REGI.disease_alias
left join   UTHSC on disease_list.disease_alias = UTHSC.disease_alias
left join   WASHU on disease_list.disease_alias = WASHU.disease_alias
order by    disease_list.disease_alias
;