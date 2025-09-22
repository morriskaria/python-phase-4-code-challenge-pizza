from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship(
        'RestaurantPizza', 
        back_populates='restaurant', 
        cascade='all, delete-orphan'
    )

    pizzas = association_proxy('restaurant_pizzas', 'pizza')
    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'pizzas': [rp.pizza.to_dict() for rp in self.restaurant_pizzas]
        }
    
    def to_dict_basic(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza',back_populates='pizza')

    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'restaurants': [rp.restaurant.to_dict_basic() for rp in self.restaurant_pizzas]
        }
    
    def to_dict_basic(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    
    # add relationships

    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    

    # add serialization rules
    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza': self.pizza.to_dict_basic(),
            'restaurant': self.restaurant.to_dict_basic()
        }
    
    def to_dict_basic(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id
        }
    # add validation
    @validates('price')
    def validate_price(self ,key,price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price





    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"