# rapid-elastic

### Disease Synonyms Curation
* Disease names and synonyms were **HUMAN expert curated** and assisted via LLM with additional checks within NLM GeneReviews, OrphaNet, and Google searches.
* [query_topics.json](rapid_elastic/resources/query_topics.json) is pre-built example of rare diseases of inborn errors of metabolism.

### Quickstart

1. configure ENV variables query your Elasticsearch server (within your **VPN/firewall**) 
   1. `ELASTIC_HOST` : default http://localhost:9200
   2. `ELASTIC_USER` : basic auth
   3. `ELASTIC_PASS` : basic auth

2. pip3 install rapid-elastic

3. rapid-elastic

### Elasticsearch server 
Read the [server setup docs](docs/server-setup.md).

### KQL (Kibana Query Language) 
* By default, synonyms used to match any "exact phrase" in the note. 
* see `kql_syntax.py` for alternate methods of building Elasticsearch queries.

### Each Elasticsearch hit is saved to "output" folder 
 * `subject_ref`       (FHIR Patient.id)
 * `encounter_ref`     (FHIR Encounter.id)
 * `note_ref`          (FHIR DocumentReference.id) 
 * `group_name`        (optional)
 * `document_title`    (optional)
