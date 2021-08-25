import logging
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from more_itertools import first_true
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired

from connection import client
from search import build_school_map, get_cities, get_schools, join_aggregates
from facets import build_query
from test_cities import test_cities

# from schools import schools, cities

app = Flask(__name__)
app.secret_key = "the random string"


class SchoolRequest(FlaskForm):
    query = StringField("name", validators=[DataRequired()])
    distance = SelectField("distance", choices=[25, 50, 100])


@app.route("/")
def index():
    return render_template("index.html", form=SchoolRequest())


@app.route("/search", methods=["GET", "POST"])
def search_cities():
    form = SchoolRequest()

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
        # cities = get_cities(q) # prevent_api_calls
        cities = test_cities
        schools_by_city = list(
            map(
                lambda x: build_school_map(x, distance=distance, tags=tags, states=states),
                cities,
            )
        )
        facets = {
            "tags": {
                "content": "Show Schools with the following tags",
                "choices": []
            },
            "states": {
                "content": "Show Schools with the following tags",
                "choices": []
             }
         }
        
        aggs = join_aggregates(schools_by_city)
        
        for agg, agg_item in aggs.items():
            # breakpoint()
            for facet in set(agg_item):
                # logging.warning(f"{tags=}", f"{states=}")
                facets[agg]['choices'].append({
                    "query": build_query(
                        facet=facet,
                        agg=agg,
                        query= q,
                        tags= tags,
                        states=states,
                    ),
                    "name": facet
            })
        
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

@app.route("/school/id")
def get_school():
    doc = client.get(index="schools",id=id)
    return render_template('school.html', doc=doc)

@app.route("/search/schools", methods=['GET', 'POST'])
def search_schools():
    q = request.args.get("q", form.query.data)
    
    
if __name__ == "__main__":
    app.run()
