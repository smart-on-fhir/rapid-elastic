CREATE EXTERNAL TABLE rapid__disease_prevalence (
    disease_name_sheet      string,
    disease_name	        string,
    disease_alias	        string,
    prevalence_max          int,
    prevalence_expect       string
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://cumulus-analytics/andy/disease_prevalence/'
TBLPROPERTIES ("skip.header.line.count"="1")
;