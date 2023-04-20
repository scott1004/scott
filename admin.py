from line_bot_api import *
from models.Reservation import Reservation
import datetime
from models.User import User


def list_reservation_event(event):
    reservations = Reservation.query.filter(Reservation.is_canceled.is_(False),
                                            Reservation.booking_datetime > datetime.datetime.now(),
                                            ).order_by(Reservation.booking_datetime.asc()).all()
    reservation_data_text = '## book list: ## \n\n'
    for reservation in reservations:
        user = User.query.filter_by(id=reservation.user_id).first()
        reservation_data_text += f'''booked date: {reservation.booking_datetime}
booked item: {reservation.booking_service}
name: {user.display_name}\n'''

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reservation_data_text)
    )