create table rapid__network_ppv_sum_checks2 as
WITH
ppv_percent as
(
    select  distinct ppv,
            cast(round(ppv*100, 1) as varchar) as ppv_string,
            hit_icd10_notes,
            hit_notes_only,
            disease_alias
    from    rapid__ppv
),
ppv_sum as
(
    select      distinct
                rapid__network_ppv_sum.*,
                cast(cnt_icd10_notes        as varchar) as cnt_icd10_notes_str,
                cast(cnt_notes_only         as varchar) as cnt_notes_only_str,
                cast(cnt_total_ppv          as varchar) as cnt_total_ppv_str,
                cast(cnt_icd10_notes_ppv    as varchar) as cnt_icd10_notes_ppv_str,
                cast(cnt_notes_only_ppv     as varchar) as cnt_notes_only_ppv_str,
                rapid__icd10_str.icd10_list
    from        rapid__icd10_str,
                rapid__network_ppv_sum
    where       rapid__network_ppv_sum.disease_alias =
                rapid__icd10_str.disease_alias
),
check_list as
(
    select      distinct
                cnt_total_ppv > (15*1000) as warn_15k,
                cnt_total_ppv > (7500)    as warn_7500,
                round(cnt_total_ppv / large_prev, 2) as ratio_large_prev,
                round(cnt_notes_only_ppv / cnt_icd10_notes_ppv, 2) as ratio_icd10_notes,
                ppv_sum.*
    from        ppv_sum
    order by    disease_alias
),
check_bool as
(
    select      distinct
                (warn_15k)    OR
                ( ratio_large_prev > 5)  OR
                ( (ratio_large_prev > 2) and (ratio_icd10_notes > 10) )  OR
                ( (ratio_large_prev > 3) and (ratio_icd10_notes > 5) )   OR
                ( (ratio_large_prev > 4) and (ratio_icd10_notes > 2) )   as failed,
                check_list.*
    from        check_list
),
n_case_icd_nlp as
(
    select  check_bool.disease_alias,
            check_bool.cnt_icd10_notes_ppv,
            concat(cnt_icd10_notes_ppv_str,
                    ' patients with both an ICD code ',
                    check_bool.icd10_list,
                    ' and note mentions (PPV_icd_nlp=',
                    ppv_percent.ppv_string,
                    '% confirmed out of ',
                    cast(cnt_icd10_notes as varchar),
                    ' potential cases) ') as report_text
    from        check_bool,
                ppv_percent
    where       check_bool.disease_alias = ppv_percent.disease_alias
    and         ppv_percent.hit_icd10_notes
),
n_case_notes_only as
(
    select  distinct
            check_bool.disease_alias,
            check_bool.cnt_notes_only_ppv,
            concat(cnt_notes_only_ppv_str,
                    ' patients with notes mentions only ',
                    '(PPV_notes_only=',
                    ppv_percent.ppv_string,
                    '% confirmed out of ',
                    cast(cnt_notes_only as varchar),
                    ' potential cases); ') as report_text
    from        check_bool,
                ppv_percent
    where       check_bool.disease_alias = ppv_percent.disease_alias
    and         ppv_percent.hit_notes_only
),
column_labels as
(
    select  distinct
            case
            when    not check_bool.failed
            then    check_bool.cnt_total_ppv
            else    check_bool.cnt_icd10_notes_ppv end as column_J,
            case
            when    not check_bool.failed
            then    concat(cnt_total_ppv_str, '=',
                            n_case_icd_nlp.report_text,
                            '  + ',
                            n_case_notes_only.report_text)
            else    concat(cnt_icd10_notes_ppv_str, '=',
                            n_case_icd_nlp.report_text)
            end     as column_L,
            check_bool.failed,
            check_bool.warn_15k,
            check_bool.warn_7500,
            check_bool.ratio_large_prev,
            check_bool.ratio_icd10_notes,
            check_bool.large_prev,
            check_bool.cnt_total_ppv,
            check_bool.cnt_icd10_notes_ppv,
            check_bool.cnt_notes_only_ppv,
            check_bool.cnt_icd10,
            check_bool.cnt_icd10_notes,
            check_bool.cnt_notes_only,
            check_bool.icd10_list,
            check_bool.disease_alias
    from check_bool
    left join   n_case_icd_nlp      on check_bool.disease_alias = n_case_icd_nlp.disease_alias
    left join   n_case_notes_only   on check_bool.disease_alias = n_case_notes_only.disease_alias
    order by check_bool.disease_alias
),
outliers as
(
    select  n_case_notes_only.cnt_notes_only_ppv as column_J,
            n_case_notes_only.report_text as column_L,
            column_labels.failed,
            column_labels.warn_15k,
            column_labels.warn_7500,
            column_labels.ratio_large_prev,
            column_labels.ratio_icd10_notes,
            column_labels.large_prev,
            column_labels.cnt_total_ppv,
            column_labels.cnt_icd10_notes_ppv,
            column_labels.cnt_notes_only_ppv,
            column_labels.cnt_icd10,
            column_labels.cnt_icd10_notes,
            column_labels.cnt_notes_only,
            column_labels.icd10_list,
            column_labels.disease_alias
    from    column_labels,
            n_case_notes_only
    where   column_labels.column_L is null
    and     column_labels.disease_alias = n_case_notes_only.disease_alias
),
union_outliers as
(
    select * from column_labels where column_L is NOT null
    UNION
    select * from outliers
)
select      prev.disease_name_sheet,
            prev.icd10_by_api,
            union_outliers.*
from        rapid__disease_prevalence as prev
left join   union_outliers  on  prev.disease_alias = union_outliers.disease_alias
;


