import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from raw_data import users, orders, offers
from datetime import datetime


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


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

with app.app_context():
    db.create_all()


def main():
    with app.app_context():
        db.create_all()
        insert_data()


def insert_data():
    new_users = []
    for user in users:
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
    for order in orders:
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
    for offer in offers:
        new_offers.append(
            Offer(
                id = offer['id'],
                order_id = offer['order_id'],
                executor_id = offer['executor_id'],
            )
        )
        with db.session.begin():
            db.session.add_all(new_offers)


if __name__ == '__main__':
    main()