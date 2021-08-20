from connection import client
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired
from search import (
        get_cities,
        get_schools,
        build_school_map,
        join_aggregates,
    )
from more_itertools import first_true

# from schools import schools, cities

app = Flask(__name__)
app.secret_key = "the random string"

def build_query(
    facet: str,
    q: str,
    filters: list) -> str:
    """builds the query to toggle filters"""
    if facet in filters:
        f = filters.remove(facet)
    elif filters:
        f = filters.append(facet)
    else:
        f = [facet]
        
    if f:
        f = ','.join(f)
        return f"/search?q={q}&filters={f}"        

    else:
        return f"/search?q={q}"
        
class SchoolRequest(FlaskForm):
    query = StringField("name", validators=[DataRequired()])
    distance = SelectField("distance", choices=[25, 50, 100])

@app.route("/")
def index():
    return render_template("index.html", form=SchoolRequest())


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SchoolRequest()
    
    q = request.args.get('q', form.query.data)
    distance = first_true([
        request.args.get('distance', None),
        form.distance.data,
        25,
    ])
        
    filters = request.args.get('filters', [])
    
    if filters:
        filters = filters.split(',')
    
    if q:
        cities = get_cities(q)
        print(cities)
        schools_by_city = list(map(lambda x:build_school_map(x, distance=distance, filters=filters), cities))
        facets = [{"query": build_query(x, q, filters), "facet": x} for x in set(join_aggregates(schools_by_city))]

        return render_template(
            "search.html",
            form=form,
            cities=schools_by_city,
            facets=facets,
            q=q,
            filters=filters,
        )
        
    return render_template(
            "search.html",
            form=form,
        )

if __name__ == "__main__":
    app.run()
