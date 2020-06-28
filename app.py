from flask import Flask, render_template, redirect, request, url_for, flash, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime


app = Flask(__name__)
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///city.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "EveRgwapoloveKarla20147105"

"""#*****open weather api with api key****"""
url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=f9c5ec17990ab247371851c53eeff528" 
unsplash_url = "https://api.unsplash.com/search/photos/?client_id=B8zkxFtJVFk_MWFW6PbTx9DD1JBZrcoxFd33FzHysUo&query={}-city"

cached_resp = []

class City(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	city = db.Column(db.String(30), nullable = False, unique = True)

	def __init__(self, city):
		self.city = city.capitalize()

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	@classmethod
	def check_by_name(cls,name):
		city = cls.query.filter_by(city=name).all()
		return city


@app.route('/cities')
def all_cities():
	cities = [{"name": city.city} for city in City.query.all()]
	return render_template("cities.html", cities = cities)

@app.route('/')
def home():
	global cached_resp
	cities = City.query.all()
	if not len(cached_resp) == len(cities):
		response = []
		for city in cities:
			r = requests.get(url.format(city.city)).json()
			image = requests.get(unsplash_url.format(city.city)).json()
			data = {
				"name" : r["name"],
				"main" : r["weather"][0]["main"],
				"description" : r["weather"][0]["description"],
				"icon" : r["weather"][0]["icon"],
				"temp" : r["main"]["temp"],
				"date" : datetime.utcnow(),
				"image" : image["results"][0]["urls"]["small"]
				}
			response.append(data)
		print("data from db")
		cached_resp = response
		return render_template("weather.html", response = response)
	else:
		print("data from cached")
		return render_template('weather.html', response = cached_resp)

@app.route('/add', methods = ['POST'])
def add():
	res = request.get_json()
	print(res["name"].capitalize())
	name = res["name"].capitalize()
	city = requests.get(url.format(name.capitalize())).json()
	if city["cod"] == 200:
		new_city = City.check_by_name(name.capitalize())
		if not new_city:
			new_city = City(name.capitalize())
			new_city.save_to_db()
			r = requests.get(url.format(name)).json()
			image = requests.get(unsplash_url.format(name)).json()
			data = {
				"name" : r["name"],
				"main" : r["weather"][0]["main"],
				"description" : r["weather"][0]["description"],
				"icon" : r["weather"][0]["icon"],
				"temp" : r["main"]["temp"],
				"date" : datetime.utcnow(),
				"image" : image["results"][0]["urls"]["small"]
				}
			res = make_response(jsonify(data),200)
			return res
		else:
			flash("City already existed", category = "danger")
			return redirect(url_for("home"))
	else: 
		flash("Invalid City name, Please try another one.", category = "warning")
		return redirect(url_for("home"))


if __name__ =="__main__":
	app.run(debug=True)