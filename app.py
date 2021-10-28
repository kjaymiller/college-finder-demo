import logging
from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from more_itertools import first_true
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired

from connection import client
from city_search import (
    City,
    build_school_map,
    get_cities_by_name,
    get_schools,
)
from search import join_aggregates, search_schools
from facets import build_query

# Testing
# from test_cities import test_cities

# from schools import schools, cities

app = Flask(__name__)
app.secret_key = "the random string"

class SchoolRequest(FlaskForm):
    query = StringField("name", validators=[DataRequired()])


@app.route("/")
def index():
    return render_template(
        "index.html",
        school_form=SchoolRequest(),
    )


@app.route("/search", methods=["GET", "POST"])
def search_cities():
    q = request.args.get("q", form.query.data)
    distance = first_true(
        [
            request.args.get("distance", None),
            form.distance.data,
            25,
        ]
    )

    tags = request.args.get("tags", [])

    if tags:
        tags = tags.split(",")

    states = request.args.get("states", [])
    if states:
        states = states.split(",")

    filtered_items = tags + states
    # print(f"{filtered_items=}")

    if q:
        cities = get_cities_by_name(q)
        # prevent_api_calls
        # cities = test_cities
        schools_by_city = list(
            map(
                lambda x: build_school_map(
                    city=x, tags=tags, states=states
                ),
                cities,
            )
        )
        facets = {
            "tags": {"content": "Show Schools with the following tags", "choices": []},
            "states": {
                "content": "Show Schools in the following states",
                "choices": [],
            },
        }

        aggs = join_aggregates(schools_by_city)

        for agg, agg_item in aggs.items():
            # breakpoint()
            for facet in set(agg_item):
                # logging.warning(f"{tags=}", f"{states=}")
                facets[agg]["choices"].append(
                    {
                        "query": build_query(
                            facet=facet,
                            agg=agg,
                            query=q,
                            tags=tags,
                            states=states,
                        ),
                        "name": facet,
                    }
                )

        return render_template(
            "search.html",
            form=form,
            cities=schools_by_city,
            facets=facets,
            filtered_items=filtered_items,
            q=q,
        )

    return render_template(
        "search.html",
        form=form,
    )


@app.route("/school/<id>")
def get_school(id):
    school = client.get(index="schools", id=id)
    form = SchoolRequest()

    return render_template("school.html", school=school, form=form)


@app.route("/search/schools", methods=["GET", "POST"])
def school_search():
    form = SchoolRequest()

    q = request.args.get("q", form.query.data)
    city = request.args.get("city", None)
    tags = request.args.get("tags", [])
    states = request.args.get("states", [])
    distance = request.args.get("distance", 25)
       
    if tags:
        tags = tags.split(",")

    if states:
        states = states.split(",")
    
    if city:
        city_from_list = first_true(
            get_cities_by_name(city), pred=lambda x:str(x)==city
        )
        cities = [city_from_list]

        response = get_schools(
            query=q,
            tags=tags,
            states=states,
            city=city_from_list,
        )
        
    else: 
        cities = get_cities_by_name(q)

        response = get_schools(
            query=q,
            tags=tags,
            states=states,
        )    

    
    if not response['hits']['total']['value']:
        
        if city:
            
            response = get_schools(
                        city=city_from_list, tags=tags, states=states
                    )

    else:
        cities = []
                     
    return render_template(
        "school_search.html",
        results=response,
        query=q,
        school_form=form,
        cities = cities,
    )

@app.route('/search/city/name/<city_name>')
def search_city_name(city_name):
    form = SchoolRequest()
    city_from_list = first_true(
        get_cities_by_name(city_name), pred=lambda x:x==city_name
    )
    city = City(city_from_list['place_id'])
    print(f"{city=}")
    
    response = get_schools(
        city=city, tags=tags, states=states
    )
    
    return render_template(
        "school_search.html",
        results=response,
        query=q,
        school_form=form,
        cities = cities,
    )


@app.route('/search/city/<place_id>')
def search_city_point(place_id):
    form = SchoolRequest()
    
    city = City(place_id)    
    response = get_schools_by_city(
        city=cities, tags=tags, states=states
    )
    
    return render_template(
        "school_search.html",
        results=response,
        query=q,
        school_form=form,
        cities = cities,
    )
    

if __name__ == "__main__":
    app.run()
