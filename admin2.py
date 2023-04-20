from line_bot_api import *
from models.Reservation import Reservation
import datetime
from models.User import User


def list_reservation_even(event):
    reservations = Reservation.query.filter(Reservation.is_canceled.is_(False),
                                            Reservation.booking_datetime > datetime.datetime.now(),
                                            ).order_by(Reservation.booking_datetime.asc()).all()

    bubbles = []
    for reservation in reservations:
        user = User.query.filter_by(id=reservation.user_id).first()

        booked_date_text = datetime.datetime.strftime(reservation.booking_datetime, '%Y-%m-%d %H:%M')
        booked_item_text = reservation.booking_service
        user_name_text = user.display_name

        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='預約資料', weight='bold', size='xl'),
                    BoxComponent(layout='vertical', margin='lg', spacing='sm', contents=[
                        BoxComponent(layout='baseline', spacing='sm', contents=[
                            TextComponent(text='預約日期:', color='#aaaaaa', size='sm', flex=2),
                            TextComponent(text=booked_date_text, wrap=True, color='#666666', size='sm', flex=3),
                        ]),
                        BoxComponent(layout='baseline', spacing='sm', contents=[
                            TextComponent(text='預約項目:', color='#aaaaaa', size='sm', flex=2),
                            TextComponent(text=booked_item_text, wrap=True, color='#666666', size='sm', flex=3),
                        ]),
                        BoxComponent(layout='baseline', spacing='sm', contents=[
                            TextComponent(text='預約者姓名:', color='#aaaaaa', size='sm', flex=2),
                            TextComponent(text=user_name_text, wrap=True, color='#666666', size='sm', flex=3),
                        ]),
                    ]),
                    BoxComponent(layout='vertical', margin='xxl', contents=[
                        ButtonComponent(
                            action=URIAction(uri='https://www.example.com', label='查看詳細'),
                            height='sm',
                            style='link'
                        ),
                        ButtonComponent(
                            action=PostbackAction(label='取消', display_text='取消', data='action=canceled'),
                            height='sm',
                            style='link',
                            color='#DC143C'
                        ),
                    ])
                ]
            )
        )
        bubbles.append(bubble)

    flex_message = FlexSendMessage(alt_text='Booking List', contents={
        "type": "carousel",
        "contents": bubbles
    })
    line_bot_api.reply_message(event.reply_token, flex_message)