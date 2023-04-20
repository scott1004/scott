from line_bot_api import *
from urllib.parse import parse_qsl, urlencode
import datetime
from extensions import db
from models.User import User
from models.Reservation import Reservation
from sqlalchemy import extract, and_

WAITING_FOR_NAME = 'waiting_for_name'
WAITING_FOR_CONFIRM = 'waiting_for_confirm'
WAITING_FOR_PHONE = 'WAITING_FOR_PHONE'
WAITING_FOR_PHONE_CONFIRM = 'WAITING_FOR_PHONE_CONFIRM'

user_state = {}

services = {
    1: {
        'itemid': '1',
        'img_url': 'https://media.istockphoto.com/id/952772504/photo/beautician-doing-permanent-eyebrows-makeup-tattoo-on-woman-face.jpg?s=1024x1024&w=is&k=20&c=f725ttfMzxz436pM733LW1v42znB5w0-XyoVxjpzZe4=',
        'title': '一般霧眉',
        'post_url': 'https://linecorp.com'
    },
    2: {
        'itemid': '2',
        'img_url': 'https://media.istockphoto.com/id/952772504/photo/beautician-doing-permanent-eyebrows-makeup-tattoo-on-woman-face.jpg?s=1024x1024&w=is&k=20&c=f725ttfMzxz436pM733LW1v42znB5w0-XyoVxjpzZe4=',
        'title': '補色服務',
        'post_url': 'https://linecorp.com'
    },
}


def service_category_event(event):
    image_carousel_template_message = TemplateSendMessage(
        alt_text='ImageCarousel template',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url='https://media.istockphoto.com/id/952772504/photo/beautician-doing-permanent-eyebrows-makeup-tattoo-on-woman-face.jpg?s=1024x1024&w=is&k=20&c=f725ttfMzxz436pM733LW1v42znB5w0-XyoVxjpzZe4=',
                    action=PostbackAction(
                        label='霧眉服務',
                        display_text='霧眉服務',
                        data='action=buy&itemid=1'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://media.istockphoto.com/id/1457048408/photo/cosmetologist-put-white-mask-at-female-face.jpg?s=1024x1024&w=is&k=20&c=-1rcZkRS9WVzluPHAq092PhNpKWbA-xV-D0BvkX7bZI=',
                    action=PostbackAction(
                        label='補色服務',
                        display_text='補色服務',
                        data='action=buy&itemid=2'
                    )
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, image_carousel_template_message)


def service_event(event):
    data = dict(parse_qsl(event.postback.data))
    bubbles = []
    bubble = None  # Initialize the variable outside the for loop
    for service_id in services:
        if services[service_id]['itemid'] == data['itemid']:
            service = services[service_id]
            bubble = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": service['img_url'],
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": service['title'],
                            "wrap": True,
                            "weight": "bold",
                            "size": "xl"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "$5800",
                                    "wrap": True,
                                    "weight": "bold",
                                    "size": "xl",
                                    "flex": 0
                                },
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "postback",
                                "label": service['title'],
                                "data": f"action=select_date&service_id={service_id}"
                            }
                        },
                    ]
                }
            }
            break  # Exit the loop when the condition is met
    if bubble is not None:  # Check if the variable is defined
        bubbles.append(bubble)
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "carousel",
                "contents": bubbles
            }
        )
        line_bot_api.reply_message(
            event.reply_token,
            [flex_message]
        )
    else:
        # Handle the case where no service matches the provided item ID
        pass


def service_select_event(event):
    user = User.query.filter(User.line_id == event.source.user_id).first()
    if booked(event, user):
        return
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')
    quick_reply_buttons = []
    today = datetime.datetime.today().date()
    book_time = ['2023-04-10', '2023-04-15', '2023-04-20', '2023-04-23', '2023-04-28']
    for x in range(1, 14):
        day = today + datetime.timedelta(days=x)
        quick_reply_button = QuickReplyButton(
            action=PostbackAction(label=f'{day}',
                                  text=f'我想預約 {day}',
                                  data=f'action=select_time&service_id={data["service_id"]}&date={day}')
        )
        quick_reply_buttons.append(quick_reply_button)

    text_message = TextSendMessage(text='請問要預約哪個日期?',
                                   quick_reply=QuickReply(items=quick_reply_buttons))

    line_bot_api.reply_message(
        event.reply_token,
        [text_message]
    )


def service_select_time_event(event):
    data = dict(parse_qsl(event.postback.data))
    quick_reply_buttons = []
    book_time = ['09:00', '11:00', '13:00', '15:00', '17:00']
    for time in book_time:
        quick_reply_button = QuickReplyButton(action=PostbackAction(label=time,
                                                                    text=f'{time} this time',
                                                                    data=f'action=confirm&service_id={data["service_id"]}&date={data["date"]}&time={time}'))
        quick_reply_buttons.append(quick_reply_button)
    text_message = TextSendMessage(text='請問要預約哪個時段?',
                                   quick_reply=QuickReply(items=quick_reply_buttons))
    line_bot_api.reply_message(
        event.reply_token,
        [text_message]
    )


