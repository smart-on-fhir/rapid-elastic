create table rapid__network_ppv as
WITH
disease_list  as ( select distinct disease_alias from rapid__ppv ),
        BCH   as ( select * from rapid__site_ppv_bch ),
        PITT  as ( select * from rapid__site_ppv_pitt),
        UTHSC as ( select * from rapid__site_ppv_uthsc)
SELECT      distinct
            disease_list.disease_alias,
            BCH.cnt_total_ppv       as cnt_total_ppv_bch,
            UTHSC.cnt_total_ppv     as cnt_total_ppv_uthsc,
            PITT.cnt_total_ppv      as cnt_total_ppv_pitt,

            BCH.cnt_icd10           as cnt_icd10_bch,
            UTHSC.cnt_icd10         as cnt_icd10_uthsc,
            PITT.cnt_icd10          as cnt_icd10_pitt,

            BCH.cnt_icd10_notes       as cnt_icd10_notes_bch,
            UTHSC.cnt_icd10_notes     as cnt_icd10_notes_uthsc,
            PITT.cnt_icd10_notes      as cnt_icd10_notes_pitt,

            BCH.cnt_notes_only       as cnt_notes_only_bch,
            UTHSC.cnt_notes_only     as cnt_notes_only_uthsc,
            PITT.cnt_notes_only      as cnt_notes_only_pitt
from        disease_list
left join   BCH on disease_list.disease_alias = BCH.disease_alias
left join   PITT on disease_list.disease_alias = PITT.disease_alias
left join   UTHSC on disease_list.disease_alias = UTHSC.disease_alias
order by    disease_list.disease_alias
;