CREATE EXTERNAL TABLE aggregate_results_detailed_anon (
    subject_ref     string,
    document_ref    string,
    disease_alias   string,
    asserted        string,
    span            boolean
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://cumulus-analytics/andy/'
TBLPROPERTIES ("skip.header.line.count"="1")
;