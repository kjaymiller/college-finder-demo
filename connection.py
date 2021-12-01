from elasticsearch import Elasticsearch
import os

# Cloud Connection
cloud_client = Elasticsearch(
    cloud_id=os.environ.get('CLOUD_ID'),
    http_auth=['elastic', os.environ.get('ES_CLOUD_PWD')]
)


# Local Connection
local_client = Elasticsearch(
    hosts = [os.environ.get('ES_LOCAL_HOST', 'localhost')],
    http_auth=['elastic', os.environ.get('ES_LOCAL_PWD')]
)