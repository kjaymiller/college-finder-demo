from elasticsearch import Elasticsearch
import os

# Cloud Connection
client = Elasticsearch(
    cloud_id=os.environ.get('CLOUD_ID'),
    http_auth=['elastic', os.environ.get('ES_PWD')]
)
