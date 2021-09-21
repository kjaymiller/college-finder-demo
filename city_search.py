import googlemaps
import os
from typing import Optional
from connection import client
from dataclasses import dataclass

gmaps = googlemaps.Client(key=os.environ.get("GMAPSKEY"))


class City:
    def __init__(self, place_id, distance=25, unit="mi"):
        city = gmaps.place(
                place_id, fields=["type", "geometry", "name", "address_component"]
        )
        self.raw = city
        self.place_id = place_id
        self.city = city["result"]["name"]
        self.state_short_name = city["result"]["address_components"][2]["short_name"]
        self.state_long_name = city["result"]["address_components"][2]["long_name"]
        self.location = city["result"]["geometry"]["location"]
        self.location = f"{self.location['lat']}, {self.location['lng']}"
        self.us_country = city['result']["address_components"][3]["short_name"] == "US"
        self.geo_filter = {
                "geo_distance": {
                    "distance": f"{distance} {unit}",
                    "location": self.location
                }
            }
        
    def __str__(self):
        return f"{self.city}, {self.state_short_name}"


def get_cities_by_name(query):
    geocode_results = gmaps.places_autocomplete(
        input_text=query, types="(cities)", components={"country": ["US"]}
    )
    places = [
        City(city['place_id'])
        for city in geocode_results
    ]

    place_list = [
        place
        for place in places
        if place.us_country
    ]

    print(geocode_results)
    return place_list


def build_school_map(city, tags, states):
    schools = get_schools(city=city, tags=tags, states=states)
    return {
        "city": f"{city}",
        "schools": schools["hits"]["hits"],
        "aggregations": {
            "tags": sorted(
                [k["key"] for k in schools["aggregations"]["tags"]["buckets"]]
            ),
            "states": sorted(
                [k["key"] for k in schools["aggregations"]["states"]["buckets"]]
            ),
        },
        "length": schools["hits"]["total"]["value"],
    }


def get_schools(
    tags: list,
    states: list,
    degree_only: bool = True,
    city: Optional[City] = None,
    query: Optional[str] = None):
    """
Run a filter query base on the city. If a query is provided, The school list in the region can be used as a filter.
"""
    
    bool = {
        'filter': []
        }
    
    if city:
        bool['filter'].append(city.geo_filter)
        
    if degree_only:
        must_not = [
            {"match": {"HIGHDEG": "Certificate degree"}},
        ]
        
        bool['must_not'] = must_not

    if tags:
        bool['filter'].append({"terms": {"tags": tags}})

    if states:
        bool['filter'].append({"terms": {"ST_FIPS": states}})
    
    if query:
        query_search = [
            {
                "simple_query_string": {
                    "query": query,
                    "fields": [
                        "tags",
                        "INSTNM", "city_state",
                    ],
                    }
            }
        ]
        
        bool['must'] = query_search
        
    body = {
        "query": {
            "bool": bool
        },
        "aggs": {
            "tags": {
                "terms": {
                    "field": "tags",
                },
            },
            "states": {"terms": {"field": "ST_FIPS"}},
        },
    }
    
    response = client.search(
        index="schools", body=body
    )
    return response
