from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50))
    location = db.Column(db.String(100))
    price = db.Column(db.Float)