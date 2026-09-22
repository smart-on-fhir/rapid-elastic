import pandas
import pytest
from elasticsearch import Elasticsearch
from testcontainers.community.elasticsearch import ElasticSearchContainer
import os
from pathlib import Path
import json
import rapid_elastic.config as config

@pytest.fixture(scope="module")
def es_client():
    """
    This creates a 'virtual' ES service that we use to mock the real one.
    It is the same ES version as we have in our instances.
    We fill it up with mock data from tests/end2end/es_content
    """
    print("Starting Elasticsearch service...")
    with ElasticSearchContainer("docker.elastic.co/elasticsearch/elasticsearch:8.19.3")\
            .with_env("ELASTIC_PASSWORD", "pass")\
            .with_env("xpack.security.enabled", "false")\
            .with_env("xpack.security.http.ssl.enabled", "false")\
            .with_env("discovery.type", "single-node")\
            as container:
        url = f"http://{container.get_container_host_ip()}:{container.get_exposed_port(container.port)}"
        client = Elasticsearch(url)

        config.ELASTIC_HOST = url
        config.ELASTIC_USER = "elastic"
        config.ELASTIC_PASS = "pass"

        client.cluster.health(wait_for_status="yellow")  # wait until ready

        if client.ping():
            print("Temporary Elasticsearch healthy {}:".format(url))
            print(client.info())

        for file in (Path(__file__).parent / "es_content").iterdir():
            if not file.is_file():
                continue

            with open(file) as f:
                doc = json.load(f)

            client.index(
                index="test",
                id=file.name,
                document=doc,
                refresh=True
            )

        yield client
        client.close()

def test_basic(es_client):
    """
    This test checks a single query file (cardiac) output.
    """
    import rapid_elastic.pipeline as pipeline

    results = pipeline.pipe_batch(
        Path(__file__).parent / "test_query_topics_basic",
        Path(__file__).parent.parent / "output"
    )

    res = pandas.read_csv(results[0])

    assert res.shape[0] == 1  # must only have 1 entry
    assert res["subject_ref"].item() == "Patient/a"
    assert res["encounter_ref"].item() == "Encounter/a"
    assert res['note_ref'].item() == "DiagnosticReport/a"
    assert res['group_name'].item() == "groupname1"
    assert res['document_title'].item() == "CBC and differential"