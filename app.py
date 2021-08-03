from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from schools import schools, cities

app = Flask(__name__)
app.secret_key = 'the random string'

def get_min_max(val: float, interval: float=0.5) -> tuple:
    _min = val - interval
    _max = val + interval
    return [_min, _max]

class SchoolRequest(FlaskForm):
    query = StringField('name', validators=[DataRequired()])

@app.route('/')
def index():
    return render_template('index.html', form=SchoolRequest())

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SchoolRequest()

    if request.method == "POST":
        search_city, search_state = form.query.data.split(', ')
        result = cities[(cities['city'] == search_city) & (cities['state'] ==
            search_state)].to_dict(orient='records')[0]
        
        city_lat = get_min_max(round(result['latitude'], 3))
        city_long = get_min_max(round(result['longitude'], 3))

        school_list = schools[(schools['LATITUDE'].between(city_lat[0], city_lat[1])) & \
                (schools['LONGITUDE'].between(city_long[0],
                    city_long[1]))].to_dict(orient='records')

        return render_template('search.html', form=form, result=school_list)

    return render_template('search.html', form=form)

if __name__ == "__main__":
    app.run()
