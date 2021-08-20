from connection import client
import googlemaps
import os

gmaps = googlemaps.Client(key=os.environ.get('GMAPSKEY'))

def form_query(query):
    return query.replace(',', '')


def get_cities(query):
    geocode_results = gmaps.places_autocomplete(
        input_text=query,
        types='(cities)',
        components= {"country": ['US']}
        )
    places = [gmaps.place(result['place_id'], fields=['type', 'geometry', 'name', 'address_component']) for result in geocode_results]
    
    return [place for place in places if place['result']['address_components'][3]['short_name'] == 'US']
    

def get_schools(city, distance, filters):
    must_not = [
          {"match" : {"HIGHDEG":"Certificate degree"}},
          ]
          
    filter = [{
             "geo_distance" : {
                  "distance" : "25 mi",
                  "location" : get_city_lat_long(city)
            }},
        ]
    
    if filters:
        filter.append({'terms': {"tags": filters}})
    
          
    body = {
        
        "query": {
            "bool" : {
                "must_not": must_not,
                "filter" : filter,
            }
          },
            "aggregations" : {
                    "tags" : {
                        "terms": { "field" : "tags" }
                    }
                }
    }
    

    return client.search(index="schools", body=body)

def get_city_name(city):
    city_name = city['result']['name']
    state_name = city['result']['address_components'][2]['short_name']
    return f"{city_name}, {state_name}"
    
def get_city_lat_long(city):
    location = city['result']['geometry']['location']
    lat = location['lat']
    lng = location['lng']
    return f"{lat}, {lng}"
    
def build_school_map(city, distance, filters):
    city_name = get_city_name(city)
    schools= get_schools(city, distance=distance, filters=filters)
    return {
        "city": f"{city_name}",
        "schools": schools['hits']['hits'],
        "aggregations": sorted([k['key'] for k in schools['aggregations']['tags']['buckets']]),
        "length": schools['hits']['total']['value'],
    }
    
def join_aggregates(school_map):
    facets = []
    for city in school_map:
        facets += city['aggregations']
    return facets