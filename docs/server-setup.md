# Elasticsearch Server Setup

## Set up Elasticsearch itself

Follow the
[official setup guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup.html).

At BCH, we use the Docker images, running on a 16GB EC2 machine.
We run it like:
```commandline
ES_PASS="xxx"

docker run -d --name es01 --net elastic -m 8GB \
  -v $HOME/elasticsearch:/host \
  -e ELASTIC_PASSWORD=$ES_PASS \
  -e discovery.type=single-node \
  -e path.data=/host/data \
  -e path.logs=/host/logs \
  -e xpack.security.http.ssl.enabled=false \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.3
```

## Set up Kibana

Kibana is the Elasticsearch dashboard.

Follow the
[official setup guide](https://www.elastic.co/guide/en/kibana/current/setup.html).

At BCH, we use the Docker images, running on the same machine as Elasticsearch.
We run it like:
```commandline
ELASTICSEARCH_IP=x.x.x.x
KIB_PASS="yyy"

curl -w '\n' --user elastic:xxx -X POST http://$ELASTICSEARCH_IP:9200/_security/user/kibana_system/_password --json "{\"password\": \"$KIB_PASS\"}"

docker run -d --name kib01 --net elastic \
  -v $HOME/kibana:/host \
  -e ELASTICSEARCH_HOSTS=http://es01:9200 \
  -e ELASTICSEARCH_USERNAME=kibana_system \
  -e "ELASTICSEARCH_PASSWORD=$KIB_PASS" \
  -e KBN_PATH_CONF=/host \
  docker.elastic.co/kibana/kibana:8.17.3
```

## Set up Logstash

Logstash is the Elasticsearch data ingestion engine.

Unlike Elasticsearch and Kibana, Logstash _can_ be just a one-and-done run.
It is set up to sit there and watch the input directories for new content,
but that's not necessary.

Logstash also requires a lot of custom work to map your clinical data as Elasticsearch events.
Let's get that work in place before we run Logstash.

### Install inscriptis

If you have clinical notes in HTML format,
you will want to run a local [inscriptis](https://github.com/weblyzard/inscriptis) http server,
which we will use to convert those HTML clinical notes into plain text.

This will look like:
```commandline
pipx install inscriptis

inscriptis-api
```

### Configure your pipeline

Logstash will need a pipeline configuration file to turn your clinical data into Elasticsearch
events.

At BCH, we use something like the pipeline below,
which operates on an archive of bulk FHIR NDJSON exports and a Cumulus anonymization scheme.
Your situation may be different, but hopefully this can be a starting place.
- Replace `YOUR_BUCKET_NAME` with your bucket name
- Replace `YOUR_PATH_TO_FHIR_NDJSON_ARCHIVES` to a folder that holds your NDJSON archives
- Replace `YOUR_SALT` with the salt value from your Cumulus ETL PHI folder (in `codebook.json`)
- Replace `YOUR_ELASTICSEARCH_IP` with the Docker IP for your Elasticsearch server
- Replace `YOUR_ELASTICSEARCH_PASS` with the `elastic` user's password
- Ideally your archive has one subfolder per FHIR Group you used for the export.
  If not, you can remove the "Add group_name" section - that's there to help you if you ever want
  to go back to the archives and find data on a patient again - it's a pointer to which group a
  document came from (in BCH's case, we have over a hundred Groups that we aggregate data from,
  so this is useful bookkeeping, but it may not be in your case)

If you do customize this pipeline for a different data source,
make sure you keep the event field names the same as the RAPID scripts expect these:
- note: the raw clinical note text from FHIR DocumentReference
- fhir_ref: FHIR DiagnosticReport or DocumentReference ID (original)
- anon_ref: FHIR DiagnosticReport or DocumentReference ID (anonymized)
- anon_subject_ref: FHIR Patient ID (anonymized)
- anon_encounter_ref: FHIR Encounter ID (anonymized)
- group_name: a marker back to how to find this document back in the archives
- codes: codes saying what kind of document this is

```
input {
  s3 {
    bucket => "YOUR_BUCKET_NAME"
    prefix => "YOUR_PATH_TO_FHIR_NDJSON_ARCHIVES"
    # There is no "include_pattern" option unfortunately. So to only
    # include .ndjson files, we must negate the include into an exclude.
    # Leading to this gross regex. See https://rubular.com/ to test it.
    exclude_pattern => "^(?!.*(DiagnosticReport|DocumentReference).*\.ndjson$).*$"
    watch_for_new_files => false
    codec => json_lines {
      target => "fhir"
      decode_size_limit_bytes => 104857600 # 100MB
    }
  }
}
filter {
  if [fhir][resourceType] not in ["DiagnosticReport", "DocumentReference"] {
    drop {}
  }
  if [fhir][resourceType] == "DiagnosticReport" {
    # Copy attachment array
    mutate {
      copy => { "[fhir][presentedForm]" => "[@metadata][attachments]" }
    }
    # Set timestamp from clinical date (or admin date as fallback)
    if [fhir][effectiveDateTime] {
      date {
        match => [ "[fhir][effectiveDateTime]", "ISO8601" ]
      }
    }
    else if [fhir][effectivePeriod][start] {
      date {
        match => [ "[fhir][effectivePeriod][start]", "ISO8601" ]
      }
    }
    else if [fhir][issued] {
      date {
        match => [ "[fhir][issued]", "ISO8601" ]
      }
    }
    # Set some basic metadata
    mutate {
      copy => {
        "[fhir][subject][reference]" => "[@metadata][subject]"
        "[fhir][encounter][reference]" => "[@metadata][encounter]"
        "[fhir][code]" => "[codes]"
      }
    }
  }
  if [fhir][resourceType] == "DocumentReference" {
    ruby {
      code => "
        attachments = []
        contents = event.get('[fhir][content]')
        if contents
          contents.each_with_index do |value, index|
            attachments.append(value['attachment'])
          end
        end
        event.set('[@metadata][attachments]', attachments)
      "
    }
    # Set timestamp from clinical date (or admin date as fallback)
    if [fhir][context][period][start] {
      date {
        match => [ "[fhir][context][period][start]", "ISO8601" ]
      }
    }
    if [fhir][date] {
      date {
        match => [ "[fhir][date]", "ISO8601" ]
      }
    }
    # Set some basic metadata
    mutate {
      copy => {
        "[fhir][subject][reference]" => "[@metadata][subject]"
        "[fhir][context][encounter][0][reference]" => "[@metadata][encounter]"
        "[fhir][type]" => "[codes]"
      }
    }
  }
  # Find and parse html attachments
  if [@metadata][attachments] {
    ruby {
      code => "
        attachments = event.get('[@metadata][attachments]')
        attachments.each_with_index do |value, index|
          if value['data'] && value['contentType'].start_with?('text/html')
            event.set('note', Base64.decode64(value['data'].force_encoding('UTF-8')))
            break
          end
        end
      "
    }
    if [note] {
      http {
        url => "http://localhost:5000/get_text"
        verb => "POST"
        headers => { "Content-Type" => "text/html; encoding=UTF-8" }
        body => "%{note}"
        target_body => "note"
      }
    }
  }
  # Anonymize some IDs
  ruby {
    init => "
      require 'openssl'
      salt = 'YOUR_SALT'
      @key = salt.scan(/../).collect { |c| c.to_i(16).chr }.join
    "
    code => "
      resourceType = event.get('[fhir][resourceType]')
      id = event.get('[fhir][id]')
      anon_ref = resourceType + '/' + OpenSSL::HMAC.hexdigest('SHA256', @key, id)
      event.set('anon_ref', anon_ref)

      if event.get('[@metadata][subject]')
        subject_id = event.get('[@metadata][subject]').split('/').last
        anon_subject_id = OpenSSL::HMAC.hexdigest('SHA256', @key, subject_id)
        event.set('anon_subject_ref', 'Patient/' + anon_subject_id)
      end

      if event.get('[@metadata][encounter]')
        encounter_id = event.get('[@metadata][encounter]').split('/').last
        anon_encounter_id = OpenSSL::HMAC.hexdigest('SHA256', @key, encounter_id)
        event.set('anon_encounter_ref', 'Encounter/' + anon_encounter_id)
      end
    "
  }
  # Add group_name
  ruby {
    code => "
      key = event.get('[@metadata][s3][key]')
      group_name = key.split('/')[2]
      event.set('group_name', group_name)
    "
  }
  # Final easy tweaks
  mutate {
    copy => {
      "[fhir][resourceType]" => "resourceType"
    }
    add_field => {
      "fhir_ref" => "%{[fhir][resourceType]}/%{[fhir][id]}"
    }
    remove_field => [ "fhir" ]
  }
}
output {
  elasticsearch {
    # Hardcode this IP because logstash is running on the host network,
    # for easy access to the inscriptis web server
    hosts => "http://YOUR_ELASTICSEARCH_IP:9200"
    user => "elastic"
    password => "YOUR_ELASTICSEARCH_PASS"
    index => "fhir"
    data_stream => false
    action => "update"
    doc_as_upsert => true
    document_id => "%{fhir_ref}"
  }
}
```

Put this in a file called `pipeline.conf` - we'll use it in the next step.

### Run Logstash itself

Follow the
[official setup guide](https://www.elastic.co/guide/en/logstash/current/setup-logstash.html).

At BCH, we use the Docker images, running on the same machine as Elasticsearch.
We run it like:
```commandline
AWS_PROFILE=zzz

docker run -d --rm \
  --name log01 \
  --net host \
  --add-host host.docker.internal:host-gateway \
  --log-driver none \
  -e AWS_PROFILE=$AWS_PROFILE \
  -v $HOME/logstash:/host \
  -v $HOME/.aws/credentials:/root/.aws/credentials \
  -v $HOME/logstash/pipeline.conf:/usr/share/logstash/pipeline/pipeline.conf \
  docker.elastic.co/logstash/logstash-oss:8.17.3 \
  --path.data /host/data \
  --path.logs /host/logs
```

This could take a while to fill up Elasticsearch.
But as it starts to fill it, you should be able to see a `fhir` index in your Kibana dashboard.
