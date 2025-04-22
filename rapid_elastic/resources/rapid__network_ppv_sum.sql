create table rapid__network_ppv_sum as
WITH
prevalence as
(
    select  disease_alias,
            (15 * 1000 * 1000) * prevalence_max / (100*1000) as large_prev
    from    rapid__disease_prevalence
),
sum_sites as
(
    SELECT  distinct
        prevalence.disease_alias,
        prevalence.large_prev,
        round(
            cnt_total_ppv_bch           +
            cnt_total_ppv_cchmc         +
            cnt_total_ppv_chop          +
            cnt_total_ppv_iu            +
            cnt_total_ppv_pitt          +
            cnt_total_ppv_uthsc         +
            cnt_total_ppv_washu, 2)         as cnt_total_ppv,

        round(
            cnt_icd10_notes_ppv_bch     +
            cnt_icd10_notes_ppv_cchmc   +
            cnt_icd10_notes_ppv_chop    +
            cnt_icd10_notes_ppv_iu      +
            cnt_icd10_notes_ppv_pitt    +
            cnt_icd10_notes_ppv_uthsc   +
            cnt_icd10_notes_ppv_washu, 2)   as cnt_icd10_notes_ppv,

        round(
            cnt_notes_only_ppv_bch	    +
            cnt_notes_only_ppv_cchmc    +
            cnt_notes_only_ppv_chop	    +
            cnt_notes_only_ppv_iu	    +
            cnt_notes_only_ppv_pitt	    +
            cnt_notes_only_ppv_uthsc	+
            cnt_notes_only_ppv_washu, 2)	as cnt_notes_only_ppv,

        round(
            cnt_icd10_bch	    +
            cnt_icd10_cchmc	    +
            cnt_icd10_chop	    +
            cnt_icd10_iu	    +
            cnt_icd10_pitt	    +
            cnt_icd10_uthsc	    +
            cnt_icd10_washu, 2)	    as cnt_icd10,

        round(
            cnt_icd10_notes_bch	    +
            cnt_icd10_notes_cchmc	+
            cnt_icd10_notes_chop	+
            cnt_icd10_notes_iu	    +
            cnt_icd10_notes_pitt	+
            cnt_icd10_notes_uthsc	+
            cnt_icd10_notes_washu, 2)	as  cnt_icd10_notes,

        round(
            cnt_notes_only_bch	    +
            cnt_notes_only_cchmc	+
            cnt_notes_only_chop	    +
            cnt_notes_only_iu	    +
            cnt_notes_only_pitt	    +
            cnt_notes_only_uthsc	+
            cnt_notes_only_washu,2)    as cnt_notes_only
from    prevalence,
        rapid__network_ppv
where   rapid__network_ppv.disease_alias = prevalence.disease_alias
)
select      *
from        sum_sites
order by    disease_alias

