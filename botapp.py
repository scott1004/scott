from flask import Flask, request, abort
from events.basic import about_us_event, location_event, other_event
from extensions import db, migrate
from models.User import User
from events.service import *
from line_bot_api import *
from urllib.parse import parse_qsl
from events.admin import *
from events.admin2 import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:scott1004@127.0.0.1:5432/eyebrow'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)
migrate.init_app(app, db)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_text = str(event.message.text).lower()
    user = User.query.filter(User.line_id == event.source.user_id).first()
    if not user:
        profile = line_bot_api.get_profile(event.source.user_id)
        print(profile.display_name)
        print(profile.user_id)
        print(profile.picture_url)
        print(profile.status_message)

        user = User(profile.user_id, profile.display_name, profile.picture_url)
        db.session.add(user)
        db.session.commit()

    if message_text == '@關於':
        about_us_event(event)

    elif message_text == '@地點':
        location_event(event)

    elif message_text == '@預約':
        service_category_event(event)
    # elif message_text == '@測試':

    elif message_text.startswith('*'):
        if event.source.user_id not in ['U4387f4bf9142f9c318cd47bef9e3a06f']:
            return
        if message_text in ['*data', '*d']:
            list_reservation_even(event)
    elif user_state.get(event.source.user_id, {}).get('state') == WAITING_FOR_NAME:  # 如果用戶狀態為等待輸入姓名
        name = event.message.text
        #  將確認指令的按鈕添加到文字輸入訊息的下方
        handle_name_input(event)
    elif user_state.get(event.source.user_id, {}).get('state') == WAITING_FOR_PHONE:  # 如果用戶狀態為等待輸入姓名
        phone = event.message.text
        #  將確認指令的按鈕添加到文字輸入訊息的下方
        handle_phone_input(event)
    '''else:
        other_event(event)'''


@handler.add(FollowEvent)   #加入帳號歡迎訊息
def handle_follow(event):
    welcome_msg = """歡迎加入"""
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg)
    )


@handler.add(UnfollowEvent)
def handle_follow(event):
    print(event)


@handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))
    print(data['action'])
    print(data['itemid'])


@handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))
    if data.get('action') == 'buy':
        service_event(event)
    elif data.get('action') == 'select_date':
        service_select_event2(event)
    elif data.get('action') == 'select_time':
        service_select_time_event2(event)
    elif data.get('action') == 'confirm1':
        ask_name(event)
    elif data.get('action') == 'confirm_phone':
        ask_phone(event)
    elif data.get('action') == 'confirm':
        confirm_event(event)
    elif data.get('action') == 'confirmed':
        service_confirmed_event(event)
    elif data.get('action') == 'canceled':
        service_canceled_event(event)

    print('action:', data.get('action'))
    print('itemid:', data.get('itemid'))
    print('service:', data.get('service_id'))
    print('date:', data.get('date'))
    print('time:', data.get('time'))
    print('service:', data.get('service'))
    print('name:', data.get('name'))
    print('phone:', data.get('phone'))


if __name__ == "__main__":
    app.run()