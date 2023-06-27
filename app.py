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

# Create a request parser for UserResource
user_parser = reqparse.RequestParser()
user_parser.add_argument("name", type=str, required=True, help="Name of the user")
user_parser.add_argument("email", type=str, required=True, help="Email of the user")

# Create a request parser for UserDetailResource
detail_parser = reqparse.RequestParser()
detail_parser.add_argument(
    "quantity", type=int, required=True, help="Quantity of the order"
)


# Models
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

    def post(self):
        args = user_parser.parse_args()
        name = args["name"]
        email = args["email"]

        # Create a new user
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully"}, 201


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

    def post(self, user_id):
        args = detail_parser.parse_args()
        quantity = args["quantity"]

        # Create a new order
        order = Order(
            user_id=user_id, item_id=1, quantity=quantity
        )  # Assuming item_id 1 for simplicity
        db.session.add(order)
        db.session.commit()

        return {"message": "Order created successfully"}, 201


api.add_resource(UserResource, "/users")
api.add_resource(UserDetailResource, "/users/<int:user_id>")


if __name__ == "__main__":
    app.run(debug=True)