def confirm_event(event):
    data = dict(parse_qsl(event.postback.data))
    booking_service = services[int(data['service_id'])]
    confirm_template_message = TemplateSendMessage(
        alt_text='Confirm template',
        template=ConfirmTemplate(
            text=f'請確認預約資訊是否正確?\n\n{booking_service["title"]}\n姓名: {data["name"]}'
                 f'\n電話: {data["phone"]}\n預約日期及時間: {data["date"]} {data["time"]}',
            actions=[
                PostbackAction(
                    label='正確',
                    display_text='正確',
                    data=f'action=confirmed&service_id={data["service_id"]}&date={data["date"]}&time={data["time"]}&name={data["name"]}&phone={data["phone"]}'
                ),
                MessageAction(
                    label='取消',
                    text='cancel'
                )
            ]
        )
    )
    line_bot_api.reply_message(
        event.reply_token,
        [confirm_template_message]
    )


def service_confirmed_event(event):
    data = dict(parse_qsl(event.postback.data))

    booking_service = services[int(data['service_id'])]
    booking_datetime = datetime.datetime.strptime(f'{data["date"]} {data["time"]}', '%Y-%m-%d %H:%M')
    name = data["name"]
    phone = data["phone"]
    print(booking_datetime)

    user = User.query.filter(User.line_id == event.source.user_id).first()

    reservation = Reservation(
        user_id=user.id,
        booking_service_itemid=f'{booking_service["itemid"]}',
        booking_service=f'{booking_service["title"]}',
        booking_datetime=booking_datetime,
        name=name,
        phone=phone
    )
    if booked(event, user):
        return
    db.session.add(reservation)
    db.session.commit()

    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text='預約請匯款訂金至 合庫:006 帳號:0330765394040 才算完成預約喔!')]
    )


def booked(event, user):
    reservation = Reservation.query.filter(Reservation.user_id == user.id,
                                           Reservation.is_canceled.is_(False),
                                           Reservation.booking_datetime > datetime.datetime.now()).first()
    if reservation:
        buttons_template_message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='您已預約服務，如需更改請取消預約，謝謝！',
                text=f'{reservation.booking_service}\n預約時間及日期: {reservation.booking_datetime}',
                actions=[
                    PostbackAction(
                        label='取消',
                        display_text='取消',
                        data='action=canceled'
                    )
                ]
            )
        )

        line_bot_api.reply_message(
            event.reply_token,
            [buttons_template_message])

        return True
    else:
        return False


def service_canceled_event(event):
    user = User.query.filter(User.line_id == event.source.user_id).first()
    reservation = Reservation.query.filter(Reservation.user_id == user.id,
                                           Reservation.is_canceled.is_(False),
                                           Reservation.booking_datetime > datetime.datetime.now()).first()
    if reservation:
        reservation.is_canceled = True

        db.session.add(reservation)
        db.session.commit()

        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text='already canceled')]
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text='no booked yet')]
        )


def service_select_event1(event):
    user = User.query.filter(User.line_id == event.source.user_id).first()
    if booked(event, user):
        return
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')

    datetime_picker_action = DatetimePickerAction(
        label='請選擇日期',
        data=f'action=select_time&service_id={service_id}',
        mode='date',
        max="2023-04-30",
        min="2023-04-01",
    )

    text_message = TextSendMessage(
        text='請選擇日期',
        quick_reply=QuickReply(
            items=[QuickReplyButton(action=datetime_picker_action)]
        )
    )

    line_bot_api.reply_message(
        event.reply_token,
        text_message
    )


def service_select_time_event1(event):
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')
    date_time_str = event.postback.params['date']
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')
    print(date_time_str)
    quick_reply_buttons = []
    book_time = ['09:00', '11:00', '13:00', '15:00', '17:00']
    for time in book_time:
        quick_reply_button = QuickReplyButton(
            action=PostbackAction(
                label=time,
                text=f'{time} this time',
                data=f'action=confirm&service_id={service_id}&date={date_time_obj.date()}&time={time}'
            )
        )
        quick_reply_buttons.append(quick_reply_button)

    text_message = TextSendMessage(
        text='請問要預約哪個時段?',
        quick_reply=QuickReply(
            items=quick_reply_buttons
        )
    )

    line_bot_api.reply_message(
        event.reply_token,
        text_message
    )


def service_select_event2(event):
    user = User.query.filter(User.line_id == event.source.user_id).first()
    if booked(event, user):
        return
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')
    quick_reply_buttons = []
    today = datetime.datetime.today().date()
    book_day = ['2023-04-20', '2023-04-21', '2023-04-22', '2023-04-23', '2023-04-28']
    for days in book_day:
        quick_reply_button = QuickReplyButton(
            action=PostbackAction(label=f'{days}',
                                  text=f'我想預約 {days}',
                                  data=f'action=select_time&service_id={data["service_id"]}&date={days}')
        )
        quick_reply_buttons.append(quick_reply_button)

    text_message = TextSendMessage(text='請問要預約哪個日期?',
                                   quick_reply=QuickReply(items=quick_reply_buttons))

    line_bot_api.reply_message(
        event.reply_token,
        [text_message]
    )


