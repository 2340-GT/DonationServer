from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from fuzzywuzzy import process

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/donation.db'
api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

# MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_role = db.Column(db.Integer, nullable=False)
    location_id = db.Column(db.Integer)
    status = db.Column(db.Integer)

    def __init__(self, username, email, password, user_role, location_id=None):
        self.username = username
        self.email = email
        self.password = password
        self.user_role = user_role
        self.location_id = location_id
        self.status = 1

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(80))
    city = db.Column(db.String(120))
    state = db.Column(db.String(10))
    type = db.Column(db.String(80))
    website = db.Column(db.String(120))
    zip = db.Column(db.String(80))
    address = db.Column(db.String(300), nullable=False)

    def __init__(self, name, latitude, longitude, address, phone=None, city=None, state=None, type=None, website=None, zip=None, users=None, items=None):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.phone = phone
        self.city = city
        self.state = state
        self.type = type
        self.website = website
        self.zip = zip
        self.address = address

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    location_id = db.Column(db.Integer)
    longDescribtion = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime)
    value = db.Column(db.Float)

    def __init__(self, category, description, location_id, longDescribtion=None, timestamp=None, value=None):
        self.category = category
        self.description = description
        self.location_id = location_id
        self.longDescribtion = longDescribtion
        self.timestamp = timestamp
        self.value = value

#SCHEMAS
class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
class LocationSchema(ma.ModelSchema):
    class Meta:
        model = Location
class ItemSchema(ma.ModelSchema):
    class Meta:
        model = Item

#RESOURCES
class UsersResource(Resource):
    def get(self):
        result = UserSchema(many = True).dump(User.query.all())
        return jsonify({"record": result.data, "status": 200})
    def post(self):
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"message" : "Data inputted is not valid or does not exist", "status": 400})
        data, errors = UserSchema().load(raw_data)
        if errors:
            return jsonify({"message" :errors, "status" : 400})
        username = data.username
        email = data.email
        password = data.password
        user_role = data.user_role
        location_id = data.location_id
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return jsonify({"message": "A user with this username has already existed, please try another", "status": 400})
        new_user = User(username, email, password, user_role, location_id)
        db.session.add(new_user)
        db.session.commit()
        result = UserSchema().dump(User.query.get(new_user.id))
        return jsonify({"record": result.data, "status": 200})
    def delete(self):
        try:
            result = db.session.query(User).delete()
            db.session.commit()
            return jsonify({"count": result, "status": 200})
        except:
            db.session.rollback()
            return jsonify({"message": "An error has occured, all changes have been reverted", "status": 400})

class UserResource(Resource):
    def get(self, username):
        result = User.query.filter_by(username=username).first()
        if result is None:
            return jsonify({"message" : "No such user", "status": 400})
        result = UserSchema().dump(result)
        return jsonify({"record": result.data, "status": 200})
    def put(self, username):
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"message" : "Data inputted is not valid or does not exist", "status": 400})
        User.query.filter_by(username=username).update(dict(status=raw_data["status"]))
        db.session.commit()
        return jsonify({"message": f"User {username} has been updated", "status": 200})

    def delete(self, username):
        try:
            result = UserSchema.dump(User.query.filter_by(username=username))
            if result is None:
                return jsonify({"message" : "There is no such user", "status": 400})
            db.session.delete(result)
            db.session.commit()
            return jsonify({"count": result, "status": 200})
        except:
            db.session.rollback()
            return jsonify({"message": "An error has occured, all changes have been reverted", "status": 400})

class UserLogInResource(Resource):
    def get(self, username, password):
        result = User.query.filter_by(username=username, password=password).first()
        if result is None:
            return jsonify({"message" : "Wrong validation information", "status": 400})
        result = UserSchema().dump(result)
        if result.data["status"] == 0:
            return jsonify({"message" : f"User {username} currently locked out", "status": 403})
        return jsonify({"record": result.data, "status": 200})

