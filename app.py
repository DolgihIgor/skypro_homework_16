import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import raw_data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
        }


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(50))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'address': self.address,
            'price': self.price,
            'customer_id': self.customer_id,
            'executor_id': self.executor_id,
        }


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'executor_id': self.order_id,
        }

with app.app_context():
    db.create_all()


def main():
    with app.app_context():
        db.create_all()
        insert_data()


def insert_data():
    new_users = []
    for user in raw_data.users:
        new_users.append(
            User(
                id = user['id'],
                first_name = user['first_name'],
                last_name = user['last_name'],
                age = user['age'],
                email = user['email'],
                role = user['role'],
                phone = user['phone'],
            )
        )

        with db.session.begin():
            db.session.add_all(new_users)

    new_orders = []
    for order in raw_data.orders:
        new_orders.append(
            Order(
                id = order['id'],
                name = order['name'],
                description = order['description'],
                # Преобразуем дату из строки вида 12/20/2023 в дату
                start_date = datetime.strptime(order['start_date'], "%m/%d/%Y"),
                end_date = datetime.strptime(order['end_date'], "%m/%d/%Y"),
                address = order['address'],
                price = order['price'],
                customer_id = order['customer_id'],
                executor_id = order['executor_id'],
            )
        )
        with db.session.begin():
            db.session.add_all(new_orders)

    new_offers = []
    for offer in raw_data.offers:
        new_offers.append(
            Offer(
                id = offer['id'],
                order_id = offer['order_id'],
                executor_id = offer['executor_id'],
            )
        )
        with db.session.begin():
            db.session.add_all(new_offers)


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        res = []
        for user in User.query.all():
            res.append(user.to_dict())
        return jsonify(res)
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        new_user = User(
                id=user_data['id'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                age=user_data['age'],
                email=user_data['email'],
                role=user_data['role'],
                phone=user_data['phone'],
            )

        db.session.add(new_user)
        db.session.commit()
        return '', 201


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    if request.method == 'GET':
        u = User.query.get(uid)
        return json.dumps(u.to_dict())
    elif request.method == 'DELETE':
        u = User.query.get(uid)
        db.session.delete(u)

        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        u = User.query.get(uid)
        u.first_name = user_data["first_name"]
        u.last_name = user_data["last_name"]
        u.age = user_data["age"]
        u.email = user_data["email"]
        u.role = user_data["role"]
        u.phone = user_data["phone"]

        db.session.add(u)
        db.session.commit()
        return "", 204

@app.route('/orders', methods = ['GET', 'POST'])
def orders():
    if request.method == 'GET':
        res = []
        for order in Order.query.all():
            res.append(order.to_dict())
        return jsonify(res)
    if request.method == 'POST':
        order_data = json.loads(request.data)
        new_order = Order(
            name = order_data['name'],
            description = order_data['description'],
            start_date = datetime.strptime(order_data['start_date'], "%m/%d/%Y"),
            end_date = datetime.strptime(order_data['end_date'], "%m/%d/%Y"),
            address = order_data['address'],
            price = order_data['price'],
            customer_id = order_data['customer_id'],
            executor_id = order_data['executor_id'],
        )

        db.session.add(new_order)
        db.session.commit()

        return '', 204

@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid: int):
    if request.method == 'GET':
        o = Order.query.get(oid)
        return o.to_dict()
    elif request.method == 'DELETE':
        o = Order.query.get(oid)
        db.session.delete(o)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        u = Order.query.get(oid)
        u.name = order_data['order_data']
        u.description = order_data['order_data']
        u.start_date = datetime.strptime(order_data['start_date'], "%m/%d/%Y")
        u.end_date = datetime.strptime(order_data['end_date'], "%m/%d/%Y")
        u.address = order_data['order_data']
        u.price = order_data['order_data']
        u.customer_id = order_data['order_data']
        u.executor_id = order_data['order_data']

        db.session.add(u)
        db.session.commit()
        return '', 204


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == "GET":
        res = []
        for u in Offer.query.all():
            res.append(u.to_dict())
        return json.dumps(res), 200
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        new_offer = Offer(
            id=offer_data['id'],
            order_id=offer_data['order_id'],
            executor_id=offer_data['executor_id'],
        )
        db.session.add(new_offer)
        db.session.commit()
        return '', 201


@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid: int):
    if request.method == 'GET':
        return json.dumps(Offer.query.get(oid).to_dict())
    elif request.method == 'DELETE':
        u = Offer.query.get(oid)
        db.session.delete(u)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        u = Offer.query.get(oid)
        u.order_id = order_data['order_id']
        u.executor_id = order_data['executor_id']

        db.session.add(u)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    main()
    app.run(debug=True)