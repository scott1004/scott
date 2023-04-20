from extensions import db
import datetime


class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    booking_service_itemid = db.Column(db.String(50), nullable=False)
    booking_service = db.Column(db.String(150), nullable=False)
    booking_datetime = db.Column(db.DateTime, nullable=False)

    is_canceled = db.Column(db.Boolean(), server_default='0')
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __init__(self, user_id, booking_service_itemid, booking_service, booking_datetime, name, phone):
        self.user_id = user_id
        self.booking_service_itemid = booking_service_itemid
        self.booking_service = booking_service
        self.booking_datetime = booking_datetime
        self.name = name
        self.phone = phone