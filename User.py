from extensions import db
import datetime
reservation = db.relationship('Reservation', backref='user')


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.String(50), unique=True)
    display_name = db.Column(db.String(255))
    picture_url = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, line_id, display_name, picture_url):
        self.line_id = line_id
        self.display_name = display_name
        self.picture_url = picture_url

    def __repr__(self):
        return f"<User(line_id='{self.line_id}', display_name='{self.display_name}')>"
