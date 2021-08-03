from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from schools import schools, cities

app = Flask(__name__)
app.secret_key = 'the random string'

class SchoolRequest(FlaskForm):
    query = StringField('name', validators=[DataRequired()])

@app.route('/')
def index():
    return render_template('index.html', form=SchoolRequest())

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SchoolRequest()

    if request.method == "POST":
        city = cities[cities['city'] == form.query.data].values
        school_list = schools
        return render_template('search.html', form=form, body=city)

    return render_template('search.html', form=form)

if __name__ == "__main__":
    app.run()
