from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from faker import Faker

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
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

    # Generate and save fake user data
    for _ in range(10):  # Generate 10 users
        name = fake.name()
        email = fake.email()
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()

        # Generate and save fake order data for the user
        for _ in range(3):  # Generate 3 orders per user
            item_id = fake.random_int(min=1, max=10)  # Assuming 10 items
            quantity = fake.random_int(min=1, max=5)  # Random quantity
            order = Order(user_id=user.id, item_id=item_id, quantity=quantity)
            db.session.add(order)
    db.session.commit()

    # Generate and save fake item data
    for _ in range(10):  # Generate 10 items
        name = fake.word()
        price = fake.pyfloat(min_value=1, max_value=100, right_digits=2)
        item = Item(name=name, price=price)
        db.session.add(item)
    db.session.commit()


@app.route("/users", methods=["GET"])
def get_users():
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
            {"id": user.id, "name": user.name, "email": user.email, "orders": orders}
        )
    return jsonify(results)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    print(f"User: {user.name}, {user.email}")
    print("Orders:")
    for order in user.orders:
        print(
            f"Item: {order.item.name}, Price: {order.item.price}, Quantity: {order.quantity}"
        )

    orders = []
    for order in user.orders:
        item = Item.query.get(order.item_id)
        orders.append(
            {"item": item.name, "price": item.price, "quantity": order.quantity}
        )

    return jsonify(
        {"id": user.id, "name": user.name, "email": user.email, "orders": orders}
    )


@app.route("/items", methods=["GET"])
def get_items():
    items = Item.query.all()
    results = []
    for item in items:
        results.append({"id": item.id, "name": item.name, "price": item.price})
    return jsonify(results)


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({"id": item.id, "name": item.name, "price": item.price})


@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")

    if not name or not price:
        return jsonify({"error": "Invalid data"}), 400

    item = Item(name=name, price=price)
    db.session.add(item)
    db.session.commit()

    return jsonify({"message": "Item created successfully", "id": item.id}), 201


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    name = data.get("name")
    price = data.get("price")

    if not name or not price:
        return jsonify({"error": "Invalid data"}), 400

    item.name = name
    item.price = price
    db.session.commit()

    return jsonify({"message": "Item updated successfully", "id": item.id})


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item deleted successfully"})


if __name__ == "__main__":
    app.run(debug=True)
