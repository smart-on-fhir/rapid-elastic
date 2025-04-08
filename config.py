import os

# HTTP Basic Auth and output destination
ELASTIC_USER = os.environ.get("ELASTIC_USER")
ELASTIC_PASS = os.environ.get("ELASTIC_PASS")

# Synchronize output to remote target for LLM processing
ELASTIC_SYNC = os.environ.get("ELASTIC_SYNC")
