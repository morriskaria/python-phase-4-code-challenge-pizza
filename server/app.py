#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

#home route 
@app.route("/")
def index():
    return "<h1>Welcome to Code Challenge</h1>"

#GET/restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_data = [restaurant.to_dict() for restaurant in restaurants]
    return jsonify(restaurants_data), 200
#GET restaurants by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    
    # Get restaurant pizzas with their details
    restaurant_pizzas = []
    for rest in restaurant.restaurant_pizzas:
        restaurant_pizzas.append({
            "id": rest.id,
            "pizza_id": rest.pizza_id,
            "restaurant_id": rest.restaurant_id,
            "price": rest.price,
            "pizza": {
                "id": rest.pizza.id,
                "name": rest.pizza.name,
                "ingredients": rest.pizza.ingredients
            }
        })
    
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": restaurant_pizzas,
        "pizzas": [{"id": p.id, "name": p.name, "ingredients": p.ingredients} for p in restaurant.pizzas]
    })
#delete restaurants by ID
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        # Delete associated restaurant_pizzas 
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
    
        return jsonify({"error": "Restaurant is not available "}), 404


#GET pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200
#create new pizza
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    # Check for required fields
    required_fields = ['price', 'pizza_id', 'restaurant_id']
    if not all(field in data for field in required_fields):
        return jsonify({"errors": ["Missing required fields"]}), 400
    
    try:
        price = int(data['price'])
        pizza_id = int(data['pizza_id'])
        restaurant_id = int(data['restaurant_id'])
    except (ValueError, TypeError):
        return jsonify({"errors": ["Invalid data types"]}), 400
    
    # Validate price range
    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400
    
    # Check for  pizza
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    
    if not pizza or not restaurant:
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404
    
    # Create new restaurant_pizza
    restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    
    try:
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        
        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,  
            "restaurant_id": restaurant_pizza.restaurant_id,  
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
        
    



if __name__ == "__main__":
    app.run(port=5555, debug=True)
