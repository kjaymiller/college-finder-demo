"""Main Flask Runner for demo."""
import os

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from more_itertools import first_true
from wtforms import StringField
from wtforms.validators import DataRequired

from city_search import get_cities_by_name, get_schools
from connection import local_client as client

app = Flask(__name__)
app.secret_key = os.urandom(24)


class SchoolRequest(FlaskForm):
    """Search Bar on every page of project"""

    query = StringField("name", validators=[DataRequired()])


@app.route("/")
def index():
    """Homepage"""

    return render_template(
        "index.html",
        school_form=SchoolRequest(),
    )


@app.route("/school/<school_id>")
def get_school(school_id):
    """Retrieves a Single Entry in Elasticsearch based on document id"""
    school = client.get(index="schools", id=school_id)
    form = SchoolRequest()

    return render_template("school.html", school=school, form=form)


@app.route("/search/schools", methods=["GET", "POST"])
def school_search():
    """Use the `SchoolRequest` object to search for documents"""
    form = SchoolRequest()

    query = request.args.get("q", form.query.data)
    city = request.args.get("city", None)
    tags = request.args.get("tags", [])
    states = request.args.get("states", [])
    location = request.args.get("location", "")
    cities = []

    if tags:
        tags = tags.split(",")

    if states:
        states = states.split(",")

    if city:
        city_from_list = first_true(
            get_cities_by_name(city), pred=lambda x: str(x) == city
        )

        location = city_from_list.location

    if location:
        response = get_schools(
            query=query,
            tags=tags,
            states=states,
            location=location,
        )

    else:
        cities = get_cities_by_name(query)
        response = get_schools(
            query=query,
            tags=tags,
            states=states,
        )

    if not response["hits"]["total"]["value"]:

        if city:

            response = get_schools(
                query=city_from_list,
                tags=tags,
                states=states,
            )

    return render_template(
        "school_search.html",
        results=response,
        query=query,
        school_form=form,
        cities=cities,
        location=location,
    )


if __name__ == "__main__":
    app.run()
