"""Search Module for interacting with google maps and Elasticsearch"""

import os
from dataclasses import dataclass
import pprint as pp
from typing import Optional

import googlemaps

from connection import local_client as client

gmaps = googlemaps.Client(key=os.environ.get("GMAPSKEY"))


@dataclass
class City:
    """A translation object for the google places API"""

    def __init__(self, place_id):
        self.raw = city = gmaps.place(
            place_id, fields=["type", "geometry", "name", "address_component"]
        )
        self.city = city["result"]["name"]
        self.state_short_name = city["result"]["address_components"][2]["short_name"]
        self.state_long_name = city["result"]["address_components"][2]["long_name"]
        location = city["result"]["geometry"]["location"]
        self.location = f"{location['lat']}, {location['lng']}"
        self.us_country = city["result"]["address_components"][3]["short_name"] == "US"

        pp.pprint(self.raw)  # For demo to review in terminal

    def __str__(self):
        return f"{self.city}, {self.state_short_name}"


def get_cities_by_name(query):
    """generates an array of City objects based on a query"""
    geocode_results = gmaps.places_autocomplete(
        input_text=query,
        types="(cities)",
        components={"country": ["US"]},
    )
    places = [City(city["place_id"]) for city in geocode_results]

    return [place for place in places if place.us_country]


def get_schools(
    tags: list,
    degree_only: bool = True,
    location: Optional[str] = None,
    location_distance="25mi",
    query: Optional[str] = None,
):
    """Run a filter query base on the city."""
    es_bool = {"filter": []}

    if location:
        es_bool["filter"].append(
            {
                "geo_distance": {
                    "distance": location_distance,
                    "location": location,
                }
            }
        )

    if degree_only:
        must_not = [
            {"match": {"HIGHDEG": "Certificate degree"}},
        ]

        es_bool["must_not"] = must_not

    if tags:
        es_bool["filter"].append({"terms": {"tags": [tag for tag in tags if tag]}})

    if query:
        query_search = [
            {
                "simple_query_string": {
                    "query": query,
                    "fields": [
                        "tags^5",
                        "INSTNM",
                        "city_state^2",
                    ],
                }
            }
        ]

        es_bool["must"] = query_search

    es_query = {"bool": es_bool}

    response = client.search(
        index="schools",
        query=es_query,
    )
    pp.pprint(es_query)
    return response
