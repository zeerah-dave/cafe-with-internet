from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model
import random as rd
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

#--------------------------- CONNECT TO DATABASE ------------------------------#
database_users = SqliteDatabase('cafes.db')

''' Model definitions -- the standard "pattern" is to define a base model class that specifies which database to use.  then, any subclasses will automaticallyuse the correct storage'''
class BaseModel(Model):
    class Meta:
        database = database_users
# The user model specifies its fields (or columns) declaratively, like django
class Cafe(BaseModel):
    id = PrimaryKeyField(unique=True, null=False)
    name = CharField()
    map_url = CharField()
    img_url = CharField()
    location = CharField()
    has_sockets = CharField()
    has_toilet = CharField()
    has_wifi = CharField()
    can_take_calls = CharField()
    seats = CharField()
    coffee_price = CharField()


@app.route('/')
def home():
    return render_template('index.html')


## HTTP POST - Create Record
#------------------------Post New Cafe Data---------------------------#
@app.route("/add", methods=['POST'])
def add():
    # Form data is from POSTMAN - Body
    # To get new locations(https://laptopfriendly.co/suggest)
    query = Cafe(name=request.form.get("name"),
    map_url=request.form.get("map_url"),
    img_url=request.form.get("img_url"),
    location=request.form.get("loc"),
    has_sockets=bool(int(request.form.get("sockets"))),
    has_toilet=bool(int(request.form.get("toilet"))),
    has_wifi=bool(int(request.form.get("wifi"))),
    can_take_calls=bool(int(request.form.get("calls"))),
    seats=request.form.get("seats"),
    coffee_price=request.form.get("coffee_price"))

    query.save()  # save() returns the number of rows modified.
    return jsonify(response={"success":" Successfully added the new cafe"})

@app.route('/cafes')
def cafes():
    query = Cafe.select()
    return render_template('cafes.html', query=query)


# HTTP GET - Read Record
#------------------------Prints a random cafe---------------------------#
@app.route("/random")
def random():
    names_of_cafes = []
    query = Cafe.select()
    for cafe in query:
        names_of_cafes.append(cafe.name)

    random_cafe = rd.choice(names_of_cafes)

    query_rand = Cafe.select().where(Cafe.name == random_cafe).get()
    json_data = json.dumps(model_to_dict(query_rand))
    json_dict = json.loads(json_data)
    # Object into a JSON - Serialization (Only appliable for SQLAlchemy)
    return jsonify(json_dict)


#------------------------Prints all cafes---------------------------#
@app.route("/all")
def all():
    all = []
    query = Cafe.select().dicts()
    for row in query:
        all.append(row)
    return jsonify(all)


#------------------------Search cafe by location------------------------#
@app.route("/search")
def search():
    # Takes the argument "?loc="
    query_location = request.args.get("loc")
    all = []
    if Cafe.select().dicts().where(Cafe.location == query_location):
        query = Cafe.select().dicts().where(Cafe.location == query_location)
        for row in query:
            all.append(row)
        return jsonify(all)
    else:
        return jsonify(error={"Not Found":" Sorry, we don't have a cafe at that position"})


#------------------------Patch Coffee Price by ID------------------------#
@app.route("/patch", methods=['PATCH'])
def patch():
    '''Patch - Update a single part of an entry
    Put - Update entire entry'''
    try:
        query = Cafe.update({Cafe.coffee_price:request.form.get('new_price')}).where(Cafe.id == request.args.get('id'))
        query.execute()
        ## Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    except:
        return jsonify(error={"error":"Sorry, no such id exists"})


#------------------------Delete cafe by name------------------------#
@app.route("/delete", methods=['DELETE'])
def delete():
    api_key = "TopSecretAPIKey"
    query_id = request.args.get("id")
    api_key_auth = request.args.get("api-key")
    if api_key == api_key_auth:
        try:
            query = Cafe.get(Cafe.id == query_id)
            query.delete_instance()
            return jsonify(response={"success":"Successfully deleted the entry."})
        except:
            return jsonify(error={"error":"Sorry, no such id exists"})
    else:
        return jsonify(error={"error":"Sorry, that's not allowed. Make sure you have the correct api_key"})


if __name__ == '__main__':
    app.run(debug=True)
