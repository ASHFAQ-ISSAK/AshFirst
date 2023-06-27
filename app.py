from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from faker import Faker

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)
fake = Faker()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    orders = db.relationship("Order", backref="user", lazy=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)

    def __init__(self, name, price):
        self.name = name
        self.price = price


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    quantity = db.Column(db.Integer)

    def __init__(self, user_id, item_id, quantity):
        self.user_id = user_id
        self.item_id = item_id
        self.quantity = quantity


# Create the database if it does not exist
with app.app_context():
    db.create_all()

    # Generate and save fake data...


# User resource
class UserResource(Resource):
    def get(self):
        users = User.query.all()
        results = []
        for user in users:
            orders = []
            for order in user.orders:
                item = Item.query.get(order.item_id)
                orders.append(
                    {"item": item.name, "price": item.price, "quantity": order.quantity}
                )
            results.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "orders": orders,
                }
            )
        return results


class UserDetailResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        orders = []
        for order in user.orders:
            item = Item.query.get(order.item_id)
            orders.append(
                {"item": item.name, "price": item.price, "quantity": order.quantity}
            )

        return {"id": user.id, "name": user.name, "email": user.email, "orders": orders}


api.add_resource(UserResource, "/users")
api.add_resource(UserDetailResource, "/users/<int:user_id>")


class ItemResource(Resource):
    def get(self):
        items = Item.query.all()
        results = []
        for item in items:
            results.append({"id": item.id, "name": item.name, "price": item.price})
        return results


class ItemDetailResource(Resource):
    def get(self, item_id):
        item = Item.query.get(item_id)
        if not item:
            return {"error": "Item not found"}, 404

        return {"id": item.id, "name": item.name, "price": item.price}


api.add_resource(ItemResource, "/items")
api.add_resource(ItemDetailResource, "/items/<int:item_id>")


if __name__ == "__main__":
    app.run(debug=True)