class ItemsResource(Resource):
    def get(self):
        result = ItemSchema(many = True).dump(Item.query.all())
        return jsonify({"record": result.data, "status": 200})
    def post(self):
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"message" : "Data inputted is not valid or does not exist", "status": 400})
        data, errors = ItemSchema().load(raw_data)
        if errors:
            return jsonify({"message" :errors, "status" : 400})
        category = data.category
        description = data.description
        location_id = data.location_id
        longDescribtion = data.longDescribtion
        timestamp = data.timestamp
        value = data.value
        new_item = Item(category, description, location_id, longDescribtion, timestamp, value)
        db.session.add(new_item)
        db.session.commit()
        result = ItemSchema().dump(Item.query.get(new_item.id))
        return jsonify({"record": result.data, "status": 200})
    def delete(self):
        try:
            result = db.session.query(Item).delete()
            db.session.commit()
            return jsonify({"count": result, "status": 200})
        except:
            db.session.rollback()
            return jsonify({"message": "An error has occured, all changes have been reverted", "status": 400})

class ItemResource(Resource):
    def get(self, name):
        choices = ItemSchema(many = True).dump(Item.query.with_entities(Item.description).all())
        choices = [name["description"] for items in choices for name in items]
        results = process.extractBests(name, choices, score_cutoff=60)
        results = set(name for name, score in results)
        result = [ItemSchema(many=True).dump(Item.query.filter_by(description=name).all()).data for name in results]
        return jsonify({"record": result, "status": 200})

class LocationItemResource(Resource):
    def get(self, location_id):
        result = ItemSchema(many=True).dump(Item.query.filter_by(location_id=location_id).all())
        return jsonify({"record": result.data, "status": 200})

class CategoryItemResource(Resource):
    def get(self, category):
        result = ItemSchema(many=True).dump(Item.query.filter_by(category=category).all())
        return jsonify({"result": result.data, "status": 200})

class LocationsResource(Resource):
    def get(self):
        result = LocationSchema(many = True).dump(Location.query.all())
        return jsonify({"status": 200, "results": result.data})
    def post(self):
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"message" : "Data inputted is not valid or does not exist", "status": 400})
        data, errors = LocationSchema().load(raw_data)
        if errors:
            return jsonify({"message" :errors, "status" : 400})
        name = data.name
        latitude = data.latitude
        longitude = data.longitude
        phone = data.phone
        city = data.city
        state = data.state
        type = data.type
        website = data.website
        zip = data.zip
        address = data.address
        location = Location.query.filter_by(name=name).first()
        if location is not None:
            return jsonify({"message": "A location with this name has already existed, please try another", "status": 400})
        new_location = Location(name, latitude, longitude, address, phone, city, state, type, website, zip)
        db.session.add(new_location)
        db.session.commit()
        result = LocationSchema().dump(Location.query.get(new_location.id))
        return jsonify({"record": result.data, "status": 200})
    def delete(self):
        try:
            result = db.session.query(Location).delete()
            db.session.commit()
            return jsonify({"count": result, "status": 200})
        except:
            db.session.rollback()
            return jsonify({"message": "An error has occured, all changes have been reverted", "status": 400})

class RecoverPasswordResource(Resource):
    def sendMessage(service, email, message):
        return
    def get(username, email):
        result = User.query.filter_by(username=username, email=email).first()
        if result is None:
            return jsonify({"message" : "Wrong validation information", "status": 400})
        password = UserSchema().dump(result).password
        sendMessage(service,email, f"Your password is {password}")
        return


#ENDPOINTS
api.add_resource(UsersResource, '/user')
api.add_resource(UserResource, '/user/<username>')
api.add_resource(UserLogInResource,'/user/<username>/<password>')
api.add_resource(ItemsResource, '/item')
api.add_resource(ItemResource, '/item/name/<name>')
api.add_resource(CategoryItemResource, '/item/category/<category>')
api.add_resource(LocationItemResource, '/item/location/<location_id>')
api.add_resource(LocationsResource, '/location')
api.add_resource(RecoverPasswordResource, '/recover/<username>/<email>')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)