def service_select_time_event2(event):
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')
    date_str = data.get('date')
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

    # 以字典形式存儲每個日期對應的可預約時間列表
    available_times = {
        '2023-04-20': ['13:00', '15:00', '17:00'],
        '2023-04-21': ['12:00', '14:00', '16:00', '18:00'],
        '2023-04-22': ['17:00', '19:00'],
        '2023-04-23': ['08:00', '10:00', '16:00'],
        '2023-04-28': ['08:30', '14:30', '16:30'],
    }

    # 從可用時間列表中取出當天可預約的時間
    book_time = available_times.get(date_str)

    if not book_time:
        # 如果當天沒有可預約的時間，提示用戶選擇其他日期
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='當天沒有可預約的時間，請選擇其他日期')
        )
        return

    # 查詢已預約的日期和時間
    reservations = Reservation.query.filter(
        Reservation.booking_service_itemid == service_id,
        extract('year', Reservation.booking_datetime) == date_obj.year,
        extract('month', Reservation.booking_datetime) == date_obj.month,
        extract('day', Reservation.booking_datetime) == date_obj.day,
        Reservation.is_canceled.is_(False)
    ).all()

    # 將已預約的日期和時間從 book_time 中刪除
    for r in reservations:
        if r.booking_datetime.time().strftime('%H:%M') in book_time:
            book_time.remove(r.booking_datetime.time().strftime('%H:%M'))

    quick_reply_buttons = []
    for time in book_time:
        quick_reply_button = QuickReplyButton(
            action=PostbackAction(
                label=time,

                data=f'action=confirm1&service_id={service_id}&date={date_obj}&time={time}'
            )
        )
        quick_reply_buttons.append(quick_reply_button)

    text_message = TextSendMessage(
        text='請問要預約哪個時段?',
        quick_reply=QuickReply(
            items=quick_reply_buttons
        )
    )

    line_bot_api.reply_message(
        event.reply_token,
        text_message
    )


def ask_phone(event):
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')
    date = data.get('date')
    time = data.get('time')
    name = data.get('name')
    user_state[event.source.user_id] = {
        'state': WAITING_FOR_PHONE,
        'service_id': service_id,
        'date': date,
        'time': time,
        'name': name,
    }
    message_template = TextSendMessage(
        text='請輸入您的電話'
    )
    line_bot_api.reply_message(event.reply_token, message_template)


def ask_name(event):
    data = dict(parse_qsl(event.postback.data))
    service_id = data.get('service_id')
    date = data.get('date')
    time = data.get('time')
    user_state[event.source.user_id] = {
        'state': WAITING_FOR_NAME,
        'service_id': service_id,
        'date': date,
        'time': time
    }
    message_template = TextSendMessage(
        text='請輸入您的姓名'
    )
    line_bot_api.reply_message(event.reply_token, message_template)


def handle_name_input(event):
    user_state[event.source.user_id]['state'] = WAITING_FOR_CONFIRM
    name = event.message.text
    service_id = user_state[event.source.user_id]['service_id']
    date = user_state[event.source.user_id]['date']
    time = user_state[event.source.user_id]['time']
    message_template = TemplateSendMessage(
        alt_text='確認姓名',
        template=ButtonsTemplate(
            title='確認姓名',
            text=f'您的姓名是 {name} 嗎？',
            actions=[
                PostbackAction(
                    label='是',
                    display_text='是',
                    data=f'action=confirm_phone&service_id={service_id}&date={date}&time={time}&name={name}'
                ),
                PostbackAction(
                    label='否',
                    display_text='否',
                    data=f'action=confirm1&service_id={service_id}&date={date}&time={time}'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message_template)


def handle_phone_input(event):
    phone = event.message.text
    if not phone.isdigit() or len(phone) != 10:
        error_message = TextSendMessage(text='請輸入10位數字的手機號碼。')
        line_bot_api.reply_message(event.reply_token, error_message)
        return
    user_state[event.source.user_id]['state'] = WAITING_FOR_PHONE_CONFIRM
    service_id = user_state[event.source.user_id]['service_id']
    date = user_state[event.source.user_id]['date']
    time = user_state[event.source.user_id]['time']
    name = user_state[event.source.user_id]['name']
    message_template = TemplateSendMessage(
        alt_text='確認電話',
        template=ButtonsTemplate(
            title='確認姓名',
            text=f'您的電話是 {phone} 嗎？',
            actions=[
                PostbackAction(
                    label='是',
                    display_text='是',
                    data=f'action=confirm&service_id={service_id}&date={date}&time={time}&name={name}&phone={phone}'
                ),
                PostbackAction(
                    label='否',
                    display_text='否',
                    data=f'action=confirm_phone&service_id={service_id}&date={date}&time={time}&name={name}'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message_template)