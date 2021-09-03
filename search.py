import os
from connection import client
from typing import Optional


def search_schools(query):
    body = {
        "query": {
            "simple_query_string": {
                "query": query,
                "fields": [
                    "tags",
                     "INSTNM", "city_state",
                 ],
            }
        }
    }
    
    response = client.search(index="schools", body=body)    
    return response  


def get_schools(
    city: str,
    distance: int,
    tags: list,
    states: list,
    degree: bool = True,
    query: Optional[str] = None,
):
    """
Run a filter query base on the city. If a query is provided, The school list in the region can be used as a filter.
"""
    
    bool = {
        }
            
    filter = [
    ]

    if city:
        city_filter = {
            "geo_distance": {
                "distance": f"{distance} mi",
                "location": get_city_lat_long(city),
            }
        }

        filter.append(city_filter)
        
    if tags:
        filter.append({"terms": {"tags": tags}})

    if states:
        filter.append({"terms": {"ST_FIPS": states}})

    if filter:
        bool['filter'] = filter
    
    if degree:
        must_not = [
            {"match": {"HIGHDEG": "Certificate degree"}},
        ]
        
        bool['must_not'] = must_not
    
    if query:
        query_search = {
            "simple_query_string": {
                "query": query,
                "fields": [
                    "tags",
                    "INSTNM", "city_state",
                ],
            }
        }

    body = {
        "aggs": {
            "tags": {"terms": {"field": "tags"}},
            "states": {"terms": {"field": "ST_FIPS"}},
        }
    }
    
    if query:
        bool['should'] = query_search
        body['query'] = {"bool": bool}
    
    print(body)
    response = client.search(index="schools", body=body)
    return response


def join_aggregates(school_map):
    facets = {
        "tags": [],
        "states": []
}
    for city in school_map:
        facets['tags'] += city["aggregations"]['tags']
        facets['states'] += city["aggregations"]['states']
        
    return facets
