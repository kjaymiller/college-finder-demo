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
def search():
    form = SchoolRequest()

    if request.method == "POST":
        cities = get_cities(form.query.data)["hits"]["hits"]
        schools_by_city = list(map(lambda x:build_school_map(x, distance=form.distance.data), cities))
        facets = join_aggregates(schools_by_city)
        render_template("search.html", form=form, cities=schools_by_city, facets=facets)

    return render_template("search.html", form=form)


if __name__ == "__main__":
    app.run()
