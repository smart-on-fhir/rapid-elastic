-- ###########################################################################
-- Overall PPV scores

--    rapid__aggregate-results-detailed-anon.sql
--    rapid__ppv.sql

-- ###########################################################################
-- BCH

drop table if exists rapid__site_count;
drop table if exists rapid__site_ppv;

create      table   rapid__site_count as
select *    from    rapid__site_count_bch
order by    disease_alias;

-- rapid__site_ppv.sql

create      table   rapid__site_ppv_bch as
select *    from rapid__site_ppv
order by    disease_alias;

--    select
--        disease_alias,
--        (cnt_total_ppv / cnt_icd10) as ratio,
--        cnt_total_ppv, cnt_icd10
--    from rapid__site_ppv_bch
--    order by ratio desc

-- ###########################################################################
drop table if exists rapid__site_count;
drop table if exists rapid__site_ppv;

create      table   rapid__site_count as
select *    from    rapid__site_count_cchmc
order by    disease_alias;

-- rapid__site_ppv.sql

create      table   rapid__site_ppv_cchmc as
select *    from rapid__site_ppv
order by    disease_alias;

-- ###########################################################################
drop table if exists rapid__site_count;
drop table if exists rapid__site_ppv;

create      table   rapid__site_count as
select *    from    rapid__site_count_pitt
order by    disease_alias;

-- rapid__site_ppv.sql

create      table   rapid__site_ppv_pitt as
select *    from rapid__site_ppv
order by    disease_alias;
-- ###########################################################################
drop table if exists rapid__site_count;
drop table if exists rapid__site_ppv;

create      table   rapid__site_count as
select *    from    rapid__site_count_uthsc
order by    disease_alias;

-- rapid__site_ppv.sql

create      table   rapid__site_ppv_uthsc as
select *    from rapid__site_ppv
order by    disease_alias;

-- ###########################################################################
drop table if exists rapid__site_count;
drop table if exists rapid__site_ppv;

create      table   rapid__site_count as
select *    from    rapid__site_count_washu
order by    disease_alias;

-- rapid__site_ppv.sql

create      table   rapid__site_ppv_washu as
select *    from rapid__site_ppv
order by    disease_alias;

