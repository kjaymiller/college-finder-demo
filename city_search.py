"""Search Module for interacting with google maps and Elasticsearch"""

import os
import pprint as pp
from typing import Optional

import googlemaps

from connection import local_client as client

gmaps = googlemaps.Client(key=os.environ.get("GMAPSKEY"))


class City:
    """A translation object for the google places API"""

    def __init__(self, place_id):
        self.raw = city = gmaps.place(
            place_id, fields=["type", "geometry", "name", "address_component"]
        )
        self.place_id = place_id
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
    geocode_results = gmaps.places_autocomplete(
        input_text=query, types="(cities)", components={"country": ["US"]}
    )
    places = [City(city["place_id"]) for city in geocode_results]

    place_list = [place for place in places if place.us_country]

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
    location: Optional[str] = None,
    location_distance="25mi",
    query: Optional[str] = None,
):
    """Run a filter query base on the city."""
    bool = {"filter": []}

    if location:
        bool["filter"].append(
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

        bool["must_not"] = must_not

    if tags:
        bool["filter"].append({"terms": {"tags": [tag for tag in tags if tag]}})

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

        bool["must"] = query_search

    query = {"bool": bool}
    aggs = {
        "tags": {
            "terms": {
                "field": "tags",
            },
        },
        "states": {"terms": {"field": "ST_FIPS"}},
    }

    response = client.search(
        index="schools",
        query=query,
        aggs=aggs,
    )
    pp.pprint(query)
    return response
