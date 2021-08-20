from connection import client

def form_query(query):
    return query.replace(',', '')


def get_cities(query):
    body = {
            "query": {
                "simple_query_string": {
                "query": query,
                "fields": ["city^1", "state"],
                "default_operator": "AND",
                }
            }
        }
    return client.search(index="cities", body=body)
    
    
def get_schools(city, distance):

    body = {
        "query": {
            "bool" : {
                "must_not" : {
                    "match" : {"HIGHDEG":"Certificate degree"}
                },
                "filter" : {
                    "geo_distance" : {
                        "distance" : f"{distance} mi",
                        "location" : city['_source']['location'],
                    }
                }
            }
        },
        "aggregations" : {
            "tags" : {
                "terms" : { "field" : "tags" }
            }
        }
    } 
    return client.search(index="schools", body=body)
    
    
def build_school_map(city, distance):
    city_source = city['_source']
    schools= get_schools(city, distance=distance)
    return {
        "city": f"{city_source['city']}, {city_source['state']}",
        "schools": schools['hits']['hits'],
        "aggregations": [k['key'] for k in schools['aggregations']['tags']['buckets']],
        "length": len(schools['hits']['hits'])
    }
    
def join_aggregates(school_map):
    facets = []
    for city in school_map:
        facets += city['aggregations']
    return facets