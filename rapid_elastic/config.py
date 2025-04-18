import os

###############################################################################
# Elastic Search configuration
#
# See also `elastic_helper.py`

#   ElasticField defines fields elastic search expects to be present
#
#   You may optionally turn fields on/off using
#       FIELD_INCLUDES
#       FIELD_EXCLUDES
#
###############################################################################
ELASTIC_HOST = os.environ.get('ELASTIC_URL', 'http://localhost:9200')

# HTTP Basic Auth and output destination
ELASTIC_USER = os.environ.get("ELASTIC_USER")
ELASTIC_PASS = os.environ.get("ELASTIC_PASS")

###############################################################################

SCP_HOST = os.environ.get("SCP_HOST")
SCP_PORT = os.environ.get("SCP_PORT", 22)
SCP_USER = os.environ.get("SCP_USER")
SCP_DIR = os.environ.get("SCP_DIR")
