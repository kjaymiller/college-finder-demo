import os

import googlemaps

from connection import client

gmaps = googlemaps.Client(key=os.environ.get("GMAPSKEY"))


def get_cities(query):
    geocode_results = gmaps.places_autocomplete(
        input_text=query, types="(cities)", components={"country": ["US"]}
    )
    places = [
        gmaps.place(
            result["place_id"], fields=["type", "geometry", "name", "address_component"]
        )
        for result in geocode_results
    ]

    return [
        place
        for place in places
        if place["result"]["address_components"][3]["short_name"] == "US"
    ]


def get_schools(city: str, distance: int, tags: list, states:list):
    must_not = [
        {"match": {"HIGHDEG": "Certificate degree"}},
    ]

    filter = [
        {"geo_distance": {"distance": f"{distance} mi", "location": get_city_lat_long(city)}},
    ]
    
    if tags:
        filter.append(
            {"terms": {"tags": tags}}
        )

    if states:
        filter.append(
            {"terms": {"ST_FIPS": states}}
        )
        
    body = {
        "query": {
            "bool": {
                "must_not": must_not,
                "filter": filter,
            }
        },
        "aggs": {
            "tags": {
                "terms": {
                    "field": "tags",
                },
            },
            "states": {
                "terms": {
                    "field": "ST_FIPS"
                }
            }
        },
    }
    response = client.search(index="schools", body=body)
    return response


def get_city_name(city):
    city_name = city["result"]["name"]
    state_name = city["result"]["address_components"][2]["short_name"]
    return f"{city_name} {state_name}"


def get_city_lat_long(city):
    location = city["result"]["geometry"]["location"]
    location = f"{location['lat']}, {location['lng']}"
    return location


def build_school_map(city, distance, tags, states):
    city_name = get_city_name(city)
    schools = get_schools(city, distance=distance, tags=tags, states=states)
    return {
        "city": f"{city_name}",
        "schools": schools["hits"]["hits"],
        "aggregations": {
            "tags": sorted(
                [k["key"] for k in schools["aggregations"]["tags"]["buckets"]]
                ),
            "states": sorted(
                [k["key"] for k in schools["aggregations"]["states"]["buckets"]]
                )
            },
        "length": schools["hits"]["total"]["value"],
    }


def search_schools(query):
    body = {
        "query": {
            "simple_query_search": {
                "query": query,
                "fields": ["tags", "INSTNM", "city_state"],
            }
        }
    }
    return client.search(index="schools", body=body)


def join_aggregates(school_map):
    facets = {
        "tags": [],
        "states": []
}
    for city in school_map:
        facets['tags'] += city["aggregations"]['tags']
        facets['states'] += city["aggregations"]['states']
        
    return facets